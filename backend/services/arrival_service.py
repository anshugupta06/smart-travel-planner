"""
Arrival Point Service
Determines the most appropriate arrival terminal for a destination
based on the selected transport mode.

Rules:
  Flight  → destination airport
  Train   → destination railway station
  Bus     → destination bus stand / ISBT
  Car/Cab → city center / popular landmark area
  Ship    → destination jetty / port
  Default → city center

Returns a verified dict with: name, latitude, longitude, address, maps_url
Never invents names — uses curated data first, then Google Places API fallback.
"""
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
PLACES_TEXT_SEARCH    = "https://maps.googleapis.com/maps/api/place/textsearch/json"
HEADERS               = {"User-Agent": "SmartTravelPlanner/1.0"}

# ── Curated arrival point database ──────────────────────────────────────────
# Format: city_lower → {mode_type → ArrivalPoint dict}
# mode_type: "airport" | "railway" | "bus" | "port" | "city_center"

ARRIVAL_POINTS: Dict[str, Dict[str, Dict[str, Any]]] = {

    # ── India ────────────────────────────────────────────────────────────────
    "delhi": {
        "airport":   {"name": "Indira Gandhi International Airport (DEL)", "latitude": 28.5562, "longitude": 77.1000, "address": "Terminal 3, IGI Airport, New Delhi 110037"},
        "railway":   {"name": "New Delhi Railway Station", "latitude": 28.6431, "longitude": 77.2195, "address": "Paharganj, New Delhi 110055"},
        "bus":       {"name": "Kashmere Gate ISBT", "latitude": 28.6660, "longitude": 77.2281, "address": "Kashmere Gate, New Delhi 110006"},
        "city_center": {"name": "Connaught Place, New Delhi", "latitude": 28.6315, "longitude": 77.2167, "address": "Connaught Place, New Delhi 110001"},
    },
    "mumbai": {
        "airport":   {"name": "Chhatrapati Shivaji Maharaj International Airport (BOM)", "latitude": 19.0896, "longitude": 72.8656, "address": "Andheri East, Mumbai 400099"},
        "railway":   {"name": "Mumbai CST (Chhatrapati Shivaji Terminus)", "latitude": 18.9400, "longitude": 72.8352, "address": "Fort, Mumbai 400001"},
        "bus":       {"name": "Mumbai Central Bus Depot", "latitude": 18.9714, "longitude": 72.8194, "address": "Mumbai Central, Mumbai 400008"},
        "port":      {"name": "Gateway of India Jetty", "latitude": 18.9220, "longitude": 72.8347, "address": "Apollo Bandar, Colaba, Mumbai 400001"},
        "city_center": {"name": "Dadar, Mumbai", "latitude": 19.0178, "longitude": 72.8478, "address": "Dadar, Mumbai 400014"},
    },
    "bangalore": {
        "airport":   {"name": "Kempegowda International Airport (BLR)", "latitude": 13.1986, "longitude": 77.7066, "address": "Devanahalli, Bengaluru 560300"},
        "railway":   {"name": "Krantivira Sangolli Rayanna (KSR) Railway Station", "latitude": 12.9771, "longitude": 77.5704, "address": "Gubbi Thotadappa Rd, Bengaluru 560023"},
        "bus":       {"name": "Majestic (Kempegowda) Bus Stand", "latitude": 12.9776, "longitude": 77.5713, "address": "Gubbi Thotadappa Rd, Bengaluru 560009"},
        "city_center": {"name": "MG Road, Bengaluru", "latitude": 12.9756, "longitude": 77.6066, "address": "MG Road, Bengaluru 560001"},
    },
    "bengaluru": {
        "airport":   {"name": "Kempegowda International Airport (BLR)", "latitude": 13.1986, "longitude": 77.7066, "address": "Devanahalli, Bengaluru 560300"},
        "railway":   {"name": "KSR Bengaluru City Railway Station", "latitude": 12.9771, "longitude": 77.5704, "address": "Gubbi Thotadappa Rd, Bengaluru 560023"},
        "bus":       {"name": "Majestic (Kempegowda) Bus Stand", "latitude": 12.9776, "longitude": 77.5713, "address": "Gubbi Thotadappa Rd, Bengaluru 560009"},
        "city_center": {"name": "MG Road, Bengaluru", "latitude": 12.9756, "longitude": 77.6066, "address": "MG Road, Bengaluru 560001"},
    },
    "hyderabad": {
        "airport":   {"name": "Rajiv Gandhi International Airport (HYD)", "latitude": 17.2403, "longitude": 78.4294, "address": "Shamshabad, Hyderabad 500409"},
        "railway":   {"name": "Hyderabad Deccan Nampally Railway Station", "latitude": 17.3850, "longitude": 78.4742, "address": "Nampally, Hyderabad 500001"},
        "bus":       {"name": "Mahatma Gandhi Bus Station (MGBS)", "latitude": 17.3784, "longitude": 78.4828, "address": "Imlibun, Hyderabad 500012"},
        "city_center": {"name": "Charminar, Hyderabad", "latitude": 17.3616, "longitude": 78.4747, "address": "Charminar, Hyderabad 500002"},
    },
    "chennai": {
        "airport":   {"name": "Chennai International Airport (MAA)", "latitude": 12.9941, "longitude": 80.1709, "address": "Tirusulam, Chennai 600027"},
        "railway":   {"name": "Chennai Central Railway Station", "latitude": 13.0827, "longitude": 80.2750, "address": "Park Town, Chennai 600003"},
        "bus":       {"name": "CMBT Chennai Mofussil Bus Terminus", "latitude": 13.0694, "longitude": 80.2177, "address": "Koyambedu, Chennai 600107"},
        "port":      {"name": "Chennai Port", "latitude": 13.0827, "longitude": 80.2896, "address": "Rajaji Salai, Chennai 600001"},
        "city_center": {"name": "Anna Salai (Mount Road), Chennai", "latitude": 13.0569, "longitude": 80.2428, "address": "Anna Salai, Chennai 600002"},
    },
    "kolkata": {
        "airport":   {"name": "Netaji Subhas Chandra Bose International Airport (CCU)", "latitude": 22.6547, "longitude": 88.4467, "address": "Dum Dum, Kolkata 700052"},
        "railway":   {"name": "Howrah Junction Railway Station", "latitude": 22.5839, "longitude": 88.3424, "address": "Howrah, Kolkata 711101"},
        "bus":       {"name": "Esplanade Bus Stand, Kolkata", "latitude": 22.5627, "longitude": 88.3519, "address": "Esplanade, Kolkata 700001"},
        "city_center": {"name": "Park Street, Kolkata", "latitude": 22.5519, "longitude": 88.3527, "address": "Park Street, Kolkata 700016"},
    },
    "goa": {
        "airport":   {"name": "Goa International Airport (GOI) – Mopa", "latitude": 15.7129, "longitude": 73.9124, "address": "Mopa, North Goa 403512"},
        "railway":   {"name": "Madgaon (Margao) Railway Station", "latitude": 15.2937, "longitude": 73.9700, "address": "Madgaon, South Goa 403601"},
        "bus":       {"name": "Kadamba Bus Terminal, Panaji", "latitude": 15.4989, "longitude": 73.8278, "address": "Patto, Panaji, Goa 403001"},
        "city_center": {"name": "Calangute Beach, North Goa", "latitude": 15.5438, "longitude": 73.7553, "address": "Calangute, North Goa 403516"},
    },
    "jaipur": {
        "airport":   {"name": "Jaipur International Airport (JAI)", "latitude": 26.8242, "longitude": 75.8122, "address": "Sanganer, Jaipur 303902"},
        "railway":   {"name": "Jaipur Junction Railway Station", "latitude": 26.9210, "longitude": 75.7880, "address": "Station Road, Jaipur 302006"},
        "bus":       {"name": "Sindhi Camp Bus Stand, Jaipur", "latitude": 26.9210, "longitude": 75.7912, "address": "Sindhi Camp, Jaipur 302001"},
        "city_center": {"name": "Hawa Mahal, Jaipur", "latitude": 26.9239, "longitude": 75.8267, "address": "Hawa Mahal Rd, Jaipur 302002"},
    },
    "agra": {
        "airport":   {"name": "Agra Airport (AGR)", "latitude": 27.1557, "longitude": 77.9608, "address": "Kheria, Agra 282001"},
        "railway":   {"name": "Agra Cantt Railway Station", "latitude": 27.1570, "longitude": 78.0098, "address": "Cantt Area, Agra 282001"},
        "bus":       {"name": "Idgah Bus Stand, Agra", "latitude": 27.1900, "longitude": 78.0131, "address": "Idgah, Agra 282001"},
        "city_center": {"name": "Taj Mahal Gate, Agra", "latitude": 27.1751, "longitude": 78.0421, "address": "Taj Ganj, Agra 282001"},
    },
    "varanasi": {
        "airport":   {"name": "Lal Bahadur Shastri International Airport (VNS)", "latitude": 25.4524, "longitude": 82.8593, "address": "Babatpur, Varanasi 221006"},
        "railway":   {"name": "Varanasi Junction Railway Station", "latitude": 25.3202, "longitude": 82.9996, "address": "Varanasi 221001"},
        "bus":       {"name": "Varanasi Cantt Bus Stand", "latitude": 25.3257, "longitude": 82.9992, "address": "Cantt, Varanasi 221002"},
        "city_center": {"name": "Dashashwamedh Ghat, Varanasi", "latitude": 25.3073, "longitude": 83.0107, "address": "Dashashwamedh Ghat Rd, Varanasi"},
    },
    "dehradun": {
        "airport":   {"name": "Jolly Grant Airport (DED)", "latitude": 30.1893, "longitude": 78.1806, "address": "Jolly Grant, Dehradun 249205"},
        "railway":   {"name": "Dehradun Railway Station", "latitude": 30.3165, "longitude": 78.0322, "address": "Railway Station Rd, Dehradun 248001"},
        "bus":       {"name": "Dehradun ISBT Bus Stand", "latitude": 30.3188, "longitude": 78.0358, "address": "ISBT, Dehradun 248001"},
        "city_center": {"name": "Paltan Bazaar, Dehradun", "latitude": 30.3247, "longitude": 78.0413, "address": "Paltan Bazaar, Dehradun 248001"},
    },
    "manali": {
        "airport":   {"name": "Bhuntar Airport (KUU) via Kullu", "latitude": 31.8787, "longitude": 77.1544, "address": "Bhuntar, Kullu 175125"},
        "bus":       {"name": "Manali Bus Stand (HRTC)", "latitude": 32.2396, "longitude": 77.1887, "address": "Mall Road, Manali 175131"},
        "city_center": {"name": "Mall Road, Manali", "latitude": 32.2432, "longitude": 77.1892, "address": "The Mall, Manali 175131"},
    },
    "shimla": {
        "airport":   {"name": "Shimla Airport (SLV)", "latitude": 31.0818, "longitude": 77.0674, "address": "Jubbarhatti, Shimla 171205"},
        "railway":   {"name": "Shimla Railway Station (Kalka-Shimla Toy Train)", "latitude": 31.1037, "longitude": 77.1717, "address": "Cart Road, Shimla 171001"},
        "bus":       {"name": "Shimla ISBT (Inter State Bus Terminal)", "latitude": 31.1063, "longitude": 77.1745, "address": "Cart Road, Shimla 171001"},
        "city_center": {"name": "The Ridge, Shimla", "latitude": 31.1048, "longitude": 77.1734, "address": "The Ridge, Shimla 171001"},
    },
    "leh": {
        "airport":   {"name": "Kushok Bakula Rimpochhe Airport (IXL)", "latitude": 34.1359, "longitude": 77.5465, "address": "Leh Airport, Leh 194101"},
        "bus":       {"name": "Leh Bus Stand (J&K SRTC)", "latitude": 34.1669, "longitude": 77.5872, "address": "Main Bazaar, Leh 194101"},
        "city_center": {"name": "Leh Main Bazaar", "latitude": 34.1676, "longitude": 77.5858, "address": "Main Bazaar, Leh 194101"},
    },
    "srinagar": {
        "airport":   {"name": "Sheikh ul-Alam International Airport (SXR)", "latitude": 33.9871, "longitude": 74.7742, "address": "Humhama, Srinagar 190007"},
        "bus":       {"name": "Srinagar Bus Stand (TRC)", "latitude": 34.0837, "longitude": 74.7973, "address": "Tourist Reception Centre, Srinagar 190001"},
        "city_center": {"name": "Dal Lake, Srinagar", "latitude": 34.0935, "longitude": 74.8365, "address": "Dal Lake, Srinagar 190001"},
    },
    "mussoorie": {
        "bus":       {"name": "Mussoorie Library Bus Stand", "latitude": 30.4598, "longitude": 78.0644, "address": "Library Road, Mussoorie 248179"},
        "city_center": {"name": "Mall Road, Mussoorie", "latitude": 30.4574, "longitude": 78.0665, "address": "The Mall, Mussoorie 248179"},
    },
    "rishikesh": {
        "railway":   {"name": "Rishikesh Railway Station", "latitude": 30.1162, "longitude": 78.2862, "address": "Rishikesh 249201"},
        "bus":       {"name": "Rishikesh ISBT Bus Stand", "latitude": 30.1083, "longitude": 78.2940, "address": "Main Road, Rishikesh 249201"},
        "city_center": {"name": "Laxman Jhula, Rishikesh", "latitude": 30.1278, "longitude": 78.3215, "address": "Laxman Jhula, Rishikesh 249302"},
    },
    "udaipur": {
        "airport":   {"name": "Maharana Pratap Airport (UDR)", "latitude": 24.6177, "longitude": 73.8961, "address": "Dabok, Udaipur 313022"},
        "railway":   {"name": "Udaipur City Railway Station", "latitude": 24.5792, "longitude": 73.6879, "address": "Station Road, Udaipur 313001"},
        "bus":       {"name": "Udaipur Bus Stand (RSRTC)", "latitude": 24.5856, "longitude": 73.6830, "address": "Station Road, Udaipur 313001"},
        "city_center": {"name": "City Palace, Udaipur", "latitude": 24.5764, "longitude": 73.6831, "address": "City Palace Complex, Udaipur 313001"},
    },
    "kochi": {
        "airport":   {"name": "Cochin International Airport (COK)", "latitude": 10.1520, "longitude": 76.3920, "address": "Nedumbassery, Kochi 683111"},
        "railway":   {"name": "Ernakulam Junction Railway Station", "latitude": 9.9834, "longitude": 76.2918, "address": "Ernakulam, Kochi 682016"},
        "bus":       {"name": "KSRTC Bus Stand, Ernakulam", "latitude": 9.9834, "longitude": 76.2772, "address": "Ernakulam, Kochi 682016"},
        "port":      {"name": "Fort Kochi Jetty", "latitude": 9.9627, "longitude": 76.2426, "address": "Fort Kochi, Kochi 682001"},
        "city_center": {"name": "MG Road, Kochi", "latitude": 9.9790, "longitude": 76.2954, "address": "MG Road, Ernakulam, Kochi"},
    },
    "andaman": {
        "airport":   {"name": "Veer Savarkar International Airport (IXZ)", "latitude": 11.6412, "longitude": 92.7295, "address": "Port Blair 744101"},
        "port":      {"name": "Haddo Jetty, Port Blair", "latitude": 11.6712, "longitude": 92.7387, "address": "Haddo, Port Blair 744102"},
        "city_center": {"name": "Aberdeen Bazaar, Port Blair", "latitude": 11.6672, "longitude": 92.7427, "address": "Aberdeen Bazaar, Port Blair 744101"},
    },
    "port blair": {
        "airport":   {"name": "Veer Savarkar International Airport (IXZ)", "latitude": 11.6412, "longitude": 92.7295, "address": "Port Blair 744101"},
        "port":      {"name": "Haddo Jetty, Port Blair", "latitude": 11.6712, "longitude": 92.7387, "address": "Haddo, Port Blair 744102"},
        "city_center": {"name": "Aberdeen Bazaar, Port Blair", "latitude": 11.6672, "longitude": 92.7427, "address": "Aberdeen Bazaar, Port Blair 744101"},
    },
    # ── International ────────────────────────────────────────────────────────
    "dubai": {
        "airport":   {"name": "Dubai International Airport (DXB)", "latitude": 25.2532, "longitude": 55.3657, "address": "Dubai International Airport, Dubai"},
        "city_center": {"name": "Dubai Mall / Downtown Dubai", "latitude": 25.1983, "longitude": 55.2796, "address": "Downtown Dubai, UAE"},
    },
    "singapore": {
        "airport":   {"name": "Changi International Airport (SIN)", "latitude": 1.3644, "longitude": 103.9915, "address": "Airport Blvd, Singapore 819642"},
        "city_center": {"name": "Orchard Road, Singapore", "latitude": 1.3010, "longitude": 103.8353, "address": "Orchard Road, Singapore"},
    },
    "bangkok": {
        "airport":   {"name": "Suvarnabhumi Airport (BKK)", "latitude": 13.6900, "longitude": 100.7501, "address": "Racha Thewa, Bang Phli, Samut Prakan"},
        "city_center": {"name": "Siam Square, Bangkok", "latitude": 13.7455, "longitude": 100.5343, "address": "Siam, Bangkok, Thailand"},
    },
    "tokyo": {
        "airport":   {"name": "Narita International Airport (NRT)", "latitude": 35.7719, "longitude": 140.3929, "address": "Narita, Chiba 282-0004, Japan"},
        "city_center": {"name": "Shinjuku, Tokyo", "latitude": 35.6905, "longitude": 139.6995, "address": "Shinjuku, Tokyo, Japan"},
    },
    "paris": {
        "airport":   {"name": "Charles de Gaulle Airport (CDG)", "latitude": 49.0097, "longitude": 2.5479, "address": "95700 Roissy-en-France, France"},
        "city_center": {"name": "Gare du Nord, Paris", "latitude": 48.8809, "longitude": 2.3553, "address": "Place Napoléon III, 75010 Paris, France"},
    },
    "london": {
        "airport":   {"name": "Heathrow Airport (LHR)", "latitude": 51.4700, "longitude": -0.4543, "address": "Longford, Hounslow TW6, United Kingdom"},
        "city_center": {"name": "Victoria Station, London", "latitude": 51.4952, "longitude": -0.1441, "address": "Victoria St, London SW1V 1JU, UK"},
    },
}


