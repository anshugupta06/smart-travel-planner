"""
ML Service: Hybrid approach combining rule-based scoring with ML techniques.
- Attraction ranking using weighted multi-criteria scoring (tourist popularity-first)
- Route optimization using nearest-neighbor heuristic (TSP approximation)
- Budget prediction using regression-based estimation
- Day-wise itinerary distribution with geo-clustering
"""
import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from utils.helpers import haversine_distance, geocode_city


# ---------------------------------------------------------------------------
# Tourist Popularity — World-famous landmark name list
# These places get a large bonus regardless of other scores.
# ---------------------------------------------------------------------------

WORLD_FAMOUS_KEYWORDS = {
    # Turkey / Istanbul
    "hagia sophia", "blue mosque", "topkapi", "grand bazaar", "basilica cistern",
    "galata tower", "dolmabahce", "bosphorus", "spice bazaar", "maiden's tower",
    "sultan ahmed", "galata bridge", "istiklal", "taksim",
    # India
    "taj mahal", "red fort", "qutub minar", "india gate", "akshardham",
    "gateway of india", "marine drive", "amber fort", "hawa mahal",
    "dashashwamedh", "kashi vishwanath", "lotus temple",
    # International
    "eiffel tower", "louvre", "notre-dame", "arc de triomphe", "versailles",
    "colosseum", "vatican", "trevi fountain", "pantheon", "sistine",
    "burj khalifa", "palm jumeirah", "dubai mall", "dubai fountain",
    "big ben", "tower of london", "buckingham palace", "london eye",
    "statue of liberty", "central park", "times square", "empire state",
    "brooklyn bridge", "metropolitan museum",
    "senso-ji", "shibuya", "tokyo skytree", "meiji shrine", "shinjuku",
    "forbidden city", "great wall", "tiananmen", "temple of heaven",
    "sagrada familia", "park guell", "alhambra",
    "acropolis", "parthenon", "santorini",
    "angkor wat", "angkor",
    "sydney opera house", "harbour bridge", "bondi beach",
    "bagan", "shwedagon",
    "petronas", "klcc",
    "gardens by the bay", "marina bay sands", "sentosa",
    "wat pho", "grand palace", "wat arun",
    "borobudur", "tanah lot", "ubud", "kuta beach",
    "machu picchu", "chichen itza", "christ the redeemer",
    "niagara falls",
    "safari", "serengeti", "pyramids", "sphinx",
}

# Attraction types that signal a must-visit tourist landmark
HIGH_POPULARITY_TYPES = {
    "tourist_attraction", "landmark", "museum", "art_gallery",
    "place_of_worship", "amusement_park", "zoo", "aquarium",
    "natural_feature", "park", "historical",
}

# Types that are NOT typical tourist priorities
LOW_POPULARITY_TYPES = {
    "point_of_interest", "establishment", "artwork",
    "memorial", "ruins",  # minor ruins rank lower than famous ones
}


def compute_tourist_popularity(place_name: str, place_types: List[str]) -> float:
    """
    Compute a 0-1 tourist popularity score.
    World-famous landmarks get the maximum score.
    Type-based scoring fills the gap for everything else.
    """
    name_lower = place_name.strip().lower()

    # Check if name contains any world-famous keyword
    for keyword in WORLD_FAMOUS_KEYWORDS:
        if keyword in name_lower:
            return 1.0

    # Type-based popularity
    has_high_type = any(t in HIGH_POPULARITY_TYPES for t in place_types)
    has_low_type  = any(t in LOW_POPULARITY_TYPES  for t in place_types)

    if has_high_type and not has_low_type:
        return 0.75
    elif has_high_type:
        return 0.55
    else:
        return 0.30


# ---------------------------------------------------------------------------
# Updated scoring weights — tourist popularity is now the dominant factor
# ---------------------------------------------------------------------------

TRAVEL_TYPE_WEIGHTS = {
    #                rating  popularity  accessibility  uniqueness
    "budget":    {"rating": 0.25, "popularity": 0.45, "accessibility": 0.20, "uniqueness": 0.10},
    "moderate":  {"rating": 0.30, "popularity": 0.45, "accessibility": 0.15, "uniqueness": 0.10},
    "luxury":    {"rating": 0.30, "popularity": 0.40, "accessibility": 0.10, "uniqueness": 0.20},
}

PREFERENCE_BOOST: Dict[str, List[str]] = {
    "nature":    ["park", "natural_feature", "campground", "waterfall", "peak", "beach"],
    "history":   ["historical", "museum", "place_of_worship", "church", "hindu_temple", "castle", "ruins", "fort", "monument"],
    "adventure": ["adventure", "amusement_park", "campground", "natural_feature"],
    "food":      ["restaurant", "food", "bakery", "cafe", "market"],
    "shopping":  ["shopping_mall", "store", "market"],
    "beach":     ["beach", "natural_feature"],
    "spiritual": ["place_of_worship", "hindu_temple", "mosque", "church"],
    "art":       ["museum", "art_gallery", "gallery"],
    "family":    ["amusement_park", "zoo", "park", "aquarium", "theme_park"],
    "luxury":    ["spa", "casino", "shopping_mall"],
}


def compute_accessibility_score(price_level: int, place_types: List[str]) -> float:
    """Lower cost = more accessible."""
    if price_level == 0:
        return 1.0
    elif price_level == 1:
        return 0.8
    elif price_level == 2:
        return 0.6
    else:
        return 0.4


def compute_uniqueness_score(place_types: List[str], all_places_types: List[List[str]]) -> float:
    """Places with rarer types get higher uniqueness scores."""
    if not place_types:
        return 0.5
    type_counts: Dict[str, int] = {}
    for types in all_places_types:
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1
    total = len(all_places_types) or 1
    rarity_scores = [1.0 - (type_counts.get(t, 1) / total) for t in place_types]
    return sum(rarity_scores) / len(rarity_scores) if rarity_scores else 0.5


def score_and_rank_attractions(
    places: List[Dict[str, Any]],
    travel_type: str = "moderate",
    preferences: List[str] = None,
) -> List[Dict[str, Any]]:
    """
    Rank attractions using a weighted multi-criteria ML scoring model.
    Tourist popularity is the dominant factor (weight ~0.45) so that
    Hagia Sophia always outranks an obscure local monument.
    Returns places sorted by composite score (descending).
    """
    if not places:
        return []
    weights   = TRAVEL_TYPE_WEIGHTS.get(travel_type, TRAVEL_TYPE_WEIGHTS["moderate"])
    all_types = [p.get("types", []) for p in places]
    # Build preference type set
    pref_types: set = set()
    if preferences:
        for pref in preferences:
            pref_lower = pref.lower()
            for key, types in PREFERENCE_BOOST.items():
                if key in pref_lower or pref_lower in key:
                    pref_types.update(types)
    scored = []
    for place in places:
        rating      = float(place.get("rating", 3.5))
        price_level = int(place.get("price_level", 1))
        place_types = place.get("types", [])
        place_name  = place.get("name", "")
        # Core scores
        norm_rating   = min(rating / 5.0, 1.0)
        popularity    = compute_tourist_popularity(place_name, place_types)
        accessibility = compute_accessibility_score(price_level, place_types)
        uniqueness    = compute_uniqueness_score(place_types, all_types)
        composite = (
            weights["rating"]        * norm_rating
            + weights["popularity"]  * popularity
            + weights["accessibility"] * accessibility
            + weights["uniqueness"]  * uniqueness
        )
        # Preference boost — adds 20% if types match user interests
        if pref_types and any(t in pref_types for t in place_types):
            composite *= 1.20
        place = dict(place)
        place["popularity_score"] = round(composite, 4)
        scored.append((composite, place))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


# ---------------------------------------------------------------------------
# Route Optimization (Nearest Neighbor TSP Heuristic)
# ---------------------------------------------------------------------------

def optimize_route(
    places: List[Dict[str, Any]],
    origin_lat: float = None,
    origin_lon: float = None,
) -> List[Dict[str, Any]]:
    """
    Optimizes the visiting order using nearest-neighbor heuristic.
    This is the ML/algorithmic hybrid component for route planning.
    """
    if len(places) <= 2:
        return places

    # Filter out places without valid coordinates
    valid = [p for p in places if p.get("latitude", 0) != 0 or p.get("longitude", 0) != 0]
    invalid = [p for p in places if p not in valid]

    if len(valid) <= 2:
        return places

    # Start from origin or first place
    if origin_lat and origin_lon:
        current_lat, current_lon = origin_lat, origin_lon
    else:
        current_lat = valid[0].get("latitude", 0)
        current_lon = valid[0].get("longitude", 0)

    unvisited = list(valid)
    ordered = []

    while unvisited:
        nearest = None
        min_dist = float("inf")
        for place in unvisited:
            dist = haversine_distance(
                current_lat, current_lon,
                place.get("latitude", current_lat),
                place.get("longitude", current_lon),
            )
            if dist < min_dist:
                min_dist = dist
                nearest = place
        if nearest:
            ordered.append(nearest)
            current_lat = nearest.get("latitude", current_lat)
            current_lon = nearest.get("longitude", current_lon)
            unvisited.remove(nearest)

    return ordered + invalid


# ---------------------------------------------------------------------------
# Local Route Segments — transport between stops within a day
# ---------------------------------------------------------------------------

# Destination terrain profiles — affects local transport recommendations
_HILL_KEYWORDS    = {"manali", "shimla", "leh", "ladakh", "darjeeling", "ooty", "mussoorie",
                     "nainital", "munnar", "coorg", "spiti", "rohtang", "solang"}
_ISLAND_KEYWORDS  = {"andaman", "lakshadweep", "maldives", "bali", "phuket", "koh samui"}
_METRO_KEYWORDS   = {"delhi", "mumbai", "bangalore", "bengaluru", "kolkata", "chennai",
                     "hyderabad", "pune", "ahmedabad"}
_INTL_KEYWORDS    = {"paris", "london", "tokyo", "dubai", "singapore", "hong kong",
                     "new york", "sydney", "rome", "istanbul", "amsterdam", "bangkok"}


