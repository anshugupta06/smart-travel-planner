import math
import os
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


# Comprehensive lat/lon for major Indian cities (and a few global ones)
CITY_COORDINATES: dict[str, Tuple[float, float]] = {
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "goa": (15.2993, 74.1240),
    "jaipur": (26.9124, 75.7873),
    "agra": (27.1767, 78.0081),
    "varanasi": (25.3176, 82.9739),
    "kerala": (10.8505, 76.2711),
    "kochi": (9.9312, 76.2673),
    "munnar": (10.0889, 77.0595),
    "thiruvananthapuram": (8.5241, 76.9366),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "udaipur": (24.5854, 73.7125),
    "jodhpur": (26.2389, 73.0243),
    "pushkar": (26.4899, 74.5515),
    "shimla": (31.1048, 77.1734),
    "manali": (32.2396, 77.1887),
    "dharamshala": (32.2190, 76.3234),
    "rishikesh": (30.0869, 78.2676),
    "haridwar": (29.9457, 78.1642),
    "dehradun": (30.3165, 78.0322),
    "darjeeling": (27.0360, 88.2627),
    "sikkim": (27.5330, 88.5122),
    "gangtok": (27.3389, 88.6065),
    "leh": (34.1526, 77.5771),
    "ladakh": (34.1526, 77.5771),
    "amritsar": (31.6340, 74.8723),
    "chandigarh": (30.7333, 76.7794),
    "lucknow": (26.8467, 80.9462),
    "bhopal": (23.2599, 77.4126),
    "indore": (22.7196, 75.8577),
    "nagpur": (21.1458, 79.0882),
    "surat": (21.1702, 72.8311),
    "coimbatore": (11.0168, 76.9558),
    "madurai": (9.9252, 78.1198),
    "mysore": (12.2958, 76.6394),
    "mysuru": (12.2958, 76.6394),
    "ooty": (11.4102, 76.6950),
    "kodaikanal": (10.2381, 77.4892),
    "hampi": (15.3350, 76.4600),
    "gokarna": (14.5479, 74.3188),
    "andaman": (11.7401, 92.6586),
    "port blair": (11.6234, 92.7265),
    "lakshadweep": (10.5667, 72.6417),
    "pondicherry": (11.9416, 79.8083),
    "tirupati": (13.6288, 79.4192),
    "vrindavan": (27.5794, 77.6964),
    "mathura": (27.4924, 77.6737),
    "khajuraho": (24.8318, 79.9199),
    "ajmer": (26.4499, 74.6399),
    "mount abu": (24.5926, 72.7156),
    "puri": (19.8135, 85.8312),
    "konark": (19.8876, 86.0948),
    "bhubaneswar": (20.2961, 85.8245),
    "shillong": (25.5788, 91.8933),
    "kaziranga": (26.5775, 93.1711),
    "guwahati": (26.1445, 91.7362),
    "aizawl": (23.7271, 92.7176),
    "imphal": (24.8170, 93.9368),
    # ── South India ────────────────────────────────────────────────────────
    "kanyakumari": (8.0883, 77.5385),
    "cape comorin": (8.0883, 77.5385),
    "rameswaram": (9.2881, 79.3129),
    "mahabalipuram": (12.6172, 80.1993),
    "mamallapuram": (12.6172, 80.1993),
    "thanjavur": (10.7870, 79.1378),
    "tanjore": (10.7870, 79.1378),
    "trichy": (10.7905, 78.7047),
    "tiruchirappalli": (10.7905, 78.7047),
    "kovalam": (8.3988, 76.9785),
    "varkala": (8.7339, 76.7165),
    "alleppey": (9.4981, 76.3388),
    "alappuzha": (9.4981, 76.3388),
    "thekkady": (9.6000, 77.3000),
    "wayanad": (11.6854, 76.1320),
    "coorg": (12.3375, 75.8069),
    "kodagu": (12.3375, 75.8069),
    "udupi": (13.3409, 74.7421),
    "mangalore": (12.9141, 74.8560),
    "mangaluru": (12.9141, 74.8560),
    "tirupati": (13.6288, 79.4192),
    "tirumala": (13.6837, 79.3470),
    "visakhapatnam": (17.6868, 83.2185),
    "vizag": (17.6868, 83.2185),
    "araku valley": (18.3274, 82.8750),
    "araku": (18.3274, 82.8750),
    "warangal": (17.9784, 79.5941),
    "aurangabad": (19.8762, 75.3433),
    "nashik": (20.0059, 73.7797),
    "kolhapur": (16.7050, 74.2433),
    "shirdi": (19.7645, 74.4766),
    "lonavala": (18.7482, 73.4058),
    "mahabaleshwar": (17.9235, 73.6586),
    "panchgani": (17.9248, 73.7998),
    "lavasa": (18.4080, 73.5030),
    # ── East India ─────────────────────────────────────────────────────────
    "puri": (19.8135, 85.8312),
    "konark": (19.8876, 86.0948),
    "bhubaneswar": (20.2961, 85.8245),
    "cuttack": (20.4625, 85.8828),
    "chilika": (19.7248, 85.3167),
    "patna": (25.5941, 85.1376),
    "bodh gaya": (24.6958, 84.9914),
    "nalanda": (25.1359, 85.4432),
    "ranchi": (23.3441, 85.3096),
    "jamshedpur": (22.8046, 86.2029),
    "raipur": (21.2514, 81.6296),
    "jagdalpur": (19.0728, 82.0218),
    # ── North India ─────────────────────────────────────────────────────────
    "mussoorie": (30.4539, 78.0826),
    "nainital": (29.3909, 79.4636),
    "corbett": (29.5300, 78.9600),
    "jim corbett": (29.5300, 78.9600),
    "ranthambore": (26.0173, 76.5026),
    "ajmer": (26.4499, 74.6399),
    "jodhpur": (26.2389, 73.0243),
    "bikaner": (28.0229, 73.3119),
    "jaisalmer": (26.9157, 70.9083),
    "alwar": (27.5530, 76.6346),
    "mount abu": (24.5926, 72.7156),
    "pushkar": (26.4899, 74.5515),
    "chittorgarh": (24.8887, 74.6269),
    "roorkee": (29.8674, 77.8960),
    "meerut": (28.9845, 77.7064),
    "agra": (27.1767, 78.0081),
    "mathura": (27.4924, 77.6737),
    "vrindavan": (27.5794, 77.6964),
    "allahabad": (25.4358, 81.8463),
    "prayagraj": (25.4358, 81.8463),
    "ayodhya": (26.7950, 82.1950),
    "gorakhpur": (26.7606, 83.3732),
    # ── Northeast India ─────────────────────────────────────────────────────
    "shillong": (25.5788, 91.8933),
    "cherrapunji": (25.2855, 91.7284),
    "kaziranga": (26.5775, 93.1711),
    "majuli": (26.9500, 94.1667),
    "tawang": (27.5860, 91.8594),
    "ziro": (27.5420, 93.8293),
    "kohima": (25.6751, 94.1077),
    # ── Himachal / J&K / Uttarakhand ─────────────────────────────────────
    "spiti": (32.2464, 78.0339),
    "spiti valley": (32.2464, 78.0339),
    "kaza": (32.2263, 78.0719),
    "mcleod ganj": (32.2427, 76.3234),
    "dalhousie": (32.5386, 75.9733),
    "kasauli": (30.9031, 76.9677),
    "solan": (30.9045, 77.0967),
    "pahalgam": (34.0155, 75.3140),
    "gulmarg": (34.0492, 74.3805),
    "sonamarg": (34.3000, 75.2900),
    "leh": (34.1526, 77.5771),
    "srinagar": (34.0837, 74.7973),
    "kargil": (34.5539, 76.1349),
    "kedarnath": (30.7352, 79.0669),
    "badrinath": (30.7433, 79.4938),
    "gangotri": (30.9928, 78.9390),
    "yamunotri": (31.0147, 78.4568),
    "char dham": (30.7352, 79.0669),
    "auli": (30.5219, 79.5681),
    "chakrata": (30.6996, 77.8670),
    # ── Rajasthan ───────────────────────────────────────────────────────────
    "hampi": (15.3350, 76.4600),
    "badami": (15.9207, 75.6777),
    "hospet": (15.2692, 76.3873),
    "hubli": (15.3647, 75.1240),
    "gulbarga": (17.3297, 76.8343),
    # ── Goa ─────────────────────────────────────────────────────────────────
    "north goa": (15.5524, 73.7516),
    "south goa": (15.1700, 74.0000),
    "panaji": (15.4909, 73.8278),
    "mapusa": (15.5939, 73.8105),
    "margao": (15.2736, 73.9577),
    # ── Andaman & Island ────────────────────────────────────────────────────
    "andaman islands": (11.7401, 92.6586),
    "neil island": (11.8300, 93.0500),
    "havelock island": (12.0170, 92.9850),
    "lakshadweep": (10.5667, 72.6417),
    "kavaratti": (10.5669, 72.6420),
    "diu": (20.7141, 70.9872),
    "dwarka": (22.2440, 68.9685),
    "paris": (48.8566, 2.3522),
    "london": (51.5074, -0.1278),
    "new york": (40.7128, -74.0060),
    "tokyo": (35.6762, 139.6503),
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
    "bangkok": (13.7563, 100.5018),
    "bali": (-8.3405, 115.0920),
    "sri lanka": (7.8731, 80.7718),
    "colombo": (6.9271, 79.8612),
    "kathmandu": (27.7172, 85.3240),
}


