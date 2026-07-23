"""
Hotel Service — Fetch real hotels near a verified arrival point.

Primary:  OpenStreetMap Overpass API (free, global, no API key needed)
Fallback: Google Places Text Search (only if key is available and working)

Never invents hotel names.
"""
import os
import math
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
OVERPASS_URL          = "https://overpass-api.de/api/interpreter"
GOOGLE_TEXT_SEARCH    = "https://maps.googleapis.com/maps/api/place/textsearch/json"
HEADERS               = {"User-Agent": "SmartTravelPlanner/1.0 (student project)"}

# ── Price ranges per destination category + travel style (INR per night) ─────
PRICE_RANGES: Dict[str, Dict[str, tuple]] = {
    "india_tier2":         {"budget": (500,  1200),  "moderate": (1200, 3500),  "luxury": (3500,  8000)},
    "india_tourist":       {"budget": (600,  1500),  "moderate": (1500, 4500),  "luxury": (4500,  12000)},
    "india_hill":          {"budget": (700,  1800),  "moderate": (1800, 5000),  "luxury": (5000,  15000)},
    "india_metro":         {"budget": (900,  2000),  "moderate": (2000, 6000),  "luxury": (6000,  20000)},
    "india_island":        {"budget": (1200, 3000),  "moderate": (3000, 8000),  "luxury": (8000,  25000)},
    "india_leisure":       {"budget": (600,  1500),  "moderate": (1500, 4000),  "luxury": (4000,  12000)},
    "southeast_asia":      {"budget": (1000, 2500),  "moderate": (2500, 7000),  "luxury": (7000,  20000)},
    "east_asia":           {"budget": (2500, 6000),  "moderate": (6000, 15000), "luxury": (15000, 40000)},
    "east_asia_expensive": {"budget": (3500, 8000),  "moderate": (8000, 20000), "luxury": (20000, 60000)},
    "middle_east":         {"budget": (4000, 9000),  "moderate": (9000, 22000), "luxury": (22000, 70000)},
    "europe_budget":       {"budget": (3000, 7000),  "moderate": (7000, 18000), "luxury": (18000, 50000)},
    "europe_moderate":     {"budget": (4500, 10000), "moderate": (10000,25000), "luxury": (25000, 70000)},
    "europe_expensive":    {"budget": (6000, 14000), "moderate": (14000,35000), "luxury": (35000, 100000)},
    "north_america":       {"budget": (5000, 12000), "moderate": (12000,30000), "luxury": (30000, 90000)},
    "australia":           {"budget": (4500, 10000), "moderate": (10000,25000), "luxury": (25000, 75000)},
    "south_asia":          {"budget": (800,  2000),  "moderate": (2000, 5000),  "luxury": (5000,  15000)},
    "africa":              {"budget": (1500, 4000),  "moderate": (4000, 10000), "luxury": (10000, 30000)},
    "luxury_island":       {"budget": (8000, 18000), "moderate": (18000,40000), "luxury": (40000, 120000)},
    "default":             {"budget": (800,  2000),  "moderate": (2000, 6000),  "luxury": (6000,  18000)},
}

_PRICE_LEVEL_TO_TIER = {0: "budget", 1: "budget", 2: "moderate", 3: "luxury", 4: "luxury"}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def _price_from_category(dest_category: str, travel_style: str, stars: int = 0) -> Dict:
    cat = PRICE_RANGES.get(dest_category, PRICE_RANGES["default"])
    if stars >= 4:
        lo, hi = cat.get("luxury", cat["moderate"])
    elif stars == 3:
        lo, hi = cat.get("moderate", cat["moderate"])
    elif stars in (1, 2):
        lo, hi = cat.get("budget", cat["budget"])
    else:
        lo, hi = cat.get(travel_style, cat["moderate"])
    return {
        "price_per_night_min": lo,
        "price_per_night_max": hi,
        "price_label":         f"₹{lo:,}–₹{hi:,}/night",
        "price_source":        "Estimated",
    }


def _fetch_hotels_osm(arrival_lat: float, arrival_lon: float, radius_m: int) -> List[Dict]:
    """
    Fetch hotels from OpenStreetMap Overpass API.
    Global coverage. Completely free. No API key needed.
    """
    query = f"""
[out:json][timeout:8];
(
  node["tourism"~"hotel|motel|guest_house|hostel"]["name"](around:{radius_m},{arrival_lat},{arrival_lon});
  way["tourism"~"hotel|motel|guest_house|hostel"]["name"](around:{radius_m},{arrival_lat},{arrival_lon});
  relation["tourism"~"hotel|motel|guest_house|hostel"]["name"](around:{radius_m},{arrival_lat},{arrival_lon});
);
out center tags;
"""
    try:
        res = requests.post(OVERPASS_URL, data={"data": query}, headers=HEADERS, timeout=9)
        if res.status_code != 200:
            print(f"[HotelService] OSM HTTP {res.status_code}")
            return []
        elements = res.json().get("elements", [])
        print(f"[HotelService] OSM raw: {len(elements)} elements for ({arrival_lat:.4f},{arrival_lon:.4f})")
        return elements
    except Exception as e:
        print(f"[HotelService] OSM request error: {e}")
        return []