def _local_transport_mode(
    dist_km: float,
    destination: str,
) -> Dict[str, Any]:
    """
    Choose the best local transport mode between two stops based on
    distance, terrain, and destination type.

    Returns dict with: mode, emoji, speed_kmh, cost_per_km_inr, fixed_cost, note
    """
    dest = destination.lower()
    is_hill   = any(k in dest for k in _HILL_KEYWORDS)
    is_island = any(k in dest for k in _ISLAND_KEYWORDS)
    is_metro  = any(k in dest for k in _METRO_KEYWORDS)
    is_intl   = any(k in dest for k in _INTL_KEYWORDS)

    # Walking: ≤ 1.5 km on flat terrain, ≤ 0.8 km on hills
    walk_limit = 0.8 if is_hill else 1.5
    if dist_km <= walk_limit:
        return {"mode": "Walk", "emoji": "🚶", "speed_kmh": 5,
                "cost_per_km": 0, "fixed_cost": 0, "note": ""}

    # Cable car: hill destinations with cable car infrastructure
    if is_hill and 1.0 <= dist_km <= 8.0:
        return {"mode": "Cable Car / Gondola", "emoji": "🚡", "speed_kmh": 20,
                "cost_per_km": 0, "fixed_cost": 350, "note": "Check cable car timings in advance"}

    # Ferry: island destinations
    if is_island and dist_km > 3:
        return {"mode": "Ferry / Boat", "emoji": "⛴️", "speed_kmh": 25,
                "cost_per_km": 0, "fixed_cost": 400, "note": "Book ferry tickets early in peak season"}

    # Metro: major cities, short-medium distances
    if is_metro and 2 <= dist_km <= 20:
        return {"mode": "Metro", "emoji": "🚇", "speed_kmh": 35,
                "cost_per_km": 2.5, "fixed_cost": 20, "note": "Buy Metro card for discounts"}

    # International cities: prefer taxi/uber for comfort
    if is_intl:
        if dist_km <= 5:
            return {"mode": "Walk / Metro", "emoji": "🚶🚇", "speed_kmh": 15,
                    "cost_per_km": 2, "fixed_cost": 15, "note": ""}
        return {"mode": "Taxi / Uber", "emoji": "🚕", "speed_kmh": 25,
                "cost_per_km": 45, "fixed_cost": 100, "note": "Use Uber/Grab app"}

    # Hill destinations: taxi/jeep for most inter-attraction travel
    if is_hill:
        if dist_km <= 15:
            return {"mode": "Taxi / Shared Jeep", "emoji": "🚕", "speed_kmh": 25,
                    "cost_per_km": 18, "fixed_cost": 80,
                    "note": "Shared jeeps available at local taxi stands"}
        return {"mode": "Private Taxi", "emoji": "🚗", "speed_kmh": 30,
                "cost_per_km": 22, "fixed_cost": 150,
                "note": "Hire a full-day taxi for ₹1500–2500"}

    # Auto-rickshaw: short distances in Indian cities
    if dist_km <= 5 and not is_metro:
        return {"mode": "Auto Rickshaw", "emoji": "🛺", "speed_kmh": 20,
                "cost_per_km": 12, "fixed_cost": 25, "note": "Use meter or agree fare beforehand"}

    # Bus: medium distances where available
    if 5 < dist_km <= 20:
        return {"mode": "Bus / Local Bus", "emoji": "🚌", "speed_kmh": 22,
                "cost_per_km": 2, "fixed_cost": 15, "note": "Check local bus routes on Google Maps"}

    # Taxi for everything else
    return {"mode": "Taxi / Cab", "emoji": "🚕", "speed_kmh": 30,
            "cost_per_km": 14, "fixed_cost": 50, "note": ""}


def compute_local_route(
    day_places: List[Dict[str, Any]],
    destination: str,
    hotel_name: str = "Your Hotel",
) -> List[Dict[str, Any]]:
    """
    Compute local transit segments between consecutive stops on a day.

    Returns a list of segment dicts:
      from_name, to_name, mode, emoji, distance_km, duration_min, cost_inr, note

    Segments: Hotel→Stop1, Stop1→Stop2, ..., StopN→Hotel
    If coordinates are missing, uses a typical city-block distance estimate.
    """
    if not day_places:
        return []

    # Build ordered stop list including hotel at start
    stops = [{"name": hotel_name, "latitude": 0.0, "longitude": 0.0}] + day_places

    segments = []
    for i in range(len(stops) - 1):
        a = stops[i]
        b = stops[i + 1]

        # Distance calculation
        lat_a, lon_a = a.get("latitude", 0.0), a.get("longitude", 0.0)
        lat_b, lon_b = b.get("latitude", 0.0), b.get("longitude", 0.0)

        if lat_a and lon_a and lat_b and lon_b:
            dist_km = round(haversine_distance(lat_a, lon_a, lat_b, lon_b), 2)
        else:
            # No coordinates — estimate typical intra-city distance
            dist_km = round(1.5 + i * 0.8, 1)

        # Choose transport mode
        transport = _local_transport_mode(dist_km, destination)

        # Calculate time and cost
        speed     = transport["speed_kmh"]
        duration  = max(3, round((dist_km / speed) * 60))   # minutes, minimum 3
        cost      = round(transport["fixed_cost"] + dist_km * transport["cost_per_km"])

        segments.append({
            "from_name":    a["name"],
            "to_name":      b["name"],
            "mode":         transport["mode"],
            "emoji":        transport["emoji"],
            "distance_km":  dist_km,
            "duration_min": duration,
            "cost_inr":     cost,
            "note":         transport["note"],
        })

    print(f"[Planner] Local route: {len(segments)} segments for Day with "
          f"{len(day_places)} stops in {destination}")
    return segments