def geocode_city(city: str) -> Optional[Tuple[float, float]]:
    """
    Return (lat, lon) for a given city name.
    Tries the local lookup dict first; falls back to geopy Nominatim.
    """
    key = city.strip().lower()
    if key in CITY_COORDINATES:
        return CITY_COORDINATES[key]

    # Try partial match
    for known_city, coords in CITY_COORDINATES.items():
        if key in known_city or known_city in key:
            return coords

    # Geopy fallback
    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

        geolocator = Nominatim(user_agent="smart_travel_planner_v1")
        location = geolocator.geocode(city, timeout=5)
        if location:
            return (location.latitude, location.longitude)
    except Exception:
        pass

    return None


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance (km) between two points
    given their latitude and longitude in decimal degrees.
    """
    R = 6371.0  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format a number as Indian Rupee string with comma separators."""
    try:
        amount = float(amount)
        if amount >= 1_00_000:
            return f"{symbol}{amount / 1_00_000:.2f}L"
        elif amount >= 1_000:
            # Indian comma grouping: 1,00,000
            integer_part = int(amount)
            decimal_part = round((amount - integer_part) * 100)
            s = str(integer_part)
            if len(s) > 3:
                result = s[-3:]
                s = s[:-3]
                while len(s) > 2:
                    result = s[-2:] + "," + result
                    s = s[:-2]
                result = s + "," + result
            else:
                result = s
            if decimal_part > 0:
                return f"{symbol}{result}.{decimal_part:02d}"
            return f"{symbol}{result}"
        return f"{symbol}{amount:.0f}"
    except (ValueError, TypeError):
        return f"{symbol}0"