def _parse_osm(el: Dict, arrival_lat: float, arrival_lon: float,
               dest_category: str, travel_style: str) -> Optional[Dict]:
    tags = el.get("tags", {})
    name = tags.get("name", "").strip()
    if not name or len(name) < 3:
        return None

    if el["type"] == "node":
        lat = el.get("lat", 0.0)
        lon = el.get("lon", 0.0)
    else:
        center = el.get("center", {})
        lat = center.get("lat", 0.0)
        lon = center.get("lon", 0.0)

    if not lat or not lon:
        return None

    dist = _haversine_km(arrival_lat, arrival_lon, lat, lon)

    try:
        stars = int(tags.get("stars", 0) or 0)
    except Exception:
        stars = 0

    addr_parts = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
        tags.get("addr:city", ""),
        tags.get("addr:postcode", ""),
    ]
    address = ", ".join(p for p in addr_parts if p) or tags.get("addr:full", "") or "See Maps for address"

    price = _price_from_category(dest_category, travel_style, stars)

    return {
        "name":                     name,
        "rating":                   float(min(stars, 5)) if stars else 0.0,
        "user_ratings_total":       0,
        "address":                  address,
        "latitude":                 lat,
        "longitude":                lon,
        "distance_from_arrival_km": round(dist, 2),
        "price_per_night_min":      price["price_per_night_min"],
        "price_per_night_max":      price["price_per_night_max"],
        "price_label":              price["price_label"],
        "price_source":             price["price_source"],
        "maps_url":                 f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
        "website":                  tags.get("website", tags.get("contact:website", "")),
        "phone":                    tags.get("phone", tags.get("contact:phone", "")),
        "tourism_type":             tags.get("tourism", "hotel"),
        "place_id":                 f"osm_{el['type']}_{el['id']}",
    }


def _fetch_hotels_google(arrival_lat: float, arrival_lon: float,
                          destination: str, dest_category: str,
                          travel_style: str, max_results: int) -> List[Dict]:
    """Google Places fallback — only used if OSM returns too few and key works."""
    if not GOOGLE_PLACES_API_KEY:
        return []
    results: List[Dict] = []
    seen_ids: set = set()
    try:
        r = requests.get(
            GOOGLE_TEXT_SEARCH,
            params={"query": f"hotels in {destination}", "key": GOOGLE_PLACES_API_KEY},
            headers=HEADERS, timeout=8,
        )
        if r.status_code != 200 or r.json().get("status") != "OK":
            return []
        for item in r.json().get("results", []):
            pid = item.get("place_id", "")
            if pid and pid in seen_ids:
                continue
            if pid:
                seen_ids.add(pid)
            lat = item.get("geometry", {}).get("location", {}).get("lat", 0.0)
            lon = item.get("geometry", {}).get("location", {}).get("lng", 0.0)
            if not lat or not lon:
                continue
            pl = item.get("price_level")
            tier = _PRICE_LEVEL_TO_TIER.get(pl, travel_style) if pl is not None else travel_style
            lo, hi = PRICE_RANGES.get(dest_category, PRICE_RANGES["default"]).get(tier, (1000, 5000))
            dist = _haversine_km(arrival_lat, arrival_lon, lat, lon)
            results.append({
                "name":                     item.get("name", "").strip(),
                "rating":                   float(item.get("rating", 0.0)),
                "user_ratings_total":        int(item.get("user_ratings_total", 0)),
                "address":                  item.get("formatted_address", destination),
                "latitude":                 lat,
                "longitude":                lon,
                "distance_from_arrival_km": round(dist, 2),
                "price_per_night_min":      lo,
                "price_per_night_max":      hi,
                "price_label":              f"₹{lo:,}–₹{hi:,}/night",
                "price_source":             "Estimated",
                "maps_url":                 f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                "place_id":                 pid,
            })
    except Exception as e:
        print(f"[HotelService] Google fallback error: {e}")
    return results[:max_results]