def _places_per_day_target(num_days: int, total_places: int) -> int:
    """
    Return the ideal attractions-per-day count based on trip duration.

    Schedule (per requirements):
      half day (0.5) → 1–2  → use 2
      1 day          → 3–5  → use min(5, total)
      2 days         → 4–6  → use 3/day
      3 days         → 6–9  → use 3/day
      4 days         → 8–12 → use 3/day
      5+ days        → 2–3  → use 3/day

    Returned value is a *per-day* target, capped to avoid using more places
    than we have.
    """
    if num_days <= 1:
        target = min(5, total_places)      # 1-day: show up to 5 attractions
    elif num_days == 2:
        target = 3                          # 2 days × 3 = 6 attractions
    elif num_days <= 4:
        target = 3                          # 3–4 days × 3 = 9–12 attractions
    else:
        target = 3                          # 5+ days × 3 = 15+ attractions

    # Never ask for more than we have across all days
    max_possible = max(1, total_places // max(num_days, 1))
    return max(1, min(target, max(max_possible, 2)))


def distribute_places_by_day(
    places: List[Dict[str, Any]],
    num_days: int,
    places_per_day: int = 3,
) -> List[List[Dict[str, Any]]]:
    """
    Distribute ranked places evenly across trip days.

    Rules:
      - Every place appears exactly once (no duplicates)
      - Every day gets ≥ 1 attraction (no empty days)
      - Even spread using base + remainder — earlier days get one extra
      - If total places < num_days, every day gets 1 place;
        extra days beyond len(places) reuse top attractions
      - places_per_day is a cap, not a fixed quota

    Examples (with places_per_day=3):
      12 places, 4 days  → [3, 3, 3, 3]
      10 places, 4 days  → [3, 3, 2, 2]
       7 places, 3 days  → [3, 2, 2]
       3 places, 5 days  → [1, 1, 1, 1, 1] (cycle top places)
       1 place,  3 days  → [1, 1, 1]
    """
    if not places:
        return [[] for _ in range(max(1, num_days))]

    num_days       = max(1, num_days)
    places_per_day = max(1, min(places_per_day, 5))
    total          = len(places)

    # ── Case 1: Fewer unique places than days ────────────────────────────────
    # Give each day 1 unique place; days beyond total reuse from the top
    if total <= num_days:
        result = []
        for i in range(num_days):
            result.append([places[i % total]])
        print(f"[Planner] distribute: {total} places ≤ {num_days} days "
              f"→ 1/day (cycling top attractions for extra days)")
        return result

    # ── Case 2: Normal distribution — even spread ────────────────────────────
    # Use all places up to num_days * places_per_day
    max_usable = min(total, num_days * places_per_day)
    usable     = places[:max_usable]
    used       = len(usable)

    base      = used // num_days
    remainder = used % num_days

    result = []
    idx    = 0
    for day in range(num_days):
        count = base + (1 if day < remainder else 0)
        count = max(1, min(count, places_per_day))
        chunk = usable[idx: idx + count]
        result.append(chunk)
        idx += count

    # Safety: if any day is empty (shouldn't happen), fill from top
    for i, day_list in enumerate(result):
        if not day_list:
            result[i] = [places[i % total]]

    sizes = [len(d) for d in result]
    total_assigned = sum(sizes)
    print(f"[Planner] distribute: {total} places → {num_days} days "
          f"(cap {places_per_day}/day) → sizes={sizes} "
          f"(total assigned={total_assigned})")
    return result


# ---------------------------------------------------------------------------
# Budget Prediction — Destination-Category-Aware Realistic Cost Model
# ---------------------------------------------------------------------------
# All values are in INR (Indian Rupees) per person per day.
# Exchange rate assumptions used for international destinations:
#   USD ~ 83 INR | EUR ~ 90 INR | GBP ~ 105 INR | AED ~ 22 INR
#   SGD ~ 62 INR | JPY ~ 0.55 INR | HKD ~ 10.6 INR | THB ~ 2.3 INR
# ---------------------------------------------------------------------------

# ── DESTINATION CATEGORIES ──────────────────────────────────────────────────
# Maps keyword → category string
DEST_CATEGORY_MAP = {
    # Indian Tier-2 / Hill / Leisure
    "goa": "india_tourist", "shimla": "india_hill", "manali": "india_hill",
    "darjeeling": "india_hill", "ooty": "india_hill", "munnar": "india_hill",
    "kodaikanal": "india_hill", "mussoorie": "india_hill", "nainital": "india_hill",
    "coorg": "india_hill", "rishikesh": "india_leisure", "haridwar": "india_leisure",
    "varanasi": "india_leisure", "amritsar": "india_leisure", "pushkar": "india_leisure",
    "agra": "india_tourist", "jaipur": "india_tourist", "udaipur": "india_tourist",
    "jodhpur": "india_tourist", "hampi": "india_tourist", "khajuraho": "india_tourist",
    "mysore": "india_tourist", "madurai": "india_tourist",
    # Indian Metros
    "mumbai": "india_metro", "delhi": "india_metro", "bangalore": "india_metro",
    "bengaluru": "india_metro", "hyderabad": "india_metro", "chennai": "india_metro",
    "kolkata": "india_metro", "pune": "india_metro", "ahmedabad": "india_metro",
    # Indian Islands
    "andaman": "india_island", "lakshadweep": "india_island",
    # Southeast Asia
    "bali": "southeast_asia", "phuket": "southeast_asia", "bangkok": "southeast_asia",
    "chiang mai": "southeast_asia", "koh samui": "southeast_asia",
    "kuala lumpur": "southeast_asia", "penang": "southeast_asia",
    "ho chi minh": "southeast_asia", "hanoi": "southeast_asia",
    "siem reap": "southeast_asia", "yangon": "southeast_asia",
    "manila": "southeast_asia", "boracay": "southeast_asia",
    "jakarta": "southeast_asia", "lombok": "southeast_asia",
    # Singapore / Hong Kong (expensive SE Asia)
    "singapore": "east_asia_expensive", "hong kong": "east_asia_expensive",
    # East Asia
    "tokyo": "east_asia", "osaka": "east_asia", "kyoto": "east_asia",
    "seoul": "east_asia", "busan": "east_asia", "taipei": "east_asia",
    "beijing": "east_asia", "shanghai": "east_asia", "guangzhou": "east_asia",
    # Middle East
    "dubai": "middle_east", "abu dhabi": "middle_east", "doha": "middle_east",
    "muscat": "middle_east", "riyadh": "middle_east", "kuwait": "middle_east",
    "beirut": "middle_east", "amman": "middle_east",
    # South Asia
    "kathmandu": "south_asia", "colombo": "south_asia", "dhaka": "south_asia",
    "pokhara": "south_asia", "thimphu": "south_asia",
    # Europe
    "paris": "europe_expensive", "london": "europe_expensive",
    "zurich": "europe_expensive", "amsterdam": "europe_expensive",
    "vienna": "europe_expensive", "stockholm": "europe_expensive",
    "oslo": "europe_expensive", "copenhagen": "europe_expensive",
    "rome": "europe_moderate", "barcelona": "europe_moderate",
    "madrid": "europe_moderate", "berlin": "europe_moderate",
    "prague": "europe_budget", "budapest": "europe_budget",
    "warsaw": "europe_budget", "krakow": "europe_budget",
    "lisbon": "europe_moderate", "athens": "europe_budget",
    "istanbul": "europe_budget",
    # North America
    "new york": "north_america", "los angeles": "north_america",
    "san francisco": "north_america", "chicago": "north_america",
    "las vegas": "north_america", "miami": "north_america",
    "toronto": "north_america", "vancouver": "north_america",
    # Australia / NZ
    "sydney": "australia", "melbourne": "australia", "brisbane": "australia",
    "auckland": "australia", "queenstown": "australia",
    # Africa
    "cairo": "africa", "nairobi": "africa", "cape town": "africa",
    "marrakech": "africa", "casablanca": "africa",
    # Maldives / Island Luxury
    "maldives": "luxury_island", "mauritius": "luxury_island",
    "seychelles": "luxury_island", "phuket": "southeast_asia",
}

# ── DAILY COST MATRIX (INR per person per day, excluding intercity transport)
# Activities are now destination-category-aware with realistic per-city values.
# Structure: category → travel_style → {accommodation, food, local_transport, activities, misc}
DEST_COST_MATRIX: Dict[str, Dict[str, Dict[str, int]]] = {
    "india_tier2": {
        "budget":   {"accommodation": 500,  "food": 250,  "local_transport": 120, "activities": 300,  "misc": 100},
        "moderate": {"accommodation": 1500, "food": 600,  "local_transport": 300, "activities": 700,  "misc": 250},
        "luxury":   {"accommodation": 4000, "food": 1400, "local_transport": 900, "activities": 1500, "misc": 600},
    },
    "india_tourist": {  # Jaipur, Agra, Udaipur, Goa — popular tourist circuits
        "budget":   {"accommodation": 600,  "food": 300,  "local_transport": 150, "activities": 500,  "misc": 120},
        "moderate": {"accommodation": 2000, "food": 700,  "local_transport": 400, "activities": 1200, "misc": 300},
        "luxury":   {"accommodation": 6000, "food": 1800, "local_transport": 1000,"activities": 2500, "misc": 700},
    },
    "india_hill": {  # Shimla, Manali, Ooty — adventure + nature activities
        "budget":   {"accommodation": 700,  "food": 300,  "local_transport": 180, "activities": 400,  "misc": 130},
        "moderate": {"accommodation": 2200, "food": 750,  "local_transport": 450, "activities": 1000, "misc": 300},
        "luxury":   {"accommodation": 7000, "food": 1800, "local_transport": 1200,"activities": 2000, "misc": 700},
    },
    "india_leisure": {  # Rishikesh, Varanasi, Amritsar
        "budget":   {"accommodation": 500,  "food": 250,  "local_transport": 120, "activities": 350,  "misc": 100},
        "moderate": {"accommodation": 1800, "food": 650,  "local_transport": 350, "activities": 800,  "misc": 250},
        "luxury":   {"accommodation": 5000, "food": 1500, "local_transport": 900, "activities": 1800, "misc": 600},
    },
    "india_metro": {  # Mumbai, Delhi, Bangalore
        "budget":   {"accommodation": 800,  "food": 400,  "local_transport": 200, "activities": 500,  "misc": 150},
        "moderate": {"accommodation": 2500, "food": 900,  "local_transport": 500, "activities": 1200, "misc": 350},
        "luxury":   {"accommodation": 8000, "food": 2200, "local_transport": 1500,"activities": 2500, "misc": 900},
    },
    "india_island": {  # Andaman — water sports, island hopping
        "budget":   {"accommodation": 1200, "food": 500,  "local_transport": 300, "activities": 1000, "misc": 200},
        "moderate": {"accommodation": 3500, "food": 1000, "local_transport": 600, "activities": 2000, "misc": 500},
        "luxury":   {"accommodation": 10000,"food": 2500, "local_transport": 1500,"activities": 4000, "misc": 1000},
    },
    "southeast_asia": {  # Bali, Bangkok, KL — temples, tours, nightlife
        "budget":   {"accommodation": 1200, "food": 600,  "local_transport": 400, "activities": 800,  "misc": 300},
        "moderate": {"accommodation": 4000, "food": 1500, "local_transport": 900, "activities": 2000, "misc": 700},
        "luxury":   {"accommodation": 12000,"food": 4000, "local_transport": 2500,"activities": 5000, "misc": 1800},
    },
    "east_asia_expensive": {  # Singapore, Hong Kong — expensive attractions
        "budget":   {"accommodation": 4000, "food": 1800, "local_transport": 800, "activities": 2500, "misc": 700},
        "moderate": {"accommodation": 10000,"food": 4000, "local_transport": 1500,"activities": 5000, "misc": 1500},
        "luxury":   {"accommodation": 25000,"food": 9000, "local_transport": 4000,"activities": 10000,"misc": 3500},
    },
    "east_asia": {  # Tokyo, Seoul, Taipei — culture, tech, anime parks
        "budget":   {"accommodation": 3000, "food": 1500, "local_transport": 700, "activities": 2000, "misc": 600},
        "moderate": {"accommodation": 8000, "food": 3500, "local_transport": 1500,"activities": 4500, "misc": 1200},
        "luxury":   {"accommodation": 20000,"food": 8000, "local_transport": 3500,"activities": 9000, "misc": 3000},
    },
    "middle_east": {  # Dubai, Abu Dhabi — paid attractions, desert safaris
        "budget":   {"accommodation": 4500, "food": 2000, "local_transport": 900, "activities": 2500, "misc": 700},
        "moderate": {"accommodation": 12000,"food": 4500, "local_transport": 2000,"activities": 6000, "misc": 1800},
        "luxury":   {"accommodation": 35000,"food": 11000,"local_transport": 6000,"activities": 12000,"misc": 5000},
    },
    "south_asia": {  # Nepal, Sri Lanka
        "budget":   {"accommodation": 800,  "food": 400,  "local_transport": 200, "activities": 600,  "misc": 200},
        "moderate": {"accommodation": 2500, "food": 1000, "local_transport": 600, "activities": 1500, "misc": 500},
        "luxury":   {"accommodation": 8000, "food": 2500, "local_transport": 2000,"activities": 3500, "misc": 1200},
    },
    "europe_budget": {  # Prague, Budapest, Istanbul, Athens
        "budget":   {"accommodation": 3500, "food": 1800, "local_transport": 700, "activities": 2500, "misc": 700},
        "moderate": {"accommodation": 9000, "food": 4000, "local_transport": 1500,"activities": 5000, "misc": 1500},
        "luxury":   {"accommodation": 22000,"food": 9000, "local_transport": 4000,"activities": 9000, "misc": 3000},
    },
    "europe_moderate": {  # Rome, Barcelona, Berlin, Madrid
        "budget":   {"accommodation": 5000, "food": 2500, "local_transport": 900, "activities": 3500, "misc": 900},
        "moderate": {"accommodation": 13000,"food": 5500, "local_transport": 2000,"activities": 7000, "misc": 2000},
        "luxury":   {"accommodation": 30000,"food": 12000,"local_transport": 5000,"activities": 12000,"misc": 4000},
    },
    "europe_expensive": {  # Paris, London, Zurich, Amsterdam
        "budget":   {"accommodation": 7000, "food": 3500, "local_transport": 1200,"activities": 4500, "misc": 1200},
        "moderate": {"accommodation": 18000,"food": 7500, "local_transport": 2500,"activities": 9000, "misc": 2500},
        "luxury":   {"accommodation": 45000,"food": 18000,"local_transport": 7000,"activities": 18000,"misc": 6000},
    },
    "north_america": {  # New York, LA, Toronto
        "budget":   {"accommodation": 6000, "food": 3000, "local_transport": 1000,"activities": 3500, "misc": 1000},
        "moderate": {"accommodation": 16000,"food": 7000, "local_transport": 2500,"activities": 8000, "misc": 2500},
        "luxury":   {"accommodation": 40000,"food": 16000,"local_transport": 7000,"activities": 15000,"misc": 6000},
    },
    "australia": {  # Sydney, Melbourne
        "budget":   {"accommodation": 5500, "food": 2800, "local_transport": 1000,"activities": 3000, "misc": 900},
        "moderate": {"accommodation": 14000,"food": 6500, "local_transport": 2500,"activities": 7000, "misc": 2200},
        "luxury":   {"accommodation": 35000,"food": 14000,"local_transport": 6000,"activities": 14000,"misc": 5000},
    },
    "africa": {  # Cairo, Cape Town, Nairobi — safaris expensive
        "budget":   {"accommodation": 2000, "food": 900,  "local_transport": 500, "activities": 2000, "misc": 500},
        "moderate": {"accommodation": 6000, "food": 2500, "local_transport": 1200,"activities": 4500, "misc": 1200},
        "luxury":   {"accommodation": 18000,"food": 6000, "local_transport": 4000,"activities": 10000,"misc": 3000},
    },
    "luxury_island": {  # Maldives, Mauritius, Seychelles
        "budget":   {"accommodation": 8000, "food": 3500, "local_transport": 1000,"activities": 4000, "misc": 1000},
        "moderate": {"accommodation": 20000,"food": 8000, "local_transport": 2500,"activities": 8000, "misc": 2500},
        "luxury":   {"accommodation": 60000,"food": 20000,"local_transport": 8000,"activities": 20000,"misc": 7000},
    },
}

# Ordered cheapest to most expensive for budget fallback
TIER_ORDER = ["budget", "moderate", "luxury"]

TIER_LABELS = {
    "budget":   "budget guesthouse / hostel",
    "moderate": "3-star hotel",
    "luxury":   "4-5 star hotel",
}


def _classify_destination(destination: str) -> str:
    """
    Classify a destination into a DEST_COST_MATRIX category.
    Also cross-checks against _detect_region for island/intl destinations
    that may not be in DEST_CATEGORY_MAP.
    """
    dest_lower = destination.lower().strip()

    # Primary: DEST_CATEGORY_MAP keyword match
    for keyword, category in DEST_CATEGORY_MAP.items():
        if keyword in dest_lower:
            print(f"[Budget] _classify_destination: '{destination}' → '{category}' (via DEST_CATEGORY_MAP)")
            return category

    # Secondary: use _detect_region to map transport region → cost category
    region = _detect_region(destination)
    region_to_category = {
        "island":              "india_island",
        "india":               "india_tier2",
        "south_asia":          "south_asia",
        "se_asia":             "southeast_asia",
        "east_asia_expensive": "east_asia_expensive",
        "east_asia":           "east_asia",
        "middle_east":         "middle_east",
        "europe":              "europe_moderate",
        "north_america":       "north_america",
        "australia":           "australia",
        "africa":              "africa",
    }
    category = region_to_category.get(region, "india_tier2")
    print(f"[Budget] _classify_destination: '{destination}' → '{category}' (via _detect_region={region})")
    return category


def _compute_trip_cost(
    category: str,
    tier: str,
    num_days: int,
    num_people: int,
    intercity_cost: float,
) -> Dict[str, Any]:
    """
    Compute a fully itemised trip cost for the given destination
    category and travel style tier.
    All daily costs scale per-person × days.
    Intercity transport is a fixed total (already per-group round-trip).
    """
    # Guard: category must exist in matrix
    if category not in DEST_COST_MATRIX:
        print(f"[Budget] WARNING: category '{category}' not in DEST_COST_MATRIX, falling back to 'india_tier2'")
        category = "india_tier2"

    matrix = DEST_COST_MATRIX[category]

    # Guard: tier must be budget/moderate/luxury
    valid_tiers = ("budget", "moderate", "luxury")
    if tier not in valid_tiers:
        print(f"[Budget] WARNING: tier '{tier}' not valid, falling back to 'budget'")
        tier = "budget"

    daily = matrix[tier]

    if num_days <= 0:
        raise ValueError(f"num_days must be > 0, got {num_days}")
    if num_people <= 0:
        raise ValueError(f"num_people must be > 0, got {num_people}")

    accommodation   = daily["accommodation"]   * num_days * num_people
    food            = daily["food"]            * num_days * num_people
    local_transport = daily["local_transport"] * num_days * num_people
    activities      = daily["activities"]      * num_days * num_people
    misc            = daily["misc"]            * num_days * num_people
    total_stay      = accommodation + food + local_transport + activities + misc
    total           = total_stay + intercity_cost

    print(
        f"[Budget] _compute_trip_cost | cat={category} tier={tier} "
        f"days={num_days} people={num_people} intercity=₹{intercity_cost:,.0f} | "
        f"accom=₹{accommodation:,.0f} food=₹{food:,.0f} "
        f"local_t=₹{local_transport:,.0f} act=₹{activities:,.0f} "
        f"misc=₹{misc:,.0f} → TOTAL=₹{total:,.0f}"
    )

    return {
        "tier": tier,
        "category": category,
        "total": round(total),
        "accommodation": round(accommodation),
        "food": round(food),
        "local_transport": round(local_transport),
        "intercity_transport": round(intercity_cost),
        "transport": round(intercity_cost + local_transport),
        "activities": round(activities),
        "misc": round(misc),
    }


# ---------------------------------------------------------------------------
# Transport Cost Engine — Distance + Mode + Route-Aware (no paid APIs)
# ---------------------------------------------------------------------------
# Strategy:
#   1. Compute distance using Haversine (already done before this is called)
#   2. Detect route type: domestic India / South Asia / SE Asia / long-haul intl
#   3. Per mode: use distance bands with realistic INR costs
#      Flight  → tiered by km + international surcharge by region
#      Train   → per-km rate capped by class; domestic only
#      Bus     → per-km rate; domestic / nearby only
#      Car/Cab → full cab hire or per-km rideshare
#      Ferry   → fixed by island type
# ---------------------------------------------------------------------------

# Region detection helpers — using substring matching, not exact set lookup
_ISLAND_KEYWORDS = [
    "andaman", "nicobar", "port blair", "lakshadweep", "bali", "maldives",
    "mauritius", "seychelles", "phuket", "koh samui", "male", "lombok",
    "boracay", "langkawi",
]

_INDIA_KEYWORDS = [
    "delhi", "mumbai", "bangalore", "bengaluru", "hyderabad", "chennai",
    "kolkata", "pune", "ahmedabad", "jaipur", "agra", "varanasi", "goa",
    "shimla", "manali", "darjeeling", "ooty", "munnar", "coorg", "rishikesh",
    "haridwar", "amritsar", "udaipur", "jodhpur", "jaisalmer", "kochi",
    "mysore", "madurai", "mussoorie", "nainital", "chandigarh", "surat",
    "indore", "bhopal", "nagpur", "lucknow", "patna", "ranchi", "bhubaneswar",
    "visakhapatnam", "vijayawada", "coimbatore", "trichy", "tiruchirappalli",
    "leh", "ladakh", "spiti", "mcleodganj", "dharamshala", "kullu",
]

_SOUTH_ASIA_KEYWORDS = [
    "kathmandu", "pokhara", "thimphu", "colombo", "dhaka", "islamabad",
    "karachi", "lahore", "kabul",
]

_SE_ASIA_KEYWORDS = [
    "bangkok", "kuala lumpur", "penang", "ho chi minh", "hanoi",
    "siem reap", "yangon", "manila", "jakarta", "chiang mai",
]

_EAST_ASIA_EXPENSIVE_KEYWORDS = ["singapore", "hong kong"]

_EAST_ASIA_KEYWORDS = [
    "tokyo", "osaka", "kyoto", "seoul", "busan", "beijing",
    "shanghai", "guangzhou", "taipei",
]

_MIDDLE_EAST_KEYWORDS = [
    "dubai", "abu dhabi", "doha", "muscat", "riyadh",
    "kuwait", "amman", "beirut", "jeddah", "sharjah",
]

_EUROPE_KEYWORDS = [
    "paris", "london", "rome", "barcelona", "madrid", "berlin", "amsterdam",
    "vienna", "prague", "budapest", "lisbon", "athens", "istanbul", "zurich",
    "stockholm", "oslo", "copenhagen", "warsaw", "krakow", "brussels",
    "milan", "florence", "nice", "geneva", "edinburgh", "dublin",
]

_NORTH_AMERICA_KEYWORDS = [
    "new york", "los angeles", "chicago", "miami", "toronto", "vancouver",
    "san francisco", "las vegas", "montreal", "seattle", "boston", "new york",
]

_AUSTRALIA_KEYWORDS = ["sydney", "melbourne", "brisbane", "perth", "auckland", "queenstown"]

_AFRICA_KEYWORDS = ["cairo", "nairobi", "cape town", "marrakech", "casablanca", "lagos"]

_LUXURY_ISLAND_KEYWORDS = ["maldives", "mauritius", "seychelles"]


def _detect_region(city: str) -> str:
    """Classify a city into a transport/cost region using substring matching."""
    c = city.lower().strip()
    # Islands checked first — they always need flight/ferry regardless of region
    if any(k in c for k in _ISLAND_KEYWORDS):         return "island"
    if any(k in c for k in _LUXURY_ISLAND_KEYWORDS):  return "island"
    if any(k in c for k in _INDIA_KEYWORDS):          return "india"
    if any(k in c for k in _SOUTH_ASIA_KEYWORDS):     return "south_asia"
    if any(k in c for k in _EAST_ASIA_EXPENSIVE_KEYWORDS): return "east_asia_expensive"
    if any(k in c for k in _SE_ASIA_KEYWORDS):        return "se_asia"
    if any(k in c for k in _EAST_ASIA_KEYWORDS):      return "east_asia"
    if any(k in c for k in _MIDDLE_EAST_KEYWORDS):    return "middle_east"
    if any(k in c for k in _EUROPE_KEYWORDS):         return "europe"
    if any(k in c for k in _NORTH_AMERICA_KEYWORDS):  return "north_america"
    if any(k in c for k in _AUSTRALIA_KEYWORDS):      return "australia"
    if any(k in c for k in _AFRICA_KEYWORDS):         return "africa"
    # Heuristic: if name ends in Indian city suffixes, treat as India
    indian_suffixes = ("pur", "bad", "nagar", "puram", "ganj", "garh", "abad", "giri")
    if c.endswith(indian_suffixes):                   return "india"
    return "india"   # safe default for unknown


def _is_island_dest(destination: str) -> bool:
    d = destination.lower()
    return any(k in d for k in _ISLAND_KEYWORDS + _LUXURY_ISLAND_KEYWORDS)


def _road_connection_exists(origin_region: str, dest_region: str, dest: str) -> bool:
    """
    Returns True only when a continuous road connection is geographically possible.
    Islands and international destinations (except Nepal/Bhutan by road) have no road link.
    """
    if dest_region == "island":
        return False
    if origin_region == "island":
        return False
    # International pairs that have no road link from India
    no_road_pairs = {
        ("india", "se_asia"), ("india", "east_asia"), ("india", "east_asia_expensive"),
        ("india", "middle_east"), ("india", "europe"), ("india", "north_america"),
        ("india", "australia"), ("india", "africa"),
    }
    pair = (origin_region, dest_region)
    rev  = (dest_region, origin_region)
    if pair in no_road_pairs or rev in no_road_pairs:
        return False
    return True


_AIRPORT_CITIES = {
    "delhi", "new delhi", "mumbai", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata",
    "pune", "ahmedabad", "jaipur", "goa", "kochi", "thiruvananthapuram", "dehradun", "rishikesh",
    "haridwar", "srinagar", "leh", "ladakh", "amritsar", "chandigarh", "lucknow", "bhopal",
    "indore", "nagpur", "surat", "coimbatore", "madurai", "mysore", "mysuru", "ooty", "kodaikanal",
    "pondicherry", "tirupati", "guwahati", "shillong", "port blair", "andaman", "udaipur",
    "jodhpur", "jaisalmer", "darjeeling", "gangtok", "sikkim", "agra", "varanasi", "bhubaneswar",
    "khajuraho"
}

_REMOTE_DESTINATIONS = {
    "leh", "ladakh", "srinagar", "port blair", "andaman", "sikkim", "gangtok", "darjeeling",
    "shillong", "dharamshala"
}

_METRO_CITIES = {
    "delhi", "new delhi", "mumbai", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata"
}

# ── Airline route coverage ─────────────────────────────────────────────────
# Which airlines fly which domestic Indian routes (city-pair based).
# Format: frozenset({city_a, city_b}) → [airline_names]
# Covers the most common tourist routes.
_AIRLINE_ROUTE_MAP: Dict[frozenset, List[str]] = {
    # Delhi ↔ others
    frozenset({"delhi", "mumbai"}):           ["IndiGo", "Air India", "SpiceJet", "Vistara", "Go First"],
    frozenset({"delhi", "bangalore"}):        ["IndiGo", "Air India", "SpiceJet", "Vistara"],
    frozenset({"delhi", "bengaluru"}):        ["IndiGo", "Air India", "SpiceJet", "Vistara"],
    frozenset({"delhi", "hyderabad"}):        ["IndiGo", "Air India", "SpiceJet"],
    frozenset({"delhi", "chennai"}):          ["IndiGo", "Air India", "SpiceJet"],
    frozenset({"delhi", "kolkata"}):          ["IndiGo", "Air India", "SpiceJet", "Vistara"],
    frozenset({"delhi", "goa"}):              ["IndiGo", "SpiceJet", "Air India", "Go First"],
    frozenset({"delhi", "leh"}):              ["IndiGo", "Air India", "SpiceJet"],
    frozenset({"delhi", "ladakh"}):           ["IndiGo", "Air India", "SpiceJet"],
    frozenset({"delhi", "srinagar"}):         ["IndiGo", "SpiceJet", "Air India"],
    frozenset({"delhi", "jaipur"}):           ["IndiGo", "SpiceJet"],
    frozenset({"delhi", "amritsar"}):         ["IndiGo", "SpiceJet", "Air India"],
    frozenset({"delhi", "chandigarh"}):       ["IndiGo", "SpiceJet"],
    frozenset({"delhi", "lucknow"}):          ["IndiGo", "SpiceJet", "Air India"],
    frozenset({"delhi", "varanasi"}):         ["IndiGo", "SpiceJet", "Air India"],
    frozenset({"delhi", "kochi"}):            ["IndiGo", "Air India"],
    frozenset({"delhi", "port blair"}):       ["IndiGo", "Air India"],
    frozenset({"delhi", "andaman"}):          ["IndiGo", "Air India"],
    frozenset({"delhi", "udaipur"}):          ["IndiGo", "SpiceJet"],
    frozenset({"delhi", "dehradun"}):         ["IndiGo", "SpiceJet"],
    # Mumbai ↔ others
    frozenset({"mumbai", "bangalore"}):       ["IndiGo", "Air India", "SpiceJet", "Vistara"],
    frozenset({"mumbai", "bengaluru"}):       ["IndiGo", "Air India", "SpiceJet", "Vistara"],
    frozenset({"mumbai", "goa"}):             ["IndiGo", "SpiceJet", "Go First"],
    frozenset({"mumbai", "hyderabad"}):       ["IndiGo", "SpiceJet", "Air India"],
    frozenset({"mumbai", "chennai"}):         ["IndiGo", "SpiceJet", "Air India"],
    frozenset({"mumbai", "kolkata"}):         ["IndiGo", "Air India", "SpiceJet"],
    frozenset({"mumbai", "kochi"}):           ["IndiGo", "SpiceJet", "Air India"],
    frozenset({"mumbai", "leh"}):             ["Air India"],
    frozenset({"mumbai", "srinagar"}):        ["IndiGo", "Air India"],
    frozenset({"mumbai", "port blair"}):      ["Air India"],
    frozenset({"mumbai", "andaman"}):         ["Air India"],
    # Bangalore ↔ others
    frozenset({"bangalore", "hyderabad"}):    ["IndiGo", "SpiceJet"],
    frozenset({"bangalore", "bengaluru"}):    [],
    frozenset({"bengaluru", "hyderabad"}):    ["IndiGo", "SpiceJet"],
    frozenset({"bangalore", "goa"}):          ["IndiGo", "SpiceJet"],
    frozenset({"bengaluru", "goa"}):          ["IndiGo", "SpiceJet"],
    frozenset({"bangalore", "kochi"}):        ["IndiGo", "Air India"],
    frozenset({"bengaluru", "kochi"}):        ["IndiGo", "Air India"],
    frozenset({"bangalore", "chennai"}):      ["IndiGo", "SpiceJet"],
    frozenset({"bengaluru", "chennai"}):      ["IndiGo", "SpiceJet"],
    # Chennai ↔ others
    frozenset({"chennai", "kolkata"}):        ["IndiGo", "Air India"],
    frozenset({"chennai", "kochi"}):          ["IndiGo", "SpiceJet"],
    frozenset({"chennai", "port blair"}):     ["IndiGo", "Air India"],
    frozenset({"chennai", "andaman"}):        ["IndiGo", "Air India"],
    frozenset({"chennai", "goa"}):            ["IndiGo", "SpiceJet"],
    # International (just top airlines)
    frozenset({"india", "dubai"}):            ["Air India", "IndiGo", "Emirates", "flydubai"],
    frozenset({"india", "singapore"}):        ["Air India", "IndiGo", "Singapore Airlines"],
    frozenset({"india", "bangkok"}):          ["Air India", "IndiGo", "Thai Airways"],
    frozenset({"india", "london"}):           ["Air India", "British Airways", "Virgin Atlantic"],
    frozenset({"india", "new york"}):         ["Air India", "United Airlines", "Delta"],
}

# Airline-specific fare multipliers relative to the base fare range
# 1.0 = base, <1 = budget carrier, >1 = premium
_AIRLINE_FARE_MULTIPLIERS = {
    "IndiGo":            (0.80, 1.10),   # budget, frequent promotions
    "SpiceJet":          (0.80, 1.15),   # budget
    "Go First":          (0.85, 1.10),   # budget
    "Air India":         (1.00, 1.40),   # full-service flag carrier
    "Vistara":           (1.10, 1.50),   # premium economy
    "Air India Express": (0.85, 1.15),   # budget subsidiary
    "Emirates":          (1.30, 2.20),
    "Singapore Airlines":(1.40, 2.50),
    "Thai Airways":      (1.20, 2.00),
    "British Airways":   (1.50, 2.60),
    "Virgin Atlantic":   (1.40, 2.40),
    "United Airlines":   (1.30, 2.50),
    "Delta":             (1.30, 2.50),
    "flydubai":          (0.90, 1.30),
}

def _get_airlines_for_route(origin: str, destination: str) -> List[str]:
    """Return list of airlines that operate between origin and destination."""
    o = origin.lower().strip()
    d = destination.lower().strip()

    # Exact city-pair match
    key = frozenset({o, d})
    if key in _AIRLINE_ROUTE_MAP:
        return _AIRLINE_ROUTE_MAP[key]

    # Partial match — check if any key's cities are substrings
    for route_key, airlines in _AIRLINE_ROUTE_MAP.items():
        cities = list(route_key)
        if (any(c in o for c in cities) and any(c in d for c in [c for c in cities if c not in o])):
            return airlines

    # Default domestic fallback
    if _has_airport(origin) and _has_airport(destination):
        return ["IndiGo", "SpiceJet", "Air India"]

    return []


def _get_airline_fares(
    origin: str,
    destination: str,
    base_lo: int,
    base_hi: int,
) -> List[Dict[str, Any]]:
    """
    Returns per-airline estimated fare entries for a route.
    Each entry: airline, logo_hint, fare_min, fare_max, fare_label, note
    """
    airlines = _get_airlines_for_route(origin, destination)
    if not airlines:
        return []

    results = []
    for airline in airlines:
        lo_mult, hi_mult = _AIRLINE_FARE_MULTIPLIERS.get(airline, (1.0, 1.4))
        fare_lo = max(1500, round(base_lo * lo_mult / 100) * 100)   # round to ₹100
        fare_hi = max(fare_lo + 500, round(base_hi * hi_mult / 100) * 100)

        # Budget vs premium label
        if lo_mult < 0.90:
            note = "Budget carrier · frequent sales"
        elif lo_mult > 1.10:
            note = "Full-service · meals included"
        else:
            note = "Standard fare"

        results.append({
            "airline":    airline,
            "fare_min":   fare_lo,
            "fare_max":   fare_hi,
            "fare_label": f"₹{fare_lo:,}–₹{fare_hi:,}",
            "note":       note,
        })

    # Sort cheapest first
    results.sort(key=lambda x: x["fare_min"])
    return results

def _has_airport(city_name: str) -> bool:
    c = city_name.lower().strip()
    return any(ac in c for ac in _AIRPORT_CITIES)

def _estimate_flight_cost_pp(
    distance_km: float,
    origin: str,
    destination: str,
    origin_region: str,
    dest_region: str
) -> Tuple[int, int]:
    """
    Returns (min_fare, max_fare) one-way per person in INR.
    Domestic India: based on real route distance bands + remote surcharges / metro discounts.
    International: based on region pairs.
    """
    if origin_region == "india" and dest_region == "india":
        # Base domestic pricing by distance
        if distance_km < 500:
            lo, hi = (2500, 5500)
        elif distance_km < 1000:
            lo, hi = (3000, 7000)
        elif distance_km < 1500:
            lo, hi = (3800, 8500)
        elif distance_km < 2500:
            lo, hi = (4500, 10500)
        else:
            lo, hi = (5500, 13000)

        # Trunk route discount (e.g. Delhi-Mumbai, Mumbai-Bangalore)
        o_clean = origin.lower().strip()
        d_clean = destination.lower().strip()
        is_o_metro = any(m in o_clean for m in _METRO_CITIES)
        is_d_metro = any(m in d_clean for m in _METRO_CITIES)
        if is_o_metro and is_d_metro:
            lo = max(2500, lo - 1300)
            hi = max(5000, hi - 1500)

        # Remote / Mountain / Island surcharge (e.g. Leh, Srinagar, Port Blair)
        is_d_remote = any(r in d_clean for r in _REMOTE_DESTINATIONS)
        is_o_remote = any(r in o_clean for r in _REMOTE_DESTINATIONS)
        if is_d_remote or is_o_remote:
            lo += 500
            hi += 2000
            # Special case for Leh and Port Blair which are highly expensive
            if "leh" in d_clean or "leh" in o_clean or "blair" in d_clean or "blair" in o_clean or "andaman" in d_clean or "andaman" in o_clean:
                hi = max(9000, hi)

        return (int(lo), int(hi))

    if origin_region == "india" and dest_region == "island":
        return (4500, 10000)   # Chennai/Kolkata → Port Blair

    INTL_FARES: Dict[str, Tuple[int, int]] = {
        "south_asia":          (4000,  9000),
        "se_asia":             (7000, 18000),
        "east_asia_expensive": (10000,22000),
        "east_asia":           (12000,28000),
        "middle_east":         (9000, 22000),
        "europe":              (28000,65000),
        "north_america":       (45000,90000),
        "australia":           (35000,75000),
        "africa":              (22000,55000),
        "island":              (10000,25000),
    }
    intl_region = dest_region if origin_region == "india" else origin_region
    lo, hi = INTL_FARES.get(intl_region, (15000, 40000))
    if distance_km > 8000:
        lo, hi = int(lo * 1.30), int(hi * 1.30)
    elif distance_km > 5000:
        lo, hi = int(lo * 1.12), int(hi * 1.12)
    return (lo, hi)


def _estimate_train_options(distance_km: float, origin_region: str, dest_region: str) -> List[Dict]:
    """
    Returns list of train class options with realistic fares.
    Based on Indian Railways distance-slab fares (2024 rates).
    Fares are marked as estimates with min/max ranges.
    """
    if not _road_connection_exists(origin_region, dest_region, ""):
        return []
    if origin_region not in ("india",):
        return []
    if distance_km > 2800:
        return []

    # Realistic duration: Express trains average ~70 km/h
    duration_h = round(distance_km / 70.0, 1)

    # ── Indian Railways realistic base fares by distance slab ────────────
    # Based on actual Rajdhani/Shatabdi/Express published fares (2024)
    if distance_km <= 100:
        sl_range   = (120,  220)
        cc_range   = (250,  450)
        ec_range   = (550,  900)
        ac3_range  = (350,  600)
        ac2_range  = (550,  900)
    elif distance_km <= 200:
        sl_range   = (200,  380)
        cc_range   = (380,  650)
        ec_range   = (800,  1300)
        ac3_range  = (550,  900)
        ac2_range  = (900,  1400)
    elif distance_km <= 350:
        # Dehradun→Delhi class: 280km
        # Real Shatabdi CC: ~₹580–₹900, EC: ~₹1200–₹1800
        # Real Sleeper: ~₹220–₹320
        sl_range   = (220,  380)
        cc_range   = (550,  950)
        ec_range   = (1200, 1900)
        ac3_range  = (700,  1100)
        ac2_range  = (1100, 1700)
    elif distance_km <= 600:
        sl_range   = (350,  600)
        cc_range   = (750,  1200)
        ec_range   = (1500, 2500)
        ac3_range  = (950,  1500)
        ac2_range  = (1500, 2300)
    elif distance_km <= 1000:
        sl_range   = (500,  850)
        cc_range   = (950,  1500)
        ec_range   = (1900, 3000)
        ac3_range  = (1300, 2000)
        ac2_range  = (2000, 3000)
    elif distance_km <= 1500:
        sl_range   = (700,  1200)
        cc_range   = (1200, 1900)
        ec_range   = (2400, 3800)
        ac3_range  = (1700, 2700)
        ac2_range  = (2700, 4000)
    else:
        sl_range   = (1000, 1800)
        cc_range   = (1600, 2600)
        ec_range   = (3200, 5000)
        ac3_range  = (2200, 3500)
        ac2_range  = (3500, 5500)

    classes = []

    # Sleeper (SL) — available for routes > 80km
    if distance_km > 80:
        classes.append({
            "class":           "Sleeper (SL)",
            "fare_min":        sl_range[0],
            "fare_max":        sl_range[1],
            "cost_per_person": sl_range[0],
            "recommended":     False,
            "note":            "Non-AC sleeper berths. Budget option. Book 2+ weeks ahead on IRCTC.",
            "duration":        f"{duration_h} hrs",
        })

    # Chair Car (CC) — day trains (Shatabdi/Jan Shatabdi), ≤700km
    if distance_km <= 700:
        classes.append({
            "class":           "Chair Car (CC)",
            "fare_min":        cc_range[0],
            "fare_max":        cc_range[1],
            "cost_per_person": cc_range[0],
            "recommended":     distance_km <= 350,
            "note":            "AC seater. Shatabdi/Jan Shatabdi. Fast, comfortable for day travel.",
            "duration":        f"{duration_h} hrs",
        })

        # Executive Chair Car (EC) — Shatabdi/Vande Bharat premium
        classes.append({
            "class":           "Executive Chair Car (EC)",
            "fare_min":        ec_range[0],
            "fare_max":        ec_range[1],
            "cost_per_person": ec_range[0],
            "recommended":     False,
            "note":            "Premium AC seating. Vande Bharat / Shatabdi Executive. Meals included.",
            "duration":        f"{duration_h} hrs",
        })

    # 3A (AC 3-Tier) — overnight routes > 150km
    if distance_km > 150:
        classes.append({
            "class":           "3A (AC 3-Tier)",
            "fare_min":        ac3_range[0],
            "fare_max":        ac3_range[1],
            "cost_per_person": ac3_range[0],
            "recommended":     350 < distance_km <= 800,
            "note":            "AC 3-tier sleeper. Standard overnight option. Book IRCTC.",
            "duration":        f"{duration_h} hrs",
        })

    # 2A (AC 2-Tier) — overnight routes > 250km
    if distance_km > 250:
        classes.append({
            "class":           "2A (AC 2-Tier)",
            "fare_min":        ac2_range[0],
            "fare_max":        ac2_range[1],
            "cost_per_person": ac2_range[0],
            "recommended":     distance_km > 800,
            "note":            "Premium AC 2-tier sleeper. More privacy and wider berths.",
            "duration":        f"{duration_h} hrs",
        })

    # Ensure at least one class is recommended
    if classes and not any(c["recommended"] for c in classes):
        classes[0]["recommended"] = True

    return classes


def _estimate_bus_options(distance_km: float, origin_region: str, dest_region: str) -> List[Dict]:
    """
    Returns bus options with realistic Indian bus fares.
    Uses real-world calibrated per-km fares with hard minimum floors.
    Prices clearly marked as estimates.
    """
    if not _road_connection_exists(origin_region, dest_region, ""):
        return []
    if origin_region != "india":
        return []
    if distance_km > 750:
        return []

    # Realistic road speed in India: 48 km/h average (includes stops)
    duration_h = round(distance_km / 48.0, 1)
    options = []

    # ── Calibrated fare ranges per distance slab ─────────────────────────
    # Based on real RSRTC/HRTC/UPSRTC/private operator fares (2024)
    if distance_km <= 80:
        ord_range  = (100,  180)
        vol_range  = (200,  380)
        sl_range   = None
    elif distance_km <= 150:
        ord_range  = (160,  280)
        vol_range  = (350,  600)
        sl_range   = None
    elif distance_km <= 250:
        # Mussoorie→Shimla class: ~220km
        ord_range  = (250,  420)
        vol_range  = (550,  900)
        sl_range   = (700,  1100)
    elif distance_km <= 350:
        # Dehradun→Delhi class: ~280km
        # Real Volvo: ₹650–₹1200, Ordinary: ₹350–₹600
        ord_range  = (350,  600)
        vol_range  = (650,  1200)
        sl_range   = (850,  1400)
    elif distance_km <= 500:
        ord_range  = (500,  850)
        vol_range  = (900,  1600)
        sl_range   = (1200, 2000)
    elif distance_km <= 750:
        ord_range  = (700,  1200)
        vol_range  = (1300, 2200)
        sl_range   = (1700, 2800)
    else:
        ord_range  = (1000, 1700)
        vol_range  = (1800, 3000)
        sl_range   = (2200, 3500)

    # 1. Ordinary / Non-AC State Bus
    options.append({
        "class":           "Ordinary Bus (Non-AC)",
        "fare_min":        ord_range[0],
        "fare_max":        ord_range[1],
        "cost_per_person": ord_range[0],
        "recommended":     False,
        "note":            "State transport (RSRTC/HRTC/UPSRTC). Non-AC. Budget option.",
        "booking_link":    "https://www.redbus.in/",
        "duration":        f"{duration_h} hrs",
    })

    # 2. Volvo AC / Semi-Sleeper
    if distance_km >= 40:
        options.append({
            "class":           "Volvo AC / Semi-Sleeper",
            "fare_min":        vol_range[0],
            "fare_max":        vol_range[1],
            "cost_per_person": vol_range[0],
            "recommended":     60 <= distance_km <= 400,
            "note":            "Private operator Volvo AC. Comfortable seater. Recommended for day travel.",
            "booking_link":    "https://www.redbus.in/",
            "duration":        f"{duration_h} hrs",
        })

    # 3. AC Sleeper Bus — only for routes where sleeper makes sense
    if distance_km >= 200 and sl_range:
        options.append({
            "class":           "AC Sleeper Bus",
            "fare_min":        sl_range[0],
            "fare_max":        sl_range[1],
            "cost_per_person": sl_range[0],
            "recommended":     distance_km > 400,
            "note":            "AC Sleeper with berths. Best for overnight intercity journeys.",
            "booking_link":    "https://www.redbus.in/",
            "duration":        f"{duration_h} hrs",
        })

    return options


def _is_hilly(destination: str) -> bool:
    d = destination.lower()
    _hilly_dests = {
        "manali", "shimla", "dharamshala", "leh", "ladakh", "srinagar", "mussoorie", "nainital",
        "ooty", "munnar", "darjeeling", "gangtok", "sikkim", "kodaikanal"
    }
    return any(h in d for h in _hilly_dests)


def _estimate_taxi_option(
    distance_km: float,
    num_people: int,
    num_days: int,
    destination: str,
    origin_region: str,
    dest_region: str,
) -> Optional[Dict]:
    if not _road_connection_exists(origin_region, dest_region, ""):
        return None
    if origin_region != "india":
        return None
    if distance_km > 800:
        return None

    is_mountain = _is_hilly(destination)
    driver_days = max(1, num_days)

    # Billed distance rule: outstation cabs charge minimum 250 km per day round trip
    billed_distance = max(distance_km * 2.0, 250.0 * driver_days)

    # Rates for classes
    rates = {
        "Hatchback (AC WagonR / Celerio)": 12.0 if not is_mountain else 15.0,
        "Sedan (AC Dzire / Etios)": 14.0 if not is_mountain else 18.0,
        "SUV (AC Innova / Ertiga)": 18.0 if not is_mountain else 22.0
    }

    driver_charge_daily = 500.0
    driver_total = driver_charge_daily * driver_days

    # Tolls & State Border Taxes: ~Rs.1.5 per km actual one-way road distance (round trip tolls)
    tolls_total = int(distance_km * 2.0 * 1.5)

    classes = []
    for cls_name, rate in rates.items():
        base_running = billed_distance * rate
        total_fare = int(base_running + driver_total + tolls_total)
        per_person = round(total_fare / max(num_people, 1))
        classes.append({
            "class":           cls_name,
            "fare_min":        round(total_fare * 0.95),
            "fare_max":        round(total_fare * 1.15),
            "cost_per_person": per_person,
            "note":            f"Rate: Rs.{rate}/km · Min 250km/day billed.",
        })

    # Main display class will be AC Sedan (the middle one)
    main_class = classes[1] # Sedan
    total_vehicle = int((billed_distance * 14.0 if not is_mountain else billed_distance * 18.0) + driver_total + tolls_total)
    main_pp = round(total_vehicle / max(num_people, 1))

    # Average speed in India: 50 km/h on plains, 30 km/h in hills
    avg_speed = 30.0 if is_mountain else 50.0
    duration_h = round(distance_km / avg_speed, 1)

    return {
        "mode":            "Taxi / Cab",
        "emoji":           "🚕",
        "duration":        f"{duration_h} hrs",
        "fare_min":        main_class["fare_min"],
        "fare_max":        main_class["fare_max"],
        "fare_label":      f"₹{main_pp:,}/person (total ₹{total_vehicle:,})",
        "cost_per_person": main_pp,
        "cost_total":      total_vehicle,
        "available":       True,
        "recommended":     False,
        "tip":             f"Total vehicle: ₹{total_vehicle:,} round trip · Includes tolls (Rs.{tolls_total:,}) & driver allowance.",
        "booking_link":    "https://www.makemytrip.com/cabs/",
        "classes":         classes
    }


def _estimate_self_drive_option(
    distance_km: float,
    num_people: int,
    num_days: int,
    destination: str,
    origin_region: str,
    dest_region: str,
) -> Optional[Dict]:
    if not _road_connection_exists(origin_region, dest_region, ""):
        return None
    if origin_region != "india":
        return None
    if distance_km > 800:
        return None

    is_mountain = _is_hilly(destination)
    driver_days = max(1, num_days)

    # 1. Fuel Cost: 13 km/l average mileage, petrol price ~Rs.100/liter in India
    fuel_l = round((distance_km * 2.0) / 13.0, 1)
    fuel_total = int(fuel_l * 100)

    # 2. Toll Cost: ~Rs.1.5/km of actual driving distance
    toll_total = int(distance_km * 2.0 * 1.5)

    # 3. Parking / Local Entry charges: Rs.150/day
    parking_total = int(150 * driver_days)

    # Total self-drive driving cost
    total_driving_cost = fuel_total + toll_total + parking_total
    sd_pp = round(total_driving_cost / max(num_people, 1))

    # Classes: Itemised breakdown of costs
    classes = [
        {
            "class": "Fuel Cost",
            "fare_min": round(fuel_total * 0.95),
            "fare_max": round(fuel_total * 1.05),
            "cost_per_person": round(fuel_total / max(num_people, 1)),
            "note": f"Estimated fuel consumption: ~{fuel_l}L at Rs.100/L.",
        },
        {
            "class": "Toll Cost",
            "fare_min": toll_total,
            "fare_max": toll_total,
            "cost_per_person": round(toll_total / max(num_people, 1)),
            "note": f"Round trip national toll highway charges.",
        },
        {
            "class": "Parking & Permit Charges",
            "fare_min": parking_total,
            "fare_max": parking_total,
            "cost_per_person": round(parking_total / max(num_people, 1)),
            "note": f"Hotel & sightseeing parking fees (Rs.150/day).",
        }
    ]

    avg_speed = 30.0 if is_mountain else 50.0
    duration_h = round(distance_km / avg_speed, 1)

    return {
        "mode":            "Self-Drive",
        "emoji":           "🚗",
        "duration":        f"{duration_h} hrs",
        "fare_min":        round(total_driving_cost * 0.95),
        "fare_max":        round(total_driving_cost * 1.05),
        "fare_label":      f"₹{sd_pp:,}/person (total ₹{total_driving_cost:,})",
        "cost_per_person": sd_pp,
        "cost_total":      total_driving_cost,
        "available":       True,
        "recommended":     False,
        "tip":             f"Fuel: ₹{fuel_total:,} · Tolls: ₹{toll_total:,} · Parking: ₹{parking_total:,}",
        "booking_link":    "https://www.zoomcar.com/",
        "classes":         classes
    }


def _best_mode_recommendation(distance_km: float) -> str:
    """
    Choose the 'Best' transport mode based on distance and comfort.
    <250 km   → Car or Bus
    250–600   → Train preferred
    600–1000  → Train or Flight
    1000+     → Flight preferred
    """
    if distance_km < 250:   return "Car / Bus"
    if distance_km < 600:   return "Train"
    if distance_km < 1000:  return "Train / Flight"
    return "Flight"


def get_transport_options(
    origin: str,
    destination: str,
    distance_km: float,
    num_people: int,
    num_days: int = 2,
    preferred: str = None,
) -> List[Dict[str, Any]]:
    """
    Returns all realistically available intercity transport options for a route.

    Each option contains:
      mode, subtype, provider/operator hints, duration,
      fare_min, fare_max, estimated_fare, currency, source, destination,
      price_source (always "Estimated"), cost_per_person, cost_total,
      recommended, tip, booking_link, classes (for train/bus),
      airlines (for flight).

    Sorted from lowest estimated cost to highest.
    """
    orig_region = _detect_region(origin)
    dest_region = _detect_region(destination)
    is_island   = _is_island_dest(destination)
    is_intl     = orig_region != dest_region
    best_mode   = _best_mode_recommendation(distance_km)

    options: List[Dict[str, Any]] = []

    def _base_fields(mode, emoji, duration, fare_min, fare_max,
                     cost_per_person, cost_total, recommended, tip, booking_link,
                     subtype="", classes=None, airlines=None):
        """Build a consistent option dict with all required fields."""
        return {
            "mode":            mode,
            "subtype":         subtype,
            "emoji":           emoji,
            "duration":        duration,
            "fare_min":        fare_min,
            "fare_max":        fare_max,
            "estimated_fare":  fare_min,          # lowest realistic estimate
            "fare_label":      f"₹{fare_min:,}–₹{fare_max:,}",
            "currency":        "INR",
            "price_source":    "Estimated",        # always honest — no live API
            "source":          origin,
            "destination":     destination,
            "cost_per_person": cost_per_person,
            "cost_total":      cost_total,
            "available":       True,
            "recommended":     recommended,
            "tip":             tip,
            "booking_link":    booking_link,
            "classes":         classes or [],
            "airlines":        airlines or [],
        }

    # ── FLIGHT ───────────────────────────────────────────────────────────────
    has_orig_airport = _has_airport(origin)  or orig_region != "india"
    has_dest_airport = _has_airport(destination) or dest_region != "india"
    show_flight = (has_orig_airport and has_dest_airport and distance_km >= 180) or is_island or is_intl

    if show_flight:
        fl_min, fl_max = _estimate_flight_cost_pp(
            distance_km, origin, destination, orig_region, dest_region)
        dur_h = round(distance_km / 700 + 1.5, 1)
        if distance_km > 10000:
            dur_h = round(distance_km / 900 + 1.5, 1)

        is_recommended = "Flight" in best_mode or is_island or is_intl or distance_km > 900
        tip = ("Fly to Port Blair — IndiGo, Air India, SpiceJet."
               if is_island else
               "Book 4–6 weeks ahead for cheapest fares. Prices are estimates.")

        airline_fares = _get_airline_fares(origin, destination, fl_min, fl_max)
        o_enc = origin.replace(" ", "+")
        d_enc = destination.replace(" ", "+")
        gf_url = f"https://www.google.com/travel/flights?q=flights+from+{o_enc}+to+{d_enc}"

        options.append(_base_fields(
            mode="Flight", subtype="Economy", emoji="✈️",
            duration=f"{dur_h} hrs (inc. airport time)",
            fare_min=fl_min, fare_max=fl_max,
            cost_per_person=fl_min, cost_total=fl_min * num_people * 2,
            recommended=is_recommended, tip=tip, booking_link=gf_url,
            classes=[{"class": "Economy", "fare_min": fl_min, "fare_max": fl_max}],
            airlines=airline_fares,
        ))

    # ── SHIP (Indian islands) ─────────────────────────────────────────────────
    if is_island and orig_region == "india":
        ship_pp = _estimate_ship_cost_pp(destination, num_people)
        options.append(_base_fields(
            mode="Ship / Cruise", subtype="Economy Cabin", emoji="🚢",
            duration="56–64 hrs (2–3 day journey)",
            fare_min=ship_pp, fare_max=ship_pp + 1500,
            cost_per_person=ship_pp, cost_total=ship_pp * num_people * 2,
            recommended=False,
            tip="Scenic but very slow. Book via Shipping Corporation of India website.",
            booking_link="https://www.shipindia.com/",
        ))

    # ── TRAIN ────────────────────────────────────────────────────────────────
    train_classes = _estimate_train_options(distance_km, orig_region, dest_region)
    if train_classes:
        rec_class = next((c for c in train_classes if c["recommended"]), train_classes[0])
        options.append(_base_fields(
            mode="Train", subtype=rec_class["class"], emoji="🚂",
            duration=rec_class["duration"],
            fare_min=rec_class["fare_min"], fare_max=rec_class["fare_max"],
            cost_per_person=rec_class["fare_min"],
            cost_total=rec_class["fare_min"] * num_people * 2,
            recommended="Train" in best_mode,
            tip=f"{rec_class.get('note','')} · Fares are estimates; book on IRCTC for exact prices.",
            booking_link="https://www.irctc.co.in/",
            classes=train_classes,
        ))

    # ── BUS ──────────────────────────────────────────────────────────────────
    bus_classes = _estimate_bus_options(distance_km, orig_region, dest_region)
    if bus_classes:
        rec_bus = next(
            (b for b in bus_classes if "Volvo" in b["class"]),
            bus_classes[-1]
        )
        options.append(_base_fields(
            mode="Bus", subtype=rec_bus["class"], emoji="🚌",
            duration=rec_bus["duration"],
            fare_min=rec_bus["fare_min"], fare_max=rec_bus["fare_max"],
            cost_per_person=rec_bus["fare_min"],
            cost_total=rec_bus["fare_min"] * num_people * 2,
            recommended="Bus" in best_mode,
            tip=f"{rec_bus.get('note','')} · Book on RedBus for exact fares.",
            booking_link="https://www.redbus.in/",
            classes=bus_classes,
        ))

    # ── TAXI / CAB ───────────────────────────────────────────────────────────
    taxi_opt = _estimate_taxi_option(
        distance_km, num_people, num_days, destination, orig_region, dest_region)
    if taxi_opt:
        if "Car" in best_mode:
            taxi_opt["recommended"] = True
        taxi_opt["source"]      = origin
        taxi_opt["destination"] = destination
        taxi_opt["currency"]    = "INR"
        taxi_opt["price_source"]= "Estimated"
        taxi_opt["estimated_fare"] = taxi_opt["cost_per_person"]
        taxi_opt["subtype"]     = "AC Sedan"
        options.append(taxi_opt)

    # ── SELF-DRIVE ───────────────────────────────────────────────────────────
    sd_opt = _estimate_self_drive_option(
        distance_km, num_people, num_days, destination, orig_region, dest_region)
    if sd_opt:
        sd_opt["source"]       = origin
        sd_opt["destination"]  = destination
        sd_opt["currency"]     = "INR"
        sd_opt["price_source"] = "Estimated"
        sd_opt["estimated_fare"] = sd_opt["cost_per_person"]
        sd_opt["subtype"]      = "Self-Drive"
        options.append(sd_opt)

    # ── GUARANTEED FALLBACK ───────────────────────────────────────────────────
    if not options:
        fl_min, fl_max = _estimate_flight_cost_pp(
            max(distance_km, 300), origin, destination, orig_region, dest_region)
        options.append(_base_fields(
            mode="Flight", subtype="Economy", emoji="✈️",
            duration="3 hrs",
            fare_min=fl_min, fare_max=fl_max,
            cost_per_person=fl_min, cost_total=fl_min * num_people * 2,
            recommended=True,
            tip="Recommended transport for this route. Fares are estimates.",
            booking_link="https://www.google.com/travel/flights",
        ))

    # ── Mark preferred as recommended ────────────────────────────────────────
    if preferred:
        pl = preferred.lower()
        for opt in options:
            if pl in opt["mode"].lower() or pl in opt.get("subtype", "").lower():
                opt["recommended"] = True

    # ── Sort by estimated_fare ascending (cheapest first) ────────────────────
    options.sort(key=lambda x: x["estimated_fare"])

    print(
        f"[Transport] {origin}→{destination} ({distance_km:.0f}km) "
        f"{len(options)} options | best={best_mode} | "
        f"cheapest={options[0]['mode']} ₹{options[0]['estimated_fare']:,}"
    )
    return options


def predict_budget(
    origin: str,
    destination: str,
    num_days: int,
    num_people: int,
    travel_type: str = "moderate",
    distance_km: float = 0.0,
    preferred_transport: str = None,
    transport_options: List[Dict[str, Any]] = None,
    user_budget: float = 0.0,
    hotel_cost_actual: float = 0.0,      # real selected hotel × days × people (0 = use matrix)
    hotel_name_actual: str = "",         # selected hotel name for display
) -> Dict[str, Any]:
    """
    Destination-aware budget prediction.
    When hotel_cost_actual > 0, uses the real selected hotel cost instead of the matrix estimate.
    Returns a fully itemised budget with: intercity transport, accommodation, food,
    local transport, activities, misc, and a final summary vs user_budget.
    """
    print(f"\n{'='*60}")
    print(f"[Budget] predict_budget CALLED")
    print(f"[Budget]   origin={origin!r}  destination={destination!r}")
    print(f"[Budget]   days={num_days}  people={num_people}  travel_type={travel_type!r}")
    print(f"[Budget]   user_budget=₹{user_budget:,.0f}  distance_km={distance_km:.1f}")
    print(f"[Budget]   preferred_transport={preferred_transport!r}")
    print(f"[Budget]   transport_options count={len(transport_options) if transport_options else 0}")

    # ── Validate inputs ─────────────────────────────────────────────────────
    num_days    = max(1, int(num_days))
    num_people  = max(1, int(num_people))
    travel_type = travel_type.lower().strip() if travel_type else "moderate"
    if travel_type not in ("budget", "moderate", "luxury"):
        print(f"[Budget] WARNING: unknown travel_type '{travel_type}', defaulting to 'moderate'")
        travel_type = "moderate"

    # ── Resolve distance if missing ─────────────────────────────────────────
    if distance_km <= 0:
        try:
            from utils.helpers import geocode_city, haversine_distance as _hav
            oc = geocode_city(origin)
            dc = geocode_city(destination)
            if oc and dc:
                distance_km = _hav(oc[0], oc[1], dc[0], dc[1])
                print(f"[Budget] Resolved distance via geocode: {distance_km:.1f} km")
            else:
                distance_km = 300
                print(f"[Budget] Geocode failed, using fallback distance: {distance_km} km")
        except Exception as e:
            distance_km = 300
            print(f"[Budget] Geocode exception ({e}), using fallback distance: {distance_km} km")

    # ── Classify destination ─────────────────────────────────────────────────
    category = _classify_destination(destination)
    print(f"[Budget] Destination category: '{category}'")

    # Verify category is valid
    if category not in DEST_COST_MATRIX:
        print(f"[Budget] ERROR: category '{category}' missing from DEST_COST_MATRIX! Falling back.")
        category = "india_tier2"

    # ── Resolve intercity transport cost ────────────────────────────────────
    intercity_total     = 0.0
    transport_mode_used = "Estimated"

    if transport_options:
        print(f"[Budget] Available transport options:")
        for opt in transport_options:
            print(f"[Budget]   {opt['mode']} → cost_total=₹{opt.get('cost_total', 0):,.0f}")

    if transport_options and preferred_transport:
        pref_lower = preferred_transport.lower().strip()
        for opt in transport_options:
            if pref_lower in opt["mode"].lower():
                intercity_total     = float(opt.get("cost_total", 0))
                transport_mode_used = opt["mode"]
                print(f"[Budget] Matched preferred transport '{preferred_transport}' → ₹{intercity_total:,.0f}")
                break
        if intercity_total == 0:
            print(f"[Budget] WARNING: preferred_transport '{preferred_transport}' not matched in options")

    # Fall back to cheapest available option
    if intercity_total == 0 and transport_options:
        cheapest = min(transport_options, key=lambda x: float(x.get("cost_total", 999999)))
        intercity_total     = float(cheapest.get("cost_total", 0))
        transport_mode_used = cheapest["mode"]
        print(f"[Budget] Using cheapest option: '{transport_mode_used}' → ₹{intercity_total:,.0f}")

    # Last resort: distance-based rough estimate
    if intercity_total <= 0:
        intercity_total     = max(500.0, distance_km * 1.2 * num_people * 2)
        transport_mode_used = "Estimated"
        print(f"[Budget] No transport options, distance estimate → ₹{intercity_total:,.0f}")

    print(f"[Budget] Final intercity cost: ₹{intercity_total:,.0f} via '{transport_mode_used}'")

    # ── Compute cost for requested tier ─────────────────────────────────────
    requested_tier = travel_type   # already validated above
    print(f"[Budget] Computing cost for tier='{requested_tier}'...")

    primary = _compute_trip_cost(category, requested_tier, num_days, num_people, intercity_total)

    # If user selected a real hotel, override the matrix accommodation estimate
    if hotel_cost_actual > 0:
        old_accom = primary["accommodation"]
        primary["accommodation"]        = round(hotel_cost_actual)
        primary["total"]                = primary["total"] - old_accom + round(hotel_cost_actual)
        primary["hotel_name_actual"]    = hotel_name_actual or "Selected Hotel"
        primary["hotel_cost_source"]    = "Selected"
        print(f"[Budget] Hotel override: matrix ₹{old_accom:,} → actual ₹{hotel_cost_actual:,} ({hotel_name_actual})")
    else:
        primary["hotel_name_actual"]    = ""
        primary["hotel_cost_source"]    = "Estimated"

    # Sanity check — if total is somehow 0, something is very wrong
    if primary["total"] <= 0:
        raise RuntimeError(
            f"[Budget] FATAL: _compute_trip_cost returned total=0 for "
            f"category={category!r} tier={requested_tier!r} "
            f"days={num_days} people={num_people} intercity={intercity_total}"
        )

    total = primary["total"]
    print(f"[Budget] Primary estimate: ₹{total:,.0f}")

    # ── Budget feasibility ───────────────────────────────────────────────────
    budget_fit = None
    if user_budget > 0:
        feasible = None
        print(f"[Budget] Checking feasibility against user_budget=₹{user_budget:,.0f}")

        for tier in TIER_ORDER:
            candidate = _compute_trip_cost(category, tier, num_days, num_people, intercity_total)
            print(f"[Budget]   Tier '{tier}' → ₹{candidate['total']:,.0f} | fits={candidate['total'] <= user_budget}")
            if candidate["total"] <= user_budget:
                feasible = candidate
                break

        if feasible:
            actual_tier   = feasible["tier"]
            adjusted_cost = feasible["total"]
            adjustments   = []

            if actual_tier != requested_tier:
                saves = round(primary["accommodation"] - feasible["accommodation"])
                adjustments.append({
                    "icon": "🏨",
                    "saves": saves,
                    "text": (
                        f"Accommodation adjusted to {TIER_LABELS[actual_tier]} — "
                        f"saves ₹{saves:,.0f}"
                    ),
                })

            savings     = round(user_budget - adjusted_cost)
            utilization = round((adjusted_cost / user_budget) * 100, 1)

            if actual_tier == requested_tier:
                recommendation = f"🎉 Your trip fits comfortably! You have ₹{savings:,.0f} to spare."
            else:
                recommendation = (
                    f"Trip optimized to {TIER_LABELS[actual_tier]} to fit your ₹{user_budget:,.0f} budget. "
                    f"₹{savings:,.0f} remaining."
                )

            upgrade_items = []
            tier_idx = TIER_ORDER.index(actual_tier)
            if tier_idx + 1 < len(TIER_ORDER):
                next_tier  = TIER_ORDER[tier_idx + 1]
                next_cost  = _compute_trip_cost(category, next_tier, num_days, num_people, intercity_total)
                extra_needed = round(next_cost["total"] - user_budget)
                if extra_needed > 0:
                    upgrade_items.append({
                        "cost": extra_needed,
                        "benefit": f"Upgrade to {TIER_LABELS[next_tier]} — better comfort & dining",
                    })
            cost_per_day = round(adjusted_cost / max(num_days, 1))
            upgrade_items.append({
                "cost": cost_per_day,
                "benefit": f"Add 1 extra day in {destination}",
            })

            budget_fit = {
                "fits_budget": True,
                "original_estimate": total,
                "adjusted_estimate": adjusted_cost,
                "actual_tier": actual_tier,
                "feasible_tier": actual_tier,
                "budget_provided": user_budget,
                "shortfall": 0,
                "savings": savings,
                "utilization_pct": utilization,
                "adjustments_made": adjustments,
                "recommendation": recommendation,
                "upgrade_plan": {
                    "extra_budget_needed": upgrade_items[0]["cost"] if upgrade_items else 0,
                    "total_with_upgrade": round(adjusted_cost + (upgrade_items[0]["cost"] if upgrade_items else 0)),
                    "items": upgrade_items[:2],
                    "summary": f"₹{savings:,.0f} to spare — consider upgrading!" if savings > 1000 else "",
                },
            }
            primary = feasible
            print(f"[Budget] Feasible at tier='{actual_tier}' → ₹{adjusted_cost:,.0f} | savings=₹{savings:,.0f}")

        else:
            # Infeasible even at cheapest tier
            cheapest_cost = _compute_trip_cost(category, "budget", num_days, num_people, intercity_total)
            shortfall     = round(cheapest_cost["total"] - user_budget)
            print(f"[Budget] INFEASIBLE — cheapest possible ₹{cheapest_cost['total']:,.0f} > budget ₹{user_budget:,.0f} | shortfall=₹{shortfall:,.0f}")

            days_suggestion = None
            for try_days in range(num_days - 1, 0, -1):
                c = _compute_trip_cost(category, "budget", try_days, num_people, intercity_total)
                if c["total"] <= user_budget:
                    days_suggestion = {"days": try_days, "estimated": c["total"]}
                    break

            cheaper_transport = None
            if transport_options:
                for opt in sorted(transport_options, key=lambda x: float(x.get("cost_total", 999999))):
                    if opt["mode"] != transport_mode_used:
                        alt = _compute_trip_cost(category, "budget", num_days, num_people, float(opt.get("cost_total", 0)))
                        if alt["total"] <= user_budget:
                            cheaper_transport = {
                                "mode": opt["mode"],
                                "emoji": opt.get("emoji", "🚌"),
                                "saves": round(intercity_total - float(opt.get("cost_total", 0))),
                            }
                            break

            budget_fit = {
                "fits_budget": False,
                "original_estimate": total,
                "adjusted_estimate": cheapest_cost["total"],
                "actual_tier": "budget",
                "feasible_tier": None,
                "budget_provided": user_budget,
                "shortfall": shortfall,
                "savings": 0,
                "utilization_pct": round((cheapest_cost["total"] / user_budget) * 100, 1),
                "adjustments_made": [],
                "recommendation": (
                    f"Even at budget tier, {num_days} days in {destination} costs "
                    f"₹{cheapest_cost['total']:,.0f}. You need ₹{shortfall:,.0f} more."
                ),
                "upgrade_plan": None,
                "suggestions": {
                    "budget_needed": shortfall,
                    "days_reduction": days_suggestion,
                    "cheaper_transport": cheaper_transport,
                },
            }

    # ── Budget tips ──────────────────────────────────────────────────────────
    eff_tier  = budget_fit["actual_tier"] if budget_fit else requested_tier
    intl_cats = {
        "europe_expensive", "europe_moderate", "europe_budget",
        "north_america", "australia", "east_asia", "east_asia_expensive",
        "middle_east", "luxury_island",
    }
    is_intl = category in intl_cats

    if eff_tier == "budget":
        budget_tips = [
            "Book hostels or guesthouses — check Hostelworld or Booking.com",
            "Eat at local markets and street stalls — authentic and affordable",
            "Use public transport: metro, bus, or shared rides",
            "Visit free attractions — parks, temples, viewpoints, beaches",
            "Book intercity travel 2–3 weeks in advance for best rates",
        ]
        if is_intl:
            budget_tips.insert(0, "Travel in shoulder season (Apr–May or Sep–Oct) for 30–40% lower costs")
    elif eff_tier == "moderate":
        budget_tips = [
            "Book mid-range hotels mid-week for 15–20% savings",
            "Mix restaurant dining with local street food",
            "Use ride-hailing apps (Uber/Grab/Ola) for local travel",
            "Look for bundled attraction tickets — often 20% cheaper",
            "Travel in off-peak season for significant savings",
        ]
    else:
        budget_tips = [
            "Book luxury hotels and flights 4–6 weeks in advance",
            "Hire a private car or driver for full-day sightseeing",
            "Pre-book premium experiences and guided tours",
            "Get travel insurance for international trips",
            "Use hotel concierge for restaurant reservations and transfers",
        ]

    # ── Compute daily sub-breakdown ─────────────────────────────────────────
    # Split food into breakfast/lunch/dinner (20% / 40% / 40%)
    food_total      = primary["food"]
    breakfast_daily = round(food_total * 0.20 / max(num_days, 1))
    lunch_daily     = round(food_total * 0.40 / max(num_days, 1))
    dinner_daily    = round(food_total * 0.40 / max(num_days, 1))
    local_t_daily   = round(primary["local_transport"] / max(num_days, 1))
    entry_daily     = round(primary["activities"] * 0.60 / max(num_days, 1))
    shopping_daily  = round(primary["activities"] * 0.20 / max(num_days, 1))
    misc_daily      = round(primary["misc"] / max(num_days, 1))
    day_total       = breakfast_daily + lunch_daily + dinner_daily + local_t_daily + entry_daily + shopping_daily + misc_daily

    # Min/Max ranges (budget ±15%, moderate ±25%, luxury ±40%)
    variance = {"budget": 0.15, "moderate": 0.25, "luxury": 0.40}
    v = variance.get(eff_tier, 0.20)
    total_min = round(primary["total"] * (1 - v))
    total_max = round(primary["total"] * (1 + v))

    daily_breakdown = {
        "breakfast":      breakfast_daily,
        "lunch":          lunch_daily,
        "dinner":         dinner_daily,
        "local_transport": local_t_daily,
        "entry_tickets":  entry_daily,
        "shopping":       shopping_daily,
        "misc":           misc_daily,
        "total":          day_total,
        "min_total":      round(day_total * (1 - v)),
        "max_total":      round(day_total * (1 + v)),
    }

    # ── Final cost summary ───────────────────────────────────────────────────
    grand_total      = primary["total"]
    remaining_budget = round(user_budget - grand_total) if user_budget > 0 else 0

    result = {
        # ── Core totals ───────────────────────────────────────────────
        "total_estimated":      grand_total,
        "total_min":            total_min,
        "total_max":            total_max,
        "per_person":           round(grand_total / num_people),
        "original_budget":      user_budget,
        "remaining_budget":     remaining_budget,
        "over_budget":          remaining_budget < 0,

        # ── Line-item breakdown ───────────────────────────────────────
        "intercity_transport":  primary["intercity_transport"],
        "intercity_transport_mode": transport_mode_used,
        "intercity_transport_label": "Estimated" if transport_mode_used == "Estimated" else "Selected",

        "accommodation":        primary["accommodation"],
        "hotel_name":           primary.get("hotel_name_actual", ""),
        "hotel_cost_source":    primary.get("hotel_cost_source", "Estimated"),

        "food":                 primary["food"],
        "local_transport":      primary["local_transport"],
        "transport":            primary["transport"],   # intercity + local combined

        "activities":           primary["activities"],
        "entry_tickets":        round(primary["activities"] * 0.60),
        "shopping":             round(primary["activities"] * 0.20),
        "misc":                 primary["misc"],

        # ── Metadata ──────────────────────────────────────────────────
        "budget_tips":          budget_tips,
        "distance_km":          round(distance_km, 1),
        "transport_mode":       transport_mode_used,
        "destination_category": category,
        "daily_breakdown":      daily_breakdown,
        "budget_fit":           budget_fit,
    }

    print(f"[Budget] FINAL RESULT:")
    print(f"[Budget]   grand_total=₹{grand_total:,.0f}  per_person=₹{result['per_person']:,.0f}")
    print(f"[Budget]   intercity=₹{result['intercity_transport']:,.0f}({transport_mode_used})  hotel=₹{result['accommodation']:,.0f}")
    print(f"[Budget]   food=₹{result['food']:,.0f}  local_t=₹{result['local_transport']:,.0f}  activities=₹{result['activities']:,.0f}  misc=₹{result['misc']:,.0f}")
    print(f"[Budget]   user_budget=₹{user_budget:,.0f}  remaining=₹{remaining_budget:,.0f}")
    print(f"{'='*60}\n")

    return result