# ── Transport mode → arrival point type mapping ──────────────────────────────
_MODE_TO_POINT_TYPE = {
    "flight":    "airport",
    "train":     "railway",
    "bus":       "bus",
    "ship":      "port",
    "cruise":    "port",
    "ferry":     "port",
    "taxi":      "city_center",
    "cab":       "city_center",
    "car":       "city_center",
    "self-drive":"city_center",
}

def _mode_to_type(transport_mode: str) -> str:
    """Map a transport mode string to an arrival point type."""
    m = transport_mode.lower().strip()
    for key, point_type in _MODE_TO_POINT_TYPE.items():
        if key in m:
            return point_type
    return "city_center"


def _maps_url(lat: float, lon: float, name: str = "") -> str:
    if lat and lon:
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    if name:
        import urllib.parse
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(name)}"
    return ""


def _enrich(point: Dict[str, Any], destination: str, point_type: str) -> Dict[str, Any]:
    """Add maps_url and type metadata to an arrival point dict."""
    return {
        "name":        point["name"],
        "latitude":    point["latitude"],
        "longitude":   point["longitude"],
        "address":     point.get("address", destination),
        "type":        point_type,
        "maps_url":    _maps_url(point["latitude"], point["longitude"], point["name"]),
        "verified":    True,
        "source":      "curated",
    }