def search_hotels_near_arrival(
    arrival_lat: float,
    arrival_lon: float,
    destination: str,
    travel_style: str = "moderate",
    dest_category: str = "default",
    radius_m: int = 5000,
    max_results: int = 10,
) -> Dict[str, Any]:
    """
    Search real hotels near the arrival point.

    Pipeline:
    1. For Indian destinations → check curated database first (instant, reliable)
    2. Try OSM if curated has no entry
    3. Try Google Places if OSM fails
    4. Fallback to destination city center search
    5. Final fallback: curated database for any destination

    Returns a dict with hotels list, fallback_used, fallback_reason, search_center_name.
    """
    if arrival_lat is None or arrival_lon is None:
        return {"hotels": [], "fallback_used": False, "fallback_reason": "", "search_center_name": ""}

    # ── Step 1: Curated database — primary for Indian destinations ────────────
    try:
        from services.curated_hotels import get_curated_hotels, is_indian_destination
        if is_indian_destination(destination):
            curated = get_curated_hotels(
                destination=destination,
                dest_lat=arrival_lat,
                dest_lon=arrival_lon,
                dest_category=dest_category,
                travel_style=travel_style,
                max_results=max_results,
            )
            if curated:
                return {
                    "hotels": curated,
                    "fallback_used": False,
                    "fallback_reason": "",
                    "search_center_name": destination,
                }
    except Exception as e:
        print(f"[HotelService] Curated lookup error: {e}")

    # ── Step 2: OSM near arrival point ───────────────────────────────────────
    hotels: List[Dict] = []
    seen: set = set()

    osm_elements = _fetch_hotels_osm(arrival_lat, arrival_lon, radius_m)
    for el in osm_elements:
        h = _parse_osm(el, arrival_lat, arrival_lon, dest_category, travel_style)
        if h is None:
            continue
        key = h["name"].lower().strip()
        if key not in seen:
            seen.add(key)
            hotels.append(h)
    print(f"[HotelService] OSM near arrival point: {len(hotels)} valid hotels")

    # Google Places fallback for arrival point
    if len(hotels) < 3:
        gp = _fetch_hotels_google(arrival_lat, arrival_lon, destination, dest_category, travel_style, max_results)
        for h in gp:
            key = h["name"].lower().strip()
            if key not in seen:
                seen.add(key)
                hotels.append(h)
        print(f"[HotelService] After Google fallback: {len(hotels)} total")

    if hotels:
        hotels.sort(key=lambda h: h["distance_from_arrival_km"])
        return {"hotels": hotels[:max_results], "fallback_used": False, "fallback_reason": "", "search_center_name": f"Near {destination} arrival point"}

    # ── Step 3: City center search ────────────────────────────────────────────
    print(f"[HotelService] ⚠️  No hotels near arrival — trying {destination} city center...")
    try:
        from services.places_service import geocode_nominatim
        dest_geo = geocode_nominatim(destination)
        if dest_geo:
            dest_lat, dest_lon = dest_geo["lat"], dest_geo["lon"]
            osm_city = _fetch_hotels_osm(dest_lat, dest_lon, radius_m)
            for el in osm_city:
                h = _parse_osm(el, dest_lat, dest_lon, dest_category, travel_style)
                if h is None:
                    continue
                key = h["name"].lower().strip()
                if key not in seen:
                    seen.add(key)
                    hotels.append(h)
            print(f"[HotelService] City center OSM: {len(hotels)} hotels")

            if len(hotels) < 3:
                gp_city = _fetch_hotels_google(dest_lat, dest_lon, destination, dest_category, travel_style, max_results)
                for h in gp_city:
                    key = h["name"].lower().strip()
                    if key not in seen:
                        seen.add(key)
                        hotels.append(h)
                print(f"[HotelService] After city Google: {len(hotels)} hotels")

            if hotels:
                hotels.sort(key=lambda h: h["distance_from_arrival_km"])
                return {
                    "hotels": hotels[:max_results],
                    "fallback_used": True,
                    "fallback_reason": f"No hotels found near arrival point. Showing hotels in {destination} city center.",
                    "search_center_name": f"{destination} (City Center)",
                }
    except Exception as e:
        print(f"[HotelService] City center fallback error: {e}")

    # ── Step 4: Final fallback — curated for any destination ─────────────────
    print(f"[HotelService] ⚠️  Trying curated hotel database for '{destination}'...")
    try:
        from services.curated_hotels import get_curated_hotels
        curated = get_curated_hotels(
            destination=destination,
            dest_lat=arrival_lat,
            dest_lon=arrival_lon,
            dest_category=dest_category,
            travel_style=travel_style,
            max_results=max_results,
        )
        if curated:
            return {
                "hotels": curated,
                "fallback_used": True,
                "fallback_reason": f"Showing curated hotels for {destination}.",
                "search_center_name": destination,
            }
    except Exception as e:
        print(f"[HotelService] Final curated fallback error: {e}")

    return {"hotels": [], "fallback_used": False, "fallback_reason": "", "search_center_name": ""}
