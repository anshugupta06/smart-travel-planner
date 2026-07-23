"""
Offline Service — Deterministic, network-free trip responses.

Supports two verified routes:
  - Delhi → Agra
  - Mumbai → Goa

All data is hand-verified: places, transport, hotels, weather, prices.
No network calls are made. Responses are fully deterministic.
data_source labels: "cached_estimate" / "curated" / "rule_based"
"""
from typing import Dict, Any

OFFLINE_GENERATED_AT = "2025-01-01T00:00:00+00:00"   # fixed for determinism

# ── Verified route data ───────────────────────────────────────────────────────

_DELHI_AGRA = {
    "places": [
        {"name": "Taj Mahal", "rating": 4.8, "address": "Dharmapuri, Tajganj, Agra 282001",
         "types": ["tourist_attraction", "historical"], "price_level": 2,
         "latitude": 27.1751, "longitude": 78.0421,
         "description": "UNESCO World Heritage marble mausoleum — one of the Seven Wonders",
         "best_time": "Sunrise", "popularity_score": 0.98},
        {"name": "Agra Fort", "rating": 4.5, "address": "Rakabganj, Agra 282003",
         "types": ["tourist_attraction", "historical"], "price_level": 1,
         "latitude": 27.1795, "longitude": 78.0211,
         "description": "UNESCO Heritage Mughal fort, residence of emperors for generations",
         "best_time": "Morning", "popularity_score": 0.85},
        {"name": "Fatehpur Sikri", "rating": 4.4, "address": "Fatehpur Sikri, Agra District",
         "types": ["tourist_attraction", "historical"], "price_level": 1,
         "latitude": 27.0946, "longitude": 77.6641,
         "description": "Abandoned Mughal capital, UNESCO World Heritage Site",
         "best_time": "Morning", "popularity_score": 0.80},
        {"name": "Mehtab Bagh", "rating": 4.3, "address": "Dharam Pura, Agra",
         "types": ["tourist_attraction", "park"], "price_level": 1,
         "latitude": 27.1804, "longitude": 78.0366,
         "description": "Moonlight garden with stunning Taj Mahal sunset views",
         "best_time": "Sunset", "popularity_score": 0.72},
        {"name": "Itmad-ud-Daula (Baby Taj)", "rating": 4.3, "address": "Moti Bagh, Agra",
         "types": ["tourist_attraction", "historical"], "price_level": 1,
         "latitude": 27.1950, "longitude": 78.0393,
         "description": "First Mughal structure fully built in marble",
         "best_time": "Morning", "popularity_score": 0.70},
    ],
    "transport": {
        "mode": "Train", "emoji": "🚂", "duration": "2.0 hrs",
        "fare_min": 550, "fare_max": 1800, "fare_label": "₹550–₹1,800",
        "cost_per_person": 550, "cost_total": 2200,
        "available": True, "recommended": True,
        "tip": "Gatimaan Express (fastest, 1h 40m) or Shatabdi. Book on IRCTC.",
        "booking_link": "https://www.irctc.co.in/",
        "price_source": "Cached estimate",
        "classes": [
            {"class": "Chair Car (CC)", "fare_min": 550, "fare_max": 900, "recommended": True},
            {"class": "Executive Chair (EC)", "fare_min": 1200, "fare_max": 1800, "recommended": False},
        ],
    },
    "arrival_point": {
        "name": "Agra Cantt Railway Station", "latitude": 27.1570, "longitude": 78.0098,
        "address": "Cantt Area, Agra 282001", "type": "railway",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=27.1570,78.0098",
        "verified": True, "source": "curated",
    },
    "hotels": [
        {"name": "Hotel Taj Plaza", "rating": 4.2, "user_ratings_total": 1200,
         "address": "Fatehabad Road, Agra", "latitude": 27.1680, "longitude": 78.0390,
         "distance_from_arrival_km": 1.8, "price_per_night_min": 1200, "price_per_night_max": 3500,
         "price_label": "₹1,200–₹3,500/night", "price_source": "Cached estimate",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=27.1680,78.0390"},
        {"name": "Hotel Amar Yatri Niwas", "rating": 4.0, "user_ratings_total": 800,
         "address": "Fatehabad Road, Agra", "latitude": 27.1660, "longitude": 78.0380,
         "distance_from_arrival_km": 2.1, "price_per_night_min": 800, "price_per_night_max": 2000,
         "price_label": "₹800–₹2,000/night", "price_source": "Cached estimate",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=27.1660,78.0380"},
        {"name": "The Oberoi Amarvilas", "rating": 4.9, "user_ratings_total": 2400,
         "address": "Taj East Gate Road, Agra", "latitude": 27.1705, "longitude": 78.0465,
         "distance_from_arrival_km": 2.5, "price_per_night_min": 18000, "price_per_night_max": 40000,
         "price_label": "₹18,000–₹40,000/night", "price_source": "Cached estimate",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=27.1705,78.0465"},
    ],
    "weather": {
        "temperature": 28.0, "feels_like": 30.0, "description": "Partly cloudy",
        "humidity": 55, "wind_speed": 12.0, "icon": "⛅",
        "forecast": [
            {"date": "2025-01-02", "min_temp": 22.0, "max_temp": 30.0, "description": "Sunny", "icon": "☀️"},
            {"date": "2025-01-03", "min_temp": 21.0, "max_temp": 29.0, "description": "Clear", "icon": "☀️"},
        ],
    },
    "intercity_cost": 2200,        # 550/pp × 2 people × 2 (round trip)
    "distance_km": 210.0,
}

_MUMBAI_GOA = {
    "places": [
        {"name": "Baga Beach", "rating": 4.3, "address": "Baga, North Goa",
         "types": ["beach", "tourist_attraction"], "price_level": 0,
         "latitude": 15.5524, "longitude": 73.7516,
         "description": "Lively beach with water sports, shacks and vibrant nightlife",
         "best_time": "Morning", "popularity_score": 0.88},
        {"name": "Basilica of Bom Jesus", "rating": 4.6, "address": "Old Goa, Velha Goa",
         "types": ["place_of_worship", "historical", "tourist_attraction"], "price_level": 0,
         "latitude": 15.5009, "longitude": 73.9116,
         "description": "UNESCO Heritage 16th-century church with St. Francis Xavier's relics",
         "best_time": "Morning", "popularity_score": 0.90},
        {"name": "Fort Aguada", "rating": 4.3, "address": "Sinquerim, North Goa",
         "types": ["tourist_attraction", "historical"], "price_level": 0,
         "latitude": 15.4945, "longitude": 73.7738,
         "description": "17th-century Portuguese fort with iconic lighthouse",
         "best_time": "Evening", "popularity_score": 0.80},
        {"name": "Dudhsagar Waterfalls", "rating": 4.6, "address": "Sonaulim, South Goa",
         "types": ["natural_feature", "tourist_attraction"], "price_level": 1,
         "latitude": 15.3145, "longitude": 74.3148,
         "description": "One of India's tallest waterfalls at 310m",
         "best_time": "Morning", "popularity_score": 0.85},
        {"name": "Palolem Beach", "rating": 4.5, "address": "Palolem, Canacona, South Goa",
         "types": ["beach", "tourist_attraction"], "price_level": 0,
         "latitude": 15.0100, "longitude": 74.0232,
         "description": "Crescent-shaped calm beach ideal for kayaking",
         "best_time": "Morning", "popularity_score": 0.83},
        {"name": "Anjuna Flea Market", "rating": 4.2, "address": "Anjuna, North Goa",
         "types": ["shopping_mall", "tourist_attraction"], "price_level": 0,
         "latitude": 15.5740, "longitude": 73.7417,
         "description": "Iconic Wednesday flea market with handicrafts and local art",
         "best_time": "Morning", "popularity_score": 0.75},
    ],
    "transport": {
        "mode": "Flight", "emoji": "✈️", "duration": "1.2 hrs",
        "fare_min": 2500, "fare_max": 7000, "fare_label": "₹2,500–₹7,000",
        "cost_per_person": 2500, "cost_total": 10000,
        "available": True, "recommended": True,
        "tip": "Book 4–6 weeks ahead. IndiGo and SpiceJet have frequent Mumbai–Goa flights.",
        "booking_link": "https://www.google.com/travel/flights",
        "price_source": "Cached estimate",
        "airlines": [
            {"airline": "IndiGo", "fare_min": 2500, "fare_max": 6000,
             "fare_label": "₹2,500–₹6,000", "note": "Budget carrier · frequent sales"},
            {"airline": "SpiceJet", "fare_min": 2800, "fare_max": 6500,
             "fare_label": "₹2,800–₹6,500", "note": "Budget carrier · frequent sales"},
            {"airline": "Air India", "fare_min": 3500, "fare_max": 7000,
             "fare_label": "₹3,500–₹7,000", "note": "Standard fare"},
        ],
    },
    "arrival_point": {
        "name": "Goa International Airport (GOI) – Mopa",
        "latitude": 15.7129, "longitude": 73.9124,
        "address": "Mopa, North Goa 403512", "type": "airport",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=15.7129,73.9124",
        "verified": True, "source": "curated",
    },
    "hotels": [
        {"name": "Resort Rio", "rating": 4.5, "user_ratings_total": 1800,
         "address": "Arpora, North Goa", "latitude": 15.5562, "longitude": 73.7606,
         "distance_from_arrival_km": 18.2, "price_per_night_min": 2500, "price_per_night_max": 7000,
         "price_label": "₹2,500–₹7,000/night", "price_source": "Cached estimate",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=15.5562,73.7606"},
        {"name": "Lemon Tree Hotel Candolim", "rating": 4.3, "user_ratings_total": 1100,
         "address": "Candolim, North Goa", "latitude": 15.5172, "longitude": 73.7610,
         "distance_from_arrival_km": 22.0, "price_per_night_min": 3000, "price_per_night_max": 8000,
         "price_label": "₹3,000–₹8,000/night", "price_source": "Cached estimate",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=15.5172,73.7610"},
        {"name": "Goa Marriott Resort", "rating": 4.7, "user_ratings_total": 2200,
         "address": "Panaji, Goa", "latitude": 15.4860, "longitude": 73.8270,
         "distance_from_arrival_km": 25.5, "price_per_night_min": 9000, "price_per_night_max": 22000,
         "price_label": "₹9,000–₹22,000/night", "price_source": "Cached estimate",
         "maps_url": "https://www.google.com/maps/search/?api=1&query=15.4860,73.8270"},
    ],
    "weather": {
        "temperature": 30.0, "feels_like": 33.0, "description": "Warm and humid",
        "humidity": 75, "wind_speed": 14.0, "icon": "☀️",
        "forecast": [
            {"date": "2025-01-02", "min_temp": 24.0, "max_temp": 32.0, "description": "Sunny", "icon": "☀️"},
            {"date": "2025-01-03", "min_temp": 25.0, "max_temp": 31.0, "description": "Partly cloudy", "icon": "⛅"},
        ],
    },
    "intercity_cost": 10000,       # 2500/pp × 2 people × 2 (round trip)
    "distance_km": 570.0,
}

# Route key → data
_ROUTES: Dict[str, Dict] = {
    "delhi-agra":   _DELHI_AGRA,
    "mumbai-goa":   _MUMBAI_GOA,
}


def _normalise(city: str) -> str:
    return city.lower().strip().replace(" ", "").replace("-", "")


def _find_route(origin: str, destination: str) -> Dict:
    o = _normalise(origin)
    d = _normalise(destination)
    for key, data in _ROUTES.items():
        parts = key.split("-")
        if _normalise(parts[0]) in o and _normalise(parts[1]) in d:
            return data
        if _normalise(parts[1]) in o and _normalise(parts[0]) in d:
            return data
    raise ValueError(
        f"Offline mode does not support '{origin}' → '{destination}'. "
        f"Supported routes: Delhi → Agra, Mumbai → Goa. "
        f"Switch to Live Mode for other destinations."
    )


def _budget(data: Dict, num_days: int, num_people: int,
            travel_type: str, hotel_ppn: float, user_budget: float) -> Dict:
    """Exact budget reconciliation using cached daily rates."""
    intercity    = data["intercity_cost"]
    accom_ppn    = hotel_ppn if hotel_ppn > 0 else data["hotels"][0]["price_per_night_min"]
    accommodation = round(accom_ppn * num_days)
    # Daily non-accommodation per person (moderate defaults)
    rates = {
        "budget":   {"food": 350, "local_transport": 150, "activities": 500, "misc": 120},
        "moderate": {"food": 700, "local_transport": 400, "activities": 1200, "misc": 300},
        "luxury":   {"food": 1800, "local_transport": 1000, "activities": 2500, "misc": 700},
    }.get(travel_type, {"food": 700, "local_transport": 400, "activities": 1200, "misc": 300})

    food            = rates["food"]          * num_days * num_people
    local_transport = rates["local_transport"]* num_days * num_people
    activities      = rates["activities"]    * num_days * num_people
    misc            = rates["misc"]          * num_days * num_people
    stay_total      = accommodation + food + local_transport + activities + misc
    grand_total     = stay_total + intercity
    remaining       = round(user_budget - grand_total)

    return {
        "total_estimated":         grand_total,
        "total_min":               round(grand_total * 0.85),
        "total_max":               round(grand_total * 1.20),
        "per_person":              round(grand_total / max(num_people, 1)),
        "original_budget":         user_budget,
        "remaining_budget":        remaining,
        "over_budget":             remaining < 0,
        "accommodation":           accommodation,
        "hotel_name":              data["hotels"][0]["name"],
        "hotel_cost_source":       "Cached estimate",
        "food":                    food,
        "local_transport":         local_transport,
        "intercity_transport":     intercity,
        "intercity_transport_mode": data["transport"]["mode"],
        "intercity_transport_label": "Cached estimate",
        "transport":               intercity + local_transport,
        "activities":              activities,
        "entry_tickets":           round(activities * 0.6),
        "shopping":                round(activities * 0.2),
        "misc":                    misc,
        "budget_tips":             ["Book accommodation 2 weeks early", "Use shared taxis for local travel"],
        "transport_mode":          data["transport"]["mode"],
        "destination_category":    "india_tourist",
        "budget_fit": {
            "fits_budget":      remaining >= 0,
            "original_estimate": grand_total,
            "adjusted_estimate": grand_total,
            "actual_tier":       travel_type,
            "feasible_tier":     travel_type,
            "budget_provided":   user_budget,
            "shortfall":         max(0, -remaining),
            "savings":           max(0, remaining),
            "utilization_pct":   min(round((grand_total / max(user_budget, 1)) * 100, 1), 120),
            "adjustments_made":  [],
            "recommendation":    (
                f"Trip fits your budget! ₹{remaining:,} to spare."
                if remaining >= 0
                else f"Budget is ₹{-remaining:,} short. Consider a shorter stay or budget accommodation."
            ),
            "upgrade_plan":      None,
        },
    }


def build_offline_budget_check(
    origin: str, destination: str,
    num_days: int, num_people: int,
    travel_type: str, user_budget: float,
    hotel_ppn: float = 0.0,
    preferred_transport: str = "",
) -> Dict:
    """Full budget check response without any network calls."""
    data   = _find_route(origin, destination)
    budget = _budget(data, num_days, num_people, travel_type, hotel_ppn, user_budget)
    total  = budget["total_estimated"]
    can_gen = budget["budget_fit"]["fits_budget"]

    return {
        "can_generate":              can_gen,
        "selected_transport":        data["transport"],
        "transport_cost":            data["intercity_cost"],
        "remaining_after_transport": round(user_budget - data["intercity_cost"]),
        "feasible_tier":             travel_type,
        "original_travel_type":      travel_type,
        "budget_breakdown":          budget,
        "adjustments":               [],
        "recommendation":            budget["budget_fit"]["recommendation"],
        "upgrade_plan":              None,
        "min_required_budget":       total,
        "suggestions": {
            "cheaper_transport": None,
            "days_reduction":    None,
            "budget_needed":     max(0, total - user_budget),
        },
        "planning_mode": "offline",
        "data_sources":  {"budget": "cached_estimate", "transport": "cached_estimate"},
    }


def build_offline_trip(
    origin: str, destination: str,
    num_days: int, num_people: int,
    travel_type: str, user_budget: float,
    preferences: list = None,
    hotel_ppn: float = 0.0,
    selected_hotel_name: str = "",
) -> Dict:
    """
    Build a complete TripResponse-compatible dict without any network calls.
    All data is verified, deterministic, and labelled with data_sources.
    """
    data   = _find_route(origin, destination)
    budget = _budget(data, num_days, num_people, travel_type, hotel_ppn, user_budget)
    places = data["places"]

    # Distribute places across days evenly
    total_places = len(places)
    ppd          = max(1, min(3, total_places // max(num_days, 1)))
    day_plans    = []
    intercity    = data["intercity_cost"]
    day_pool     = (budget["total_estimated"] - intercity) / max(num_days, 1)

    for d in range(num_days):
        start = (d * ppd) % total_places
        day_ps = [places[(start + j) % total_places] for j in range(ppd)]
        p1 = day_ps[0]["name"]
        p2 = day_ps[1]["name"] if len(day_ps) > 1 else p1

        if d == 0:
            morning = (f"Arrive in {destination} via {data['transport']['mode']}. "
                       f"Check in and freshen up. Head to {p1} early to beat the crowds.")
        else:
            morning = f"Start the day with breakfast and visit {p1} in the morning."

        afternoon = (f"After lunch at a local restaurant, explore {p2}. "
                     f"Ask locals for food recommendations.")
        evening = (f"Enjoy the evening atmosphere of {destination}. "
                   f"Try local street food and relax.")

        if d == num_days - 1:
            evening = f"Last evening in {destination}. Pack, have dinner, and prepare for departure."

        day_plans.append({
            "day":           d + 1,
            "date_label":    f"Day {d + 1} – Explore {destination}",
            "places":        day_ps,
            "narrative":     f"Day {d + 1} exploring the best of {destination}.",
            "morning":       morning,
            "afternoon":     afternoon,
            "evening":       evening,
            "estimated_cost": round(day_pool),
            "route_segments": [],
        })

    return {
        "destination":      destination,
        "origin":           origin,
        "days":             num_days,
        "travel_type":      travel_type,
        "num_people":       num_people,
        "budget_provided":  user_budget,
        "weather":          data["weather"],
        "day_plans":        day_plans,
        "budget_estimate":  budget,
        "transport_options": [data["transport"]],
        "arrival_point":    data["arrival_point"],
        "travel_tips": [
            f"Book {data['transport']['mode'].lower()} tickets at least 2 weeks in advance.",
            "Carry cash — many local attractions don't accept cards.",
            "Start sightseeing early (before 9 AM) to avoid crowds.",
            "Download Google Maps offline for the destination.",
            "Keep a copy of hotel address and emergency contacts.",
        ],
        "top_places":       places[:6],
        "itinerary_summary": (
            f"Discover {destination} over {num_days} days from {origin}. "
            f"This {travel_type} trip covers iconic landmarks and local experiences "
            f"for {num_people} traveller{'s' if num_people > 1 else ''}."
        ),
        "status":        "success",
        "message":       f"Offline itinerary for {destination} — {num_days} days",
        "planning_mode": "offline",
        "generated_at":  OFFLINE_GENERATED_AT,
        "data_sources": {
            "attractions": "curated",
            "weather":     "cached_estimate",
            "transport":   "cached_estimate",
            "hotels":      "curated",
            "itinerary":   "rule_based",
            "budget":      "cached_estimate",
        },
    }