def _google_places_terminal(destination: str, point_type: str) -> Optional[Dict[str, Any]]:
    """
    Fallback: search Google Places for the terminal if not in curated data.
    Only called when curated lookup fails.
    """
    if not GOOGLE_PLACES_API_KEY:
        return None

    query_map = {
        "airport":   f"international airport in {destination}",
        "railway":   f"main railway station in {destination}",
        "bus":       f"main bus stand ISBT in {destination}",
        "port":      f"jetty port in {destination}",
        "city_center": f"city center {destination}",
    }
    query = query_map.get(point_type, f"arrival point {destination}")

    try:
        res = requests.get(
            PLACES_TEXT_SEARCH,
            params={"query": query, "key": GOOGLE_PLACES_API_KEY},
            headers=HEADERS,
            timeout=6,
        )
        if res.status_code == 200:
            results = res.json().get("results", [])
            if results:
                r   = results[0]
                lat = r.get("geometry", {}).get("location", {}).get("lat", 0.0)
                lon = r.get("geometry", {}).get("location", {}).get("lng", 0.0)
                return {
                    "name":      r.get("name", f"{destination} {point_type}"),
                    "latitude":  lat,
                    "longitude": lon,
                    "address":   r.get("formatted_address", destination),
                    "type":      point_type,
                    "maps_url":  _maps_url(lat, lon, r.get("name", "")),
                    "verified":  True,
                    "source":    "google_places",
                }
    except Exception as e:
        print(f"[ArrivalService] Google Places fallback error: {e}")
    return None