def normalize_city_name(city: str) -> str:
    """Clean and title-case a city name."""
    return city.strip().title()


def estimate_travel_time(distance_km: float, mode: str = "road") -> str:
    """Return a human-readable travel-time estimate."""
    speeds = {"road": 60, "train": 80, "air": 700, "walk": 5}
    speed = speeds.get(mode, 60)
    hours = distance_km / speed
    if hours < 1:
        return f"{int(hours * 60)} mins"
    elif hours < 24:
        return f"{hours:.1f} hrs"
    return f"{hours / 24:.1f} days"


def get_route_distance(origin: str, destination: str) -> Tuple[float, float]:
    """
    Compute driving road distance (km) and travel duration (hours) between origin and destination.
    Uses Haversine straight-line distance adjusted by a routing multiplier.
    Google Routes/Directions APIs are skipped — they are not enabled on this key.
    """
    # Direct Haversine fallback (fast, no external API needed)
    print(f"[DistanceService] Computing Haversine distance for {origin} -> {destination}")
    o_coords = geocode_city(origin)
    d_coords = geocode_city(destination)
    if not o_coords or not d_coords:
        try:
            from services.places_service import geocode_nominatim
            if not o_coords:
                geo_o = geocode_nominatim(origin)
                if geo_o:
                    o_coords = (geo_o["lat"], geo_o["lon"])
            if not d_coords:
                geo_d = geocode_nominatim(destination)
                if geo_d:
                    d_coords = (geo_d["lat"], geo_d["lon"])
        except Exception as e:
            print(f"[DistanceService] Nominatim geocode error: {e}")

    if o_coords and d_coords:
        hav_dist = haversine_distance(o_coords[0], o_coords[1], d_coords[0], d_coords[1])
        _hilly_dests = {
            "manali", "shimla", "dharamshala", "leh", "ladakh", "srinagar", "mussoorie", "nainital",
            "ooty", "munnar", "darjeeling", "gangtok", "sikkim", "kodaikanal"
        }
        dest_lower = destination.lower()
        is_hilly = any(h in dest_lower for h in _hilly_dests)
        multiplier = 1.4 if is_hilly else 1.25

        dist_km = hav_dist * multiplier
        avg_speed = 30.0 if is_hilly else 50.0
        dur_h = dist_km / avg_speed
        print(f"[DistanceService] Haversine ({'Hilly' if is_hilly else 'Plains'}): {origin} -> {destination} = {dist_km:.1f} km, {dur_h:.1f} hrs")
        return dist_km, dur_h

    # Absolute fallback
    print(f"[DistanceService] Geocoding failed completely, returning default 300 km")
    return 300.0, 6.0