def get_arrival_point(
    destination: str,
    transport_mode: str,
) -> Dict[str, Any]:
    """
    Determine the verified arrival point for a destination based on transport mode.

    Returns a dict with:
      name, latitude, longitude, address, type, maps_url, verified, source

    Priority:
      1. Curated ARRIVAL_POINTS database (exact city + mode type match)
      2. Curated database with city_center fallback (same city, different mode)
      3. Google Places API search
      4. Geocode-based city center estimate

    Never invents names.
    """
    city        = destination.lower().strip()
    point_type  = _mode_to_type(transport_mode)

    print(f"[ArrivalService] destination='{destination}' mode='{transport_mode}' → type='{point_type}'")

    # ── Step 1: Exact match from curated data ────────────────────────────────
    city_data = None
    # Try exact match first
    if city in ARRIVAL_POINTS:
        city_data = ARRIVAL_POINTS[city]
    else:
        # Partial keyword match (e.g. "new delhi" → "delhi")
        for key, data in ARRIVAL_POINTS.items():
            if key in city or city in key:
                city_data = data
                break

    if city_data:
        if point_type in city_data:
            print(f"[ArrivalService] ✅ Curated exact: '{city}' → {city_data[point_type]['name']}")
            return _enrich(city_data[point_type], destination, point_type)

        # Requested type not available (e.g. no train to Leh) → use city_center
        if "city_center" in city_data:
            print(f"[ArrivalService] ✅ Curated fallback city_center: '{city}'")
            return _enrich(city_data["city_center"], destination, "city_center")

    # ── Step 2: Google Places fallback ───────────────────────────────────────
    gp = _google_places_terminal(destination, point_type)
    if gp:
        print(f"[ArrivalService] ✅ Google Places: {gp['name']}")
        return gp

    # ── Step 3: Geocode-based city center estimate ────────────────────────────
    try:
        from utils.helpers import geocode_city
        coords = geocode_city(destination)
        if coords:
            lat, lon = coords
            name = f"{destination.title()} City Center"
            print(f"[ArrivalService] ⚠️  Using geocoded city center for '{destination}'")
            return {
                "name":      name,
                "latitude":  lat,
                "longitude": lon,
                "address":   destination,
                "type":      "city_center",
                "maps_url":  _maps_url(lat, lon, name),
                "verified":  False,
                "source":    "geocode",
            }
    except Exception as e:
        print(f"[ArrivalService] Geocode error: {e}")

    # ── Step 4: Last resort — return minimal dict with flag ───────────────────
    print(f"[ArrivalService] ❌ No arrival point found for '{destination}'")
    return {
        "name":      f"{destination.title()} (arrival point unknown)",
        "latitude":  0.0,
        "longitude": 0.0,
        "address":   destination,
        "type":      point_type,
        "maps_url":  "",
        "verified":  False,
        "source":    "unknown",
    }
