"""
Places Service — Real attractions only. No hallucinations ever.

Priority pipeline:
  1. Google Places API (Text Search → type-filtered, deduped)
  2. curated_world.WORLD_ATTRACTIONS  (hand-verified international)
  3. FALLBACK_ATTRACTIONS (hand-verified Indian cities)
  4. Empty list — never invent names

NEVER falls back to invented generic names.
"""
import os
import requests
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
PLACES_TEXT_SEARCH    = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_NEARBY_SEARCH  = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACES_DETAILS        = "https://maps.googleapis.com/maps/api/place/details/json"
OSM_NOMINATIM         = "https://nominatim.openstreetmap.org/search"
HEADERS               = {"User-Agent": "SmartTravelPlanner/1.0 (student project)"}

# ── Place type filters ───────────────────────────────────────────────────────
TOURIST_TYPES = {
    "tourist_attraction", "museum", "art_gallery", "aquarium", "zoo",
    "amusement_park", "theme_park", "park", "natural_feature", "beach",
    "campground", "church", "mosque", "hindu_temple", "place_of_worship",
    "stadium", "shopping_mall", "casino", "spa", "night_club",
    "point_of_interest", "establishment", "attraction", "viewpoint",
    "monument", "castle", "ruins", "memorial", "archaeological_site",
    "fort", "historical", "historic", "peak", "waterfall", "landmark",
}

BLOCKED_TYPES = {
    "accounting", "airport", "atm", "bank", "beauty_salon", "bicycle_store",
    "book_store", "bowling_alley", "car_dealer", "car_rental", "car_repair",
    "car_wash", "cemetery", "clothing_store", "convenience_store",
    "courier_service", "dentist", "department_store", "doctor", "drugstore",
    "electrician", "electronics_store", "embassy", "finance", "fire_station",
    "florist", "food", "funeral_home", "furniture_store", "gas_station",
    "general_contractor", "grocery_or_supermarket", "gym", "hair_care",
    "hardware_store", "health", "home_goods_store", "hospital",
    "insurance_agency", "jewelry_store", "laundry", "lawyer",
    "light_rail_station", "liquor_store", "local_government_office",
    "locksmith", "lodging", "meal_delivery", "meal_takeaway", "moving_company",
    "painter", "parking", "pet_store", "pharmacy", "physiotherapist",
    "plumber", "police", "post_office", "primary_school", "real_estate_agency",
    "restaurant", "roofing_contractor", "rv_park", "school", "secondary_school",
    "shoe_store", "storage", "store", "subway_station", "supermarket",
    "taxi_stand", "train_station", "transit_station", "travel_agency",
    "university", "veterinary_care", "clothing", "office",
}

BLOCKED_NAME_PATTERNS = re.compile(
    r"\b(llc|ltd|corp|pvt|inc|clinic|hospital|pharmacy|school|college|"
    r"university|embassy|consulate|ministry|supermarket|salon|barber|"
    r"dentist|dental|garage|auto repair|car wash|law firm|bank|atm|"
    r"real estate|realty|insurance|logistics|warehouse|freight|"
    r"highlights tour|cultural district|panoramic viewpoint|food street|"
    r"city tour|local market|sightseeing|excursion)\b",
    re.IGNORECASE,
)

# ── Indian curated fallback ───────────────────────────────────────────────────
FALLBACK_ATTRACTIONS: Dict[str, List[Dict[str, Any]]] = {
    "delhi": [
        {"name": "Red Fort", "rating": 4.5, "address": "Netaji Subhash Marg, Chandni Chowk, Delhi", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 28.6562, "longitude": 77.2410, "description": "UNESCO World Heritage Mughal fort built in 1638 by Shah Jahan", "best_time": "Morning"},
        {"name": "Qutub Minar", "rating": 4.6, "address": "Mehrauli, New Delhi", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 28.5245, "longitude": 77.1855, "description": "Tallest brick minaret in the world, UNESCO World Heritage Site", "best_time": "Morning"},
        {"name": "India Gate", "rating": 4.7, "address": "Kartavya Path, New Delhi", "types": ["tourist_attraction", "landmark"], "price_level": 0, "latitude": 28.6129, "longitude": 77.2295, "description": "42m war memorial arch, iconic landmark of the capital", "best_time": "Evening"},
        {"name": "Humayun's Tomb", "rating": 4.5, "address": "Mathura Road, Nizamuddin East, New Delhi", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 28.5933, "longitude": 77.2507, "description": "UNESCO Heritage tomb that inspired the Taj Mahal", "best_time": "Morning"},
        {"name": "Akshardham Temple", "rating": 4.7, "address": "NH 24, Pandav Nagar, New Delhi", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 28.6127, "longitude": 77.2773, "description": "Magnificent Hindu temple complex with cultural boat ride", "best_time": "Afternoon"},
        {"name": "Chandni Chowk", "rating": 4.3, "address": "Chandni Chowk, Old Delhi", "types": ["tourist_attraction", "shopping_mall"], "price_level": 1, "latitude": 28.6506, "longitude": 77.2334, "description": "350-year-old market famous for street food, spices and textiles", "best_time": "Morning"},
        {"name": "Lotus Temple", "rating": 4.4, "address": "Bahapur, New Delhi", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 28.5535, "longitude": 77.2588, "description": "Award-winning Bahá'í House of Worship shaped like a blooming lotus", "best_time": "Afternoon"},
        {"name": "Jama Masjid", "rating": 4.5, "address": "Jama Masjid, Old Delhi", "types": ["place_of_worship", "historical"], "price_level": 0, "latitude": 28.6507, "longitude": 77.2334, "description": "India's largest mosque, built by Shah Jahan in 1656", "best_time": "Morning"},
        {"name": "National Museum Delhi", "rating": 4.3, "address": "Janpath, New Delhi", "types": ["museum", "tourist_attraction"], "price_level": 1, "latitude": 28.6118, "longitude": 77.2191, "description": "India's premier museum with 200,000+ artifacts spanning 5000 years", "best_time": "Morning"},
        {"name": "Lodhi Garden", "rating": 4.6, "address": "Lodhi Road, New Delhi", "types": ["park", "tourist_attraction", "historical"], "price_level": 0, "latitude": 28.5931, "longitude": 77.2195, "description": "90-acre garden with 15th-century tombs, morning joggers and birding", "best_time": "Morning"},
    ],
    "agra": [
        {"name": "Taj Mahal", "rating": 4.8, "address": "Dharmapuri, Tajganj, Agra", "types": ["tourist_attraction", "historical"], "price_level": 2, "latitude": 27.1751, "longitude": 78.0421, "description": "Seven Wonders of the World — UNESCO Heritage marble mausoleum", "best_time": "Sunrise"},
        {"name": "Agra Fort", "rating": 4.5, "address": "Rakabganj, Agra", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 27.1795, "longitude": 78.0211, "description": "UNESCO Heritage Mughal fort, residence of Mughal emperors", "best_time": "Morning"},
        {"name": "Fatehpur Sikri", "rating": 4.4, "address": "Fatehpur Sikri, Agra District", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 27.0946, "longitude": 77.6641, "description": "Abandoned Mughal capital, UNESCO World Heritage Site", "best_time": "Morning"},
        {"name": "Mehtab Bagh", "rating": 4.3, "address": "Dharam Pura, Agra", "types": ["tourist_attraction", "park"], "price_level": 1, "latitude": 27.1804, "longitude": 78.0366, "description": "Moonlight garden with stunning Taj Mahal sunset views", "best_time": "Sunset"},
        {"name": "Itmad-ud-Daula (Baby Taj)", "rating": 4.3, "address": "Moti Bagh, Agra", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 27.1950, "longitude": 78.0393, "description": "First Mughal structure fully built in marble — precursor of Taj Mahal", "best_time": "Morning"},
    ],
    "goa": [
        {"name": "Baga Beach", "rating": 4.3, "address": "Baga, North Goa", "types": ["beach", "tourist_attraction"], "price_level": 0, "latitude": 15.5524, "longitude": 73.7516, "description": "Lively beach with water sports, shacks and vibrant nightlife", "best_time": "Morning"},
        {"name": "Basilica of Bom Jesus", "rating": 4.6, "address": "Old Goa, Velha Goa", "types": ["place_of_worship", "historical", "tourist_attraction"], "price_level": 0, "latitude": 15.5009, "longitude": 73.9116, "description": "UNESCO Heritage 16th-century church holding St. Francis Xavier's relics", "best_time": "Morning"},
        {"name": "Dudhsagar Waterfalls", "rating": 4.6, "address": "Sonaulim, South Goa", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 15.3145, "longitude": 74.3148, "description": "One of India's tallest waterfalls at 310m", "best_time": "Morning"},
        {"name": "Fort Aguada", "rating": 4.3, "address": "Sinquerim, North Goa", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 15.4945, "longitude": 73.7738, "description": "17th-century Portuguese fort with iconic lighthouse", "best_time": "Evening"},
        {"name": "Palolem Beach", "rating": 4.5, "address": "Palolem, Canacona, South Goa", "types": ["beach", "tourist_attraction"], "price_level": 0, "latitude": 15.0100, "longitude": 74.0232, "description": "Crescent-shaped calm beach ideal for kayaking", "best_time": "Morning"},
        {"name": "Anjuna Flea Market", "rating": 4.2, "address": "Anjuna, North Goa", "types": ["shopping_mall", "tourist_attraction"], "price_level": 0, "latitude": 15.5740, "longitude": 73.7417, "description": "Iconic Wednesday flea market with handicrafts and local art", "best_time": "Morning"},
        {"name": "Calangute Beach", "rating": 4.1, "address": "Calangute, North Goa", "types": ["beach", "tourist_attraction"], "price_level": 0, "latitude": 15.5438, "longitude": 73.7553, "description": "Queen of Beaches — largest and most popular beach in North Goa", "best_time": "Morning"},
        {"name": "Chapora Fort", "rating": 4.2, "address": "Chapora, North Goa", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 15.5963, "longitude": 73.7438, "description": "Famous Dil Chahta Hai fort with breathtaking Vagator beach views", "best_time": "Sunset"},
    ],
    "jaipur": [
        {"name": "Amber Fort", "rating": 4.7, "address": "Amer, Jaipur", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 26.9855, "longitude": 75.8513, "description": "Magnificent 16th-century Rajput fort-palace overlooking Maota Lake", "best_time": "Morning"},
        {"name": "Hawa Mahal", "rating": 4.6, "address": "Badi Choupad, Jaipur", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 26.9239, "longitude": 75.8267, "description": "Palace of Winds — 953 windows, pink sandstone facade", "best_time": "Morning"},
        {"name": "City Palace Jaipur", "rating": 4.6, "address": "Tulsi Marg, Jaipur", "types": ["tourist_attraction", "historical", "museum"], "price_level": 1, "latitude": 26.9257, "longitude": 75.8237, "description": "Royal palace complex housing museums and courtyards", "best_time": "Morning"},
        {"name": "Jantar Mantar Jaipur", "rating": 4.4, "address": "Gangori Bazaar, Jaipur", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 26.9246, "longitude": 75.8242, "description": "UNESCO Heritage 18th-century astronomical observatory", "best_time": "Morning"},
        {"name": "Nahargarh Fort", "rating": 4.5, "address": "Brahampuri, Jaipur", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 26.9431, "longitude": 75.8065, "description": "Tiger fort with best panoramic views of Jaipur at sunset", "best_time": "Sunset"},
        {"name": "Jal Mahal", "rating": 4.4, "address": "Amer Road, Jaipur", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 26.9516, "longitude": 75.8464, "description": "Water palace floating in Man Sagar Lake", "best_time": "Evening"},
        {"name": "Albert Hall Museum", "rating": 4.4, "address": "Ram Niwas Garden, Jaipur", "types": ["museum", "tourist_attraction"], "price_level": 1, "latitude": 26.9043, "longitude": 75.8210, "description": "Oldest museum in Rajasthan in an Indo-Saracenic building", "best_time": "Morning"},
    ],
    "mumbai": [
        {"name": "Gateway of India", "rating": 4.6, "address": "Apollo Bandar, Colaba, Mumbai", "types": ["tourist_attraction", "historical", "landmark"], "price_level": 0, "latitude": 18.9220, "longitude": 72.8347, "description": "Iconic 26m basalt arch monument on the Arabian Sea", "best_time": "Evening"},
        {"name": "Marine Drive", "rating": 4.7, "address": "Netaji Subhash Chandra Bose Road, Mumbai", "types": ["tourist_attraction", "landmark"], "price_level": 0, "latitude": 18.9438, "longitude": 72.8233, "description": "3.6km C-shaped promenade — Queen's Necklace at night", "best_time": "Evening"},
        {"name": "Elephanta Caves", "rating": 4.4, "address": "Elephanta Island, Mumbai Harbour", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 18.9633, "longitude": 72.9315, "description": "UNESCO Heritage 5th-century rock-cut cave temples", "best_time": "Morning"},
        {"name": "Chhatrapati Shivaji Maharaj Terminus", "rating": 4.5, "address": "CST Area, Fort, Mumbai", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 18.9400, "longitude": 72.8351, "description": "UNESCO Heritage Victorian Gothic railway terminus", "best_time": "Morning"},
        {"name": "Juhu Beach", "rating": 4.1, "address": "Juhu, Mumbai", "types": ["beach", "tourist_attraction"], "price_level": 0, "latitude": 19.0948, "longitude": 72.8258, "description": "Famous beach for street food bhel puri and vada pav", "best_time": "Evening"},
        {"name": "Sanjay Gandhi National Park", "rating": 4.4, "address": "Borivali East, Mumbai", "types": ["park", "tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 19.2147, "longitude": 72.9110, "description": "Urban forest with Kanheri Buddhist caves and toy train", "best_time": "Morning"},
        {"name": "Haji Ali Dargah", "rating": 4.6, "address": "Haji Ali, Worli, Mumbai", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 18.9827, "longitude": 72.8091, "description": "15th-century mosque-mausoleum on a tiny islet accessible via causeway", "best_time": "Morning"},
    ],
    "varanasi": [
        {"name": "Dashashwamedh Ghat", "rating": 4.7, "address": "Dashashwamedh Ghat Road, Varanasi", "types": ["tourist_attraction", "place_of_worship"], "price_level": 0, "latitude": 25.3073, "longitude": 83.0107, "description": "Main ghat with grand Ganga Aarti ceremony every evening", "best_time": "Evening"},
        {"name": "Kashi Vishwanath Temple", "rating": 4.8, "address": "Lahori Tola, Varanasi", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 25.3109, "longitude": 83.0107, "description": "One of the 12 Jyotirlingas, holiest Shiva temple in Hinduism", "best_time": "Morning"},
        {"name": "Sarnath", "rating": 4.5, "address": "Sarnath, Varanasi", "types": ["tourist_attraction", "historical", "place_of_worship"], "price_level": 1, "latitude": 25.3810, "longitude": 83.0229, "description": "Where Buddha gave his first sermon — Dhamek Stupa and Ashoka Pillar", "best_time": "Morning"},
        {"name": "Sunrise Boat Ride on Ganges", "rating": 4.8, "address": "Dashashwamedh Ghat, Varanasi", "types": ["tourist_attraction"], "price_level": 1, "latitude": 25.3073, "longitude": 83.0107, "description": "Iconic dawn boat ride past 84 ghats", "best_time": "Sunrise"},
        {"name": "Manikarnika Ghat", "rating": 4.4, "address": "Manikarnika Ghat, Varanasi", "types": ["tourist_attraction", "place_of_worship"], "price_level": 0, "latitude": 25.3119, "longitude": 83.0108, "description": "Sacred cremation ghat burning 24×7 — profound spiritual experience", "best_time": "Morning"},
        {"name": "Ramnagar Fort", "rating": 4.2, "address": "Ramnagar, Varanasi", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 25.2697, "longitude": 83.0291, "description": "18th-century fort-palace with vintage car museum", "best_time": "Afternoon"},
    ],
    "shimla": [
        {"name": "The Ridge Shimla", "rating": 4.5, "address": "The Ridge, Shimla", "types": ["tourist_attraction", "landmark"], "price_level": 0, "latitude": 31.1048, "longitude": 77.1734, "description": "Open plaza at 2213m with Christ Church and Himalayan panoramas", "best_time": "Morning"},
        {"name": "Jakhu Temple", "rating": 4.6, "address": "Jakhu Hill, Shimla", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 31.1089, "longitude": 77.1831, "description": "Ancient Hanuman temple at Shimla's highest peak (2455m)", "best_time": "Morning"},
        {"name": "Kalka-Shimla Toy Train", "rating": 4.7, "address": "Shimla Railway Station", "types": ["tourist_attraction"], "price_level": 1, "latitude": 31.1037, "longitude": 77.1717, "description": "UNESCO Heritage narrow-gauge mountain railway through 102 tunnels", "best_time": "Morning"},
        {"name": "Kufri", "rating": 4.3, "address": "Kufri, Shimla District", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 31.0980, "longitude": 77.2654, "description": "Alpine ski resort 16km from Shimla with Himalayan zoo", "best_time": "Morning"},
        {"name": "Mall Road Shimla", "rating": 4.4, "address": "Mall Road, Shimla", "types": ["shopping_mall", "tourist_attraction"], "price_level": 1, "latitude": 31.1042, "longitude": 77.1714, "description": "Colonial-era pedestrian promenade with heritage buildings", "best_time": "Afternoon"},
        {"name": "Chadwick Falls", "rating": 4.3, "address": "Summer Hill, Shimla", "types": ["natural_feature", "tourist_attraction"], "price_level": 0, "latitude": 31.0930, "longitude": 77.1520, "description": "67m seasonal waterfall through dense forests in Summer Hill", "best_time": "Morning"},
    ],
    "manali": [
        {"name": "Rohtang Pass", "rating": 4.7, "address": "Rohtang Pass, Kullu District", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 32.3714, "longitude": 77.2501, "description": "High mountain pass at 3979m with snow year-round", "best_time": "Morning"},
        {"name": "Hadimba Devi Temple", "rating": 4.6, "address": "Old Manali", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 32.2459, "longitude": 77.1826, "description": "1553 CE wooden pagoda temple amid cedar forests", "best_time": "Morning"},
        {"name": "Solang Valley", "rating": 4.6, "address": "Solang Village, Kullu District", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 32.3217, "longitude": 77.1508, "description": "Adventure valley — skiing, paragliding, zorbing, cable car", "best_time": "Morning"},
        {"name": "Beas Kund Trek", "rating": 4.5, "address": "Solang Valley, Manali", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 32.3600, "longitude": 77.1300, "description": "High-altitude glacial lake trek through alpine meadows and snow", "best_time": "Morning"},
        {"name": "Old Manali Village", "rating": 4.4, "address": "Old Manali Road, Manali", "types": ["tourist_attraction"], "price_level": 1, "latitude": 32.2519, "longitude": 77.1835, "description": "Charming village with cafes, boutiques and apple orchards", "best_time": "Afternoon"},
        {"name": "Naggar Castle", "rating": 4.3, "address": "Naggar, Kullu District", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 32.1027, "longitude": 77.1762, "description": "500-year-old castle with Nicholas Roerich Art Gallery", "best_time": "Morning"},
    ],
    "kerala": [
        {"name": "Alleppey Backwaters", "rating": 4.8, "address": "Alappuzha (Alleppey), Kerala", "types": ["tourist_attraction", "natural_feature"], "price_level": 2, "latitude": 9.4981, "longitude": 76.3388, "description": "Canals, lakes and lagoons with traditional houseboat cruises", "best_time": "Morning"},
        {"name": "Munnar Tea Gardens", "rating": 4.7, "address": "Munnar, Idukki District, Kerala", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 10.0889, "longitude": 77.0595, "description": "Rolling hills with tea estates at 1600m in Western Ghats", "best_time": "Morning"},
        {"name": "Periyar National Park", "rating": 4.6, "address": "Thekkady, Idukki District", "types": ["tourist_attraction", "natural_feature", "park"], "price_level": 2, "latitude": 9.4649, "longitude": 77.3275, "description": "Tiger reserve with boat safari to spot elephants", "best_time": "Morning"},
        {"name": "Fort Kochi & Chinese Fishing Nets", "rating": 4.5, "address": "Fort Kochi, Ernakulam", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 9.9627, "longitude": 76.2426, "description": "Historic colonial district with iconic cantilevered fishing nets", "best_time": "Evening"},
        {"name": "Varkala Cliff Beach", "rating": 4.5, "address": "Varkala, Thiruvananthapuram", "types": ["beach", "tourist_attraction"], "price_level": 0, "latitude": 8.7330, "longitude": 76.7160, "description": "Dramatic laterite cliffs over the Arabian Sea with mineral spring", "best_time": "Sunset"},
        {"name": "Athirapally Waterfalls", "rating": 4.7, "address": "Athirapally, Thrissur District", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 10.2908, "longitude": 76.5700, "description": "Kerala's largest waterfall at 80ft — the 'Niagara of India'", "best_time": "Morning"},
    ],
    "rishikesh": [
        {"name": "Laxman Jhula", "rating": 4.5, "address": "Laxman Jhula, Rishikesh", "types": ["tourist_attraction", "landmark"], "price_level": 0, "latitude": 30.1278, "longitude": 78.3215, "description": "Iconic iron suspension bridge over the Ganges at 450 feet", "best_time": "Morning"},
        {"name": "Triveni Ghat", "rating": 4.6, "address": "Triveni Ghat, Rishikesh", "types": ["tourist_attraction", "place_of_worship"], "price_level": 0, "latitude": 30.1091, "longitude": 78.2977, "description": "Main ghat with stunning Maha Aarti ceremony at sunset", "best_time": "Evening"},
        {"name": "Bungee Jumping at Jumpin Heights", "rating": 4.7, "address": "Mohan Chatti Village, Rishikesh", "types": ["tourist_attraction"], "price_level": 2, "latitude": 30.1500, "longitude": 78.3100, "description": "India's highest bungee jump at 83 metres over the Ganges", "best_time": "Morning"},
        {"name": "Neelkanth Mahadev Temple", "rating": 4.5, "address": "Neelkanth Mahadev, Rishikesh", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 30.2122, "longitude": 78.3650, "description": "Ancient Shiva temple at 1675m altitude in the forested hills", "best_time": "Morning"},
        {"name": "Ganga Rafting Shivpuri", "rating": 4.7, "address": "Shivpuri, Rishikesh", "types": ["tourist_attraction"], "price_level": 1, "latitude": 30.1660, "longitude": 78.3570, "description": "16km thrilling Grade III-IV white-water rafting on the Ganges", "best_time": "Morning"},
        {"name": "Beatles Ashram (Chaurasi Kutia)", "rating": 4.4, "address": "Swargashram, Rishikesh", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 30.1155, "longitude": 78.3202, "description": "Abandoned forest ashram where The Beatles meditated in 1968", "best_time": "Morning"},
    ],
    "leh": [
        {"name": "Pangong Tso Lake", "rating": 4.9, "address": "Pangong Lake, Leh-Ladakh 194101", "types": ["natural_feature", "tourist_attraction"], "price_level": 0, "latitude": 33.7600, "longitude": 78.6700, "description": "Stunning 134km high-altitude lake (4350m) — turns vivid shades of blue, green and red", "best_time": "Morning"},
        {"name": "Nubra Valley", "rating": 4.8, "address": "Nubra Valley, Leh-Ladakh 194401", "types": ["natural_feature", "tourist_attraction"], "price_level": 0, "latitude": 34.7700, "longitude": 77.5500, "description": "Scenic valley with Bactrian camels, sand dunes and Diskit Monastery at 3048m", "best_time": "Morning"},
        {"name": "Leh Palace", "rating": 4.5, "address": "Fort Road, Leh 194101", "types": ["tourist_attraction", "historical", "museum"], "price_level": 1, "latitude": 34.1633, "longitude": 77.5861, "description": "17th-century nine-storey palace of Ladakhi kings modelled on Potala Palace in Tibet", "best_time": "Morning"},
        {"name": "Thiksey Monastery", "rating": 4.7, "address": "Thiksey, Leh 194101", "types": ["place_of_worship", "tourist_attraction"], "price_level": 1, "latitude": 34.0432, "longitude": 77.6672, "description": "12-storey Buddhist monastery resembling the Potala Palace with a 15m Maitreya statue", "best_time": "Morning"},
        {"name": "Magnetic Hill Leh", "rating": 4.3, "address": "Leh-Kargil-Srinagar Highway, Leh", "types": ["tourist_attraction", "natural_feature"], "price_level": 0, "latitude": 34.2013, "longitude": 77.3710, "description": "Gravity-defying optical illusion road where vehicles appear to roll uphill on their own", "best_time": "Morning"},
        {"name": "Khardung La Pass", "rating": 4.8, "address": "Khardung La, Leh-Ladakh 194101", "types": ["natural_feature", "tourist_attraction"], "price_level": 0, "latitude": 34.2780, "longitude": 77.6090, "description": "One of the world's highest motorable roads at 5359m — gateway to Nubra Valley", "best_time": "Morning"},
        {"name": "Shanti Stupa Leh", "rating": 4.6, "address": "Chanspa, Leh 194101", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 34.1584, "longitude": 77.5683, "description": "White-domed Buddhist stupa built in 1991 with panoramic 360° views over Leh town", "best_time": "Sunset"},
        {"name": "Hemis Monastery", "rating": 4.6, "address": "Hemis, Leh 194101", "types": ["place_of_worship", "tourist_attraction"], "price_level": 1, "latitude": 33.9264, "longitude": 77.7014, "description": "Largest and wealthiest monastery in Ladakh — hosts the famous Hemis Festival every June", "best_time": "Morning"},
        {"name": "Moriri Lake (Tsomoriri)", "rating": 4.8, "address": "Tsomoriri Wetland, Korzok, Leh-Ladakh", "types": ["natural_feature", "tourist_attraction"], "price_level": 0, "latitude": 32.9031, "longitude": 78.3165, "description": "Pristine high-altitude lake at 4522m, home to rare Tibetan migratory birds", "best_time": "Morning"},
        {"name": "Hall of Fame Museum Leh", "rating": 4.4, "address": "Leh-Srinagar Highway, Leh 194101", "types": ["museum", "tourist_attraction"], "price_level": 1, "latitude": 34.1700, "longitude": 77.5900, "description": "Military museum built by Indian Army to honour soldiers who died in Siachen and Kargil", "best_time": "Morning"},
        {"name": "Alchi Monastery", "rating": 4.5, "address": "Alchi, Leh 194301", "types": ["place_of_worship", "tourist_attraction", "historical"], "price_level": 1, "latitude": 34.2260, "longitude": 77.1780, "description": "11th-century monastery with rare Buddhist art and painted clay statues — UNESCO shortlisted", "best_time": "Morning"},
        {"name": "Tso Moriri Wetland Conservation Reserve", "rating": 4.7, "address": "Korzok, Leh-Ladakh", "types": ["natural_feature", "park", "tourist_attraction"], "price_level": 0, "latitude": 32.9000, "longitude": 78.3000, "description": "High-altitude wetland and biosphere reserve with migratory birds and wild horses", "best_time": "Morning"},
    ],
    "udaipur": [
        {"name": "City Palace Udaipur", "rating": 4.7, "address": "City Palace Complex, Udaipur", "types": ["tourist_attraction", "historical", "museum"], "price_level": 1, "latitude": 24.5764, "longitude": 73.6831, "description": "Largest palace complex in Rajasthan overlooking Lake Pichola", "best_time": "Morning"},
        {"name": "Lake Pichola Boat Ride", "rating": 4.6, "address": "Lake Pichola, Udaipur", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 24.5702, "longitude": 73.6762, "description": "Boat ride on the shimmering lake passing Jag Mandir island palace", "best_time": "Evening"},
        {"name": "Jag Mandir Palace", "rating": 4.5, "address": "Lake Pichola, Udaipur", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 24.5658, "longitude": 73.6742, "description": "17th century island palace that inspired the Taj Mahal", "best_time": "Afternoon"},
        {"name": "Saheliyon ki Bari", "rating": 4.3, "address": "Fateh Sagar Road, Udaipur", "types": ["tourist_attraction", "park"], "price_level": 1, "latitude": 24.5905, "longitude": 73.6820, "description": "Garden of maids with fountains, marble elephants and lotus pools", "best_time": "Morning"},
        {"name": "Fateh Sagar Lake", "rating": 4.5, "address": "Fateh Sagar, Udaipur", "types": ["tourist_attraction", "natural_feature"], "price_level": 0, "latitude": 24.5954, "longitude": 73.6771, "description": "Artificial lake surrounded by Aravalli Hills — beautiful sunset views", "best_time": "Sunset"},
        {"name": "Jagdish Temple", "rating": 4.4, "address": "City Palace Road, Udaipur", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 24.5795, "longitude": 73.6831, "description": "1651 CE indo-Aryan style Vishnu temple near City Palace", "best_time": "Morning"},
    ],
}

FALLBACK_ATTRACTIONS["new delhi"] = FALLBACK_ATTRACTIONS["delhi"]
FALLBACK_ATTRACTIONS["kochi"]     = FALLBACK_ATTRACTIONS["kerala"]
FALLBACK_ATTRACTIONS["cochin"]    = FALLBACK_ATTRACTIONS["kerala"]
FALLBACK_ATTRACTIONS["haridwar"]  = FALLBACK_ATTRACTIONS["rishikesh"]
FALLBACK_ATTRACTIONS["ladakh"]    = FALLBACK_ATTRACTIONS["leh"]
FALLBACK_ATTRACTIONS["leh ladakh"] = FALLBACK_ATTRACTIONS["leh"]

# ── Indian state name → best tourist city mapping ────────────────────────────
# When someone types a state instead of a city, redirect to the state's top tourist destination
STATE_TO_CITY: Dict[str, str] = {
    "odisha":            "puri",
    "orissa":            "puri",
    "rajasthan":         "jaipur",
    "himachal pradesh":  "shimla",
    "himachal":          "shimla",
    "uttarakhand":       "rishikesh",
    "uttaranchal":       "rishikesh",
    "tamil nadu":        "madurai",
    "tamilnadu":         "madurai",
    "gujarat":           "ahmedabad",
    "maharashtra":       "mumbai",
    "west bengal":       "kolkata",
    "bengal":            "kolkata",
    "andhra pradesh":    "visakhapatnam",
    "andhra":            "visakhapatnam",
    "telangana":         "hyderabad",
    "karnataka":         "mysore",
    "assam":             "kaziranga",
    "meghalaya":         "shillong",
    "punjab":            "amritsar",
    "haryana":           "chandigarh",
    "madhya pradesh":    "khajuraho",
    "mp":                "khajuraho",
    "uttar pradesh":     "agra",
    "up":                "agra",
    "kerala":            "alleppey",
    "goa state":         "goa",
    "jammu kashmir":     "srinagar",
    "j&k":               "srinagar",
    "sikkim":            "gangtok",
    "nagaland":          "kohima",
    "manipur":           "imphal",
    "mizoram":           "aizawl",
    "arunachal pradesh": "tawang",
    "tripura":           "agartala",
    "bihar":             "bodh gaya",
    "jharkhand":         "ranchi",
    "chhattisgarh":      "raipur",
    "north east india":  "shillong",
    "northeast india":   "shillong",
}

# ── Ahmedabad (Gujarat) fallback ─────────────────────────────────────────────
FALLBACK_ATTRACTIONS["ahmedabad"] = [
    {"name": "Sabarmati Ashram", "rating": 4.7, "address": "Gandhi Smarak Sangrahalaya, Ashram Road, Ahmedabad 380027", "types": ["tourist_attraction", "historical", "museum"], "price_level": 0, "latitude": 23.0609, "longitude": 72.5800, "description": "Mahatma Gandhi's home for 13 years — peaceful ashram on the Sabarmati riverbank where the Salt March began", "best_time": "Morning"},
    {"name": "Sidi Saiyyed Mosque", "rating": 4.5, "address": "Lal Darwaja, Ahmedabad 380001", "types": ["place_of_worship", "historical", "tourist_attraction"], "price_level": 0, "latitude": 23.0252, "longitude": 72.5717, "description": "16th-century mosque famous for its intricately carved stone latticework windows — Ahmedabad's most iconic image", "best_time": "Morning"},
    {"name": "Adalaj Stepwell", "rating": 4.5, "address": "Adalaj, Gandhinagar District 382421", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 23.1680, "longitude": 72.5810, "description": "Elaborate 5-storey 15th-century Hindu stepwell with intricate carvings — stays cool even in summer", "best_time": "Morning"},
    {"name": "Kankaria Lake", "rating": 4.3, "address": "Kankaria, Ahmedabad 380022", "types": ["park", "tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 22.9920, "longitude": 72.6061, "description": "350-year-old lakefront park with zoo, toy train, water rides and heritage walk around the perimeter", "best_time": "Afternoon"},
    {"name": "Rann of Kutch", "rating": 4.8, "address": "Kutch District, Gujarat 370485", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 23.7337, "longitude": 70.1741, "description": "World's largest salt desert — dazzling white expanse famous for Rann Utsav festival (Oct-Feb)", "best_time": "Evening"},
]

# ── Khajuraho (Madhya Pradesh) fallback ──────────────────────────────────────
FALLBACK_ATTRACTIONS["khajuraho"] = [
    {"name": "Western Group of Temples Khajuraho", "rating": 4.8, "address": "Khajuraho, Chhatarpur District 471606", "types": ["tourist_attraction", "historical", "place_of_worship"], "price_level": 1, "latitude": 24.8518, "longitude": 79.9202, "description": "UNESCO Heritage 10th-century temples with exquisite erotic sculptures — architectural masterpieces of Chandela dynasty", "best_time": "Morning"},
    {"name": "Kandariya Mahadeva Temple", "rating": 4.7, "address": "Khajuraho 471606", "types": ["place_of_worship", "tourist_attraction", "historical"], "price_level": 1, "latitude": 24.8517, "longitude": 79.9203, "description": "Tallest and most ornate temple at Khajuraho at 31m — 900 sculptures covering the exterior", "best_time": "Morning"},
    {"name": "Eastern Group of Temples Khajuraho", "rating": 4.5, "address": "Old Village, Khajuraho 471606", "types": ["tourist_attraction", "historical", "place_of_worship"], "price_level": 1, "latitude": 24.8527, "longitude": 79.9281, "description": "Jain and Hindu temples in the old village — less crowded than western group, equally beautiful", "best_time": "Morning"},
    {"name": "Panna National Park", "rating": 4.5, "address": "Panna District, Madhya Pradesh 488001", "types": ["park", "natural_feature", "tourist_attraction"], "price_level": 2, "latitude": 24.7168, "longitude": 80.1851, "description": "Tiger reserve on the Ken River 45km from Khajuraho — jeep safaris with tigers, leopards and vultures", "best_time": "Morning"},
    {"name": "Raneh Falls", "rating": 4.4, "address": "Raneh, Ken River, Khajuraho", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 24.8810, "longitude": 80.0440, "description": "Crystalline basalt gorge on the Ken River with waterfalls — spectacular geology and crocodiles", "best_time": "Morning"},
]

# ── Bodh Gaya (Bihar) fallback ────────────────────────────────────────────────
FALLBACK_ATTRACTIONS["bodh gaya"] = [
    {"name": "Mahabodhi Temple", "rating": 4.9, "address": "Bodh Gaya, Gaya District 824231", "types": ["place_of_worship", "tourist_attraction", "historical"], "price_level": 0, "latitude": 24.6958, "longitude": 84.9914, "description": "UNESCO Heritage — the most sacred Buddhist site in the world, where Gautama Buddha attained enlightenment", "best_time": "Morning"},
    {"name": "Bodhi Tree", "rating": 4.8, "address": "Mahabodhi Temple Complex, Bodh Gaya 824231", "types": ["tourist_attraction", "place_of_worship"], "price_level": 0, "latitude": 24.6957, "longitude": 84.9914, "description": "Descendant of the original fig tree under which the Buddha sat and attained enlightenment 2,500+ years ago", "best_time": "Morning"},
    {"name": "80-Feet Buddha Statue", "rating": 4.5, "address": "Bodh Gaya 824231", "types": ["tourist_attraction", "place_of_worship"], "price_level": 0, "latitude": 24.6965, "longitude": 84.9872, "description": "25m Great Buddha statue in sandstone and red granite — 64 smaller Buddha statues surround the base", "best_time": "Morning"},
    {"name": "Sujata Stupa", "rating": 4.3, "address": "Bakraur Village, Bodh Gaya", "types": ["tourist_attraction", "historical", "place_of_worship"], "price_level": 0, "latitude": 24.7019, "longitude": 85.0011, "description": "Ancient stupa where Sujata offered rice pudding to the Buddha before his enlightenment", "best_time": "Morning"},
    {"name": "Nalanda University Ruins", "rating": 4.7, "address": "Nalanda, Bihar 803111", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 25.1359, "longitude": 85.4432, "description": "UNESCO Heritage — ruins of the world's first residential university (5th-12th century) that taught 10,000 students", "best_time": "Morning"},
]

# ── Shillong (Meghalaya/Northeast) fallback ───────────────────────────────────
FALLBACK_ATTRACTIONS["shillong"] = [
    {"name": "Elephant Falls", "rating": 4.4, "address": "Upper Shillong, Shillong 793019", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 25.5388, "longitude": 91.8400, "description": "Three-tier waterfall in dense subtropical forest — a short walk through a garden of ferns", "best_time": "Morning"},
    {"name": "Ward's Lake", "rating": 4.3, "address": "Lachaumiere, Shillong 793001", "types": ["park", "natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 25.5733, "longitude": 91.8933, "description": "Picturesque horseshoe-shaped lake in the heart of Shillong — boating, gardens and hanging bridge", "best_time": "Morning"},
    {"name": "Cherrapunji (Sohra)", "rating": 4.7, "address": "Sohra, East Khasi Hills, Meghalaya 793108", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 25.2855, "longitude": 91.7284, "description": "Once the wettest place on Earth — Nohkalikai Falls (340m), living root bridges and Seven Sisters Falls", "best_time": "Morning"},
    {"name": "Mawlynnong Village", "rating": 4.6, "address": "Mawlynnong, East Khasi Hills 793119", "types": ["tourist_attraction", "natural_feature"], "price_level": 0, "latitude": 25.2034, "longitude": 91.8979, "description": "Asia's cleanest village — tree houses, living root bridges and stunning views into Bangladesh", "best_time": "Morning"},
    {"name": "Don Bosco Museum Shillong", "rating": 4.5, "address": "Mawlai, Shillong 793008", "types": ["museum", "tourist_attraction"], "price_level": 1, "latitude": 25.5857, "longitude": 91.9099, "description": "Seven-storey museum of Northeast India's tribal culture — 9,000+ artifacts from all 8 NE states", "best_time": "Morning"},
]

# ── State name → fallback mappings ──────────────────────────────────────────
# These pull from WORLD_ATTRACTIONS when FALLBACK_ATTRACTIONS doesn't have the city.
# _WA is a local reference to avoid repeated imports at module level.
def _wa_get(key: str) -> List[Dict[str, Any]]:
    """Safe fetch from WORLD_ATTRACTIONS, empty list if missing."""
    try:
        from services.curated_world import WORLD_ATTRACTIONS as _WA
        return _WA.get(key, [])
    except Exception:
        return []

FALLBACK_ATTRACTIONS["odisha"]            = _wa_get("puri")    or FALLBACK_ATTRACTIONS.get("puri", [])
FALLBACK_ATTRACTIONS["orissa"]            = FALLBACK_ATTRACTIONS["odisha"]
FALLBACK_ATTRACTIONS["rajasthan"]         = FALLBACK_ATTRACTIONS["jaipur"]
FALLBACK_ATTRACTIONS["himachal pradesh"]  = FALLBACK_ATTRACTIONS["shimla"]
FALLBACK_ATTRACTIONS["himachal"]          = FALLBACK_ATTRACTIONS["shimla"]
FALLBACK_ATTRACTIONS["uttaranchal"]       = FALLBACK_ATTRACTIONS["rishikesh"]
FALLBACK_ATTRACTIONS["tamil nadu"]        = _wa_get("madurai")  or FALLBACK_ATTRACTIONS.get("madurai", [])
FALLBACK_ATTRACTIONS["tamilnadu"]         = FALLBACK_ATTRACTIONS["tamil nadu"]
FALLBACK_ATTRACTIONS["gujarat"]           = FALLBACK_ATTRACTIONS["ahmedabad"]
FALLBACK_ATTRACTIONS["maharashtra"]       = FALLBACK_ATTRACTIONS["mumbai"]
FALLBACK_ATTRACTIONS["west bengal"]       = _wa_get("kolkata")
FALLBACK_ATTRACTIONS["bengal"]            = FALLBACK_ATTRACTIONS["west bengal"]
FALLBACK_ATTRACTIONS["telangana"]         = _wa_get("hyderabad")
FALLBACK_ATTRACTIONS["karnataka"]         = _wa_get("mysore")
FALLBACK_ATTRACTIONS["haryana"]           = FALLBACK_ATTRACTIONS["delhi"]
FALLBACK_ATTRACTIONS["madhya pradesh"]    = FALLBACK_ATTRACTIONS["khajuraho"]
FALLBACK_ATTRACTIONS["mp"]               = FALLBACK_ATTRACTIONS["khajuraho"]
FALLBACK_ATTRACTIONS["uttar pradesh"]     = FALLBACK_ATTRACTIONS["agra"]
FALLBACK_ATTRACTIONS["up"]               = FALLBACK_ATTRACTIONS["agra"]
FALLBACK_ATTRACTIONS["up state"]          = FALLBACK_ATTRACTIONS["agra"]
FALLBACK_ATTRACTIONS["bihar"]             = FALLBACK_ATTRACTIONS["bodh gaya"]
FALLBACK_ATTRACTIONS["meghalaya"]         = FALLBACK_ATTRACTIONS["shillong"]
FALLBACK_ATTRACTIONS["assam"]             = FALLBACK_ATTRACTIONS["shillong"]
FALLBACK_ATTRACTIONS["northeast india"]   = FALLBACK_ATTRACTIONS["shillong"]
FALLBACK_ATTRACTIONS["north east india"]  = FALLBACK_ATTRACTIONS["shillong"]
FALLBACK_ATTRACTIONS["jammu kashmir"]     = _wa_get("srinagar") or FALLBACK_ATTRACTIONS.get("srinagar", [])
FALLBACK_ATTRACTIONS["jammu and kashmir"] = FALLBACK_ATTRACTIONS["jammu kashmir"]
FALLBACK_ATTRACTIONS["j&k"]              = FALLBACK_ATTRACTIONS["jammu kashmir"]
FALLBACK_ATTRACTIONS["sikkim"]            = _wa_get("gangtok")  or FALLBACK_ATTRACTIONS.get("darjeeling", [])
FALLBACK_ATTRACTIONS["andhra pradesh"]    = _wa_get("visakhapatnam")
FALLBACK_ATTRACTIONS["andhra"]            = FALLBACK_ATTRACTIONS["andhra pradesh"]
FALLBACK_ATTRACTIONS["punjab"]            = _wa_get("amritsar")
FALLBACK_ATTRACTIONS["haryana"]           = FALLBACK_ATTRACTIONS["delhi"]
FALLBACK_ATTRACTIONS["roorkee"] = [
    {"name": "IIT Roorkee Campus", "rating": 4.5, "address": "IIT Roorkee, Roorkee 247667, Uttarakhand", "types": ["tourist_attraction", "landmark"], "price_level": 0, "latitude": 29.8674, "longitude": 77.8960, "description": "India's oldest technical institute (1847), the historic campus is a national heritage landmark with grand colonial architecture", "best_time": "Morning"},
    {"name": "Solani Aqueduct", "rating": 4.2, "address": "Solani River, Roorkee, Uttarakhand", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 29.8630, "longitude": 77.8880, "description": "Historic 19th-century aqueduct built during the construction of the Upper Ganges Canal — an engineering marvel of its era", "best_time": "Morning"},
    {"name": "Upper Ganges Canal", "rating": 4.1, "address": "Canal Road, Roorkee, Uttarakhand", "types": ["tourist_attraction", "natural_feature"], "price_level": 0, "latitude": 29.8700, "longitude": 77.9000, "description": "One of the oldest and largest irrigation canals in India, built in 1854 — scenic walks along the embankment", "best_time": "Morning"},
    {"name": "Chandi Devi Temple Haridwar", "rating": 4.6, "address": "Neel Parvat, Haridwar, Uttarakhand", "types": ["place_of_worship", "tourist_attraction"], "price_level": 1, "latitude": 29.9630, "longitude": 78.1740, "description": "Hilltop temple dedicated to Chandi Devi accessible by cable car with panoramic Ganges valley views (30km from Roorkee)", "best_time": "Morning"},
    {"name": "Har Ki Pauri Ghat", "rating": 4.7, "address": "Har Ki Pauri, Haridwar, Uttarakhand", "types": ["tourist_attraction", "place_of_worship"], "price_level": 0, "latitude": 29.9582, "longitude": 78.1638, "description": "Most sacred ghat in Haridwar — spectacular Ganga Aarti ceremony every evening (30km from Roorkee)", "best_time": "Evening"},
    {"name": "Mansa Devi Temple", "rating": 4.5, "address": "Bilwa Parvat, Haridwar, Uttarakhand", "types": ["place_of_worship", "tourist_attraction"], "price_level": 1, "latitude": 29.9650, "longitude": 78.1600, "description": "Ancient hilltop temple dedicated to Mansa Devi — accessible via cable car with views of Haridwar (30km from Roorkee)", "best_time": "Morning"},
    {"name": "Rajaji National Park", "rating": 4.5, "address": "Chilla Range, Haridwar, Uttarakhand", "types": ["park", "natural_feature", "tourist_attraction"], "price_level": 2, "latitude": 29.9167, "longitude": 78.2000, "description": "National park in the Shivalik foothills with elephants, leopards, tigers and over 315 bird species (near Roorkee)", "best_time": "Morning"},
]

FALLBACK_ATTRACTIONS["haridwar"] = [
    {"name": "Har Ki Pauri", "rating": 4.7, "address": "Har Ki Pauri, Haridwar, Uttarakhand", "types": ["tourist_attraction", "place_of_worship"], "price_level": 0, "latitude": 29.9582, "longitude": 78.1638, "description": "Most sacred ghat in Haridwar — evening Ganga Aarti ceremony draws thousands of devotees every day", "best_time": "Evening"},
    {"name": "Chandi Devi Temple", "rating": 4.6, "address": "Neel Parvat, Haridwar", "types": ["place_of_worship", "tourist_attraction"], "price_level": 1, "latitude": 29.9630, "longitude": 78.1740, "description": "Hilltop temple accessible by cable car with panoramic views of Haridwar and the Ganges valley", "best_time": "Morning"},
    {"name": "Mansa Devi Temple", "rating": 4.5, "address": "Bilwa Parvat, Haridwar", "types": ["place_of_worship", "tourist_attraction"], "price_level": 1, "latitude": 29.9650, "longitude": 78.1600, "description": "Ancient goddess temple on a hilltop — rope-way ride offers stunning views of the Himalayan foothills", "best_time": "Morning"},
    {"name": "Rajaji National Park", "rating": 4.5, "address": "Chilla Range, Haridwar", "types": ["park", "natural_feature", "tourist_attraction"], "price_level": 2, "latitude": 29.9167, "longitude": 78.2000, "description": "Protected forest with elephants, leopards and 315 bird species — jeep and elephant safaris available", "best_time": "Morning"},
    {"name": "Maya Devi Temple", "rating": 4.4, "address": "Railway Road, Haridwar", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 29.9497, "longitude": 78.1573, "description": "One of the oldest temples in Haridwar, considered a Shakti Peetha (sacred site of goddess worship)", "best_time": "Morning"},
    {"name": "Daksha Mahadev Temple", "rating": 4.3, "address": "Kankhal, Haridwar", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 29.9350, "longitude": 78.1583, "description": "Ancient Shiva temple associated with the mythological King Daksha, in the pilgrimage town of Kankhal", "best_time": "Morning"},
]

FALLBACK_ATTRACTIONS["dehradun"] = [
    {"name": "Robber's Cave (Guchhupani)", "rating": 4.4, "address": "Anarwala Village, Dehradun", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 30.3833, "longitude": 78.0167, "description": "Fascinating natural river cave 8km from the city, where the stream disappears underground and re-emerges", "best_time": "Morning"},
    {"name": "Sahastradhara", "rating": 4.3, "address": "Sahastradhara Road, Dehradun", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 30.3750, "longitude": 78.1200, "description": "Sulphur springs with cascading waterfalls — the name means 'thousand-fold springs', known for medicinal waters", "best_time": "Morning"},
    {"name": "Forest Research Institute (FRI)", "rating": 4.5, "address": "New Forest, Dehradun 248006", "types": ["museum", "tourist_attraction", "historical"], "price_level": 1, "latitude": 30.3433, "longitude": 77.9857, "description": "UNESCO Heritage colonial building set in 450 acres — six museums covering forest ecology and botany", "best_time": "Morning"},
    {"name": "Tapkeshwar Temple", "rating": 4.4, "address": "Garhi Cantonment, Dehradun", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 30.3417, "longitude": 78.0000, "description": "Natural Shiva temple inside a cave where water drips onto a self-formed Shivalinga from stalactites", "best_time": "Morning"},
    {"name": "Paltan Bazaar", "rating": 4.1, "address": "Paltan Bazaar, Dehradun", "types": ["shopping_mall", "tourist_attraction"], "price_level": 1, "latitude": 30.3200, "longitude": 78.0400, "description": "Dehradun's main commercial market — famous for local basmati rice, tea, handicrafts and Pahadi food", "best_time": "Afternoon"},
    {"name": "Mindrolling Monastery", "rating": 4.6, "address": "Clement Town, Dehradun", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 30.2885, "longitude": 77.9847, "description": "One of the largest Buddhist centres in India — a 185-foot stupa and stunning Tibetan Buddhist monastery", "best_time": "Morning"},
]

FALLBACK_ATTRACTIONS["mussoorie"] = [
    {"name": "Kempty Falls", "rating": 4.3, "address": "Kempty, Mussoorie, Uttarakhand", "types": ["natural_feature", "tourist_attraction"], "price_level": 1, "latitude": 30.4667, "longitude": 78.0000, "description": "Multi-tiered waterfall 15km from Mussoorie — natural pool at the base, popular picnic and bathing spot", "best_time": "Morning"},
    {"name": "Gun Hill", "rating": 4.4, "address": "Mall Road, Mussoorie", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 30.4571, "longitude": 78.0822, "description": "Second highest peak in Mussoorie (2024m) reachable by ropeway — panoramic views of the Himalayas", "best_time": "Morning"},
    {"name": "Camel's Back Road", "rating": 4.3, "address": "Camel's Back Road, Mussoorie", "types": ["tourist_attraction", "natural_feature"], "price_level": 0, "latitude": 30.4553, "longitude": 78.0810, "description": "3km scenic ridge walk shaped like a camel's back — stunning sunset views and a rock resembling a camel", "best_time": "Evening"},
    {"name": "Lal Tibba", "rating": 4.4, "address": "Landour, Mussoorie", "types": ["tourist_attraction", "natural_feature"], "price_level": 0, "latitude": 30.4589, "longitude": 78.1017, "description": "Highest peak in Mussoorie (2275m) in the quiet Landour cantonment — telescopes to view snow-capped Himalayan peaks", "best_time": "Morning"},
    {"name": "George Everest House", "rating": 4.2, "address": "Park Estate, Mussoorie", "types": ["tourist_attraction", "historical"], "price_level": 1, "latitude": 30.4617, "longitude": 78.1000, "description": "Ruins of the 19th-century lab and home of Sir George Everest (who Mount Everest is named after)", "best_time": "Morning"},
    {"name": "Mall Road Mussoorie", "rating": 4.4, "address": "The Mall, Mussoorie", "types": ["tourist_attraction", "shopping_mall"], "price_level": 1, "latitude": 30.4536, "longitude": 78.0747, "description": "Main promenade of Mussoorie — colonial-era buildings, local shops, cafes with Himalayan valley views", "best_time": "Afternoon"},
    {"name": "Landour Cantonment", "rating": 4.5, "address": "Landour, Mussoorie", "types": ["tourist_attraction", "historical"], "price_level": 0, "latitude": 30.4589, "longitude": 78.0950, "description": "Charming colonial village above Mussoorie — rustic lanes, old churches, Char Dukan bakery and Ruskin Bond's home", "best_time": "Morning"},
]

FALLBACK_ATTRACTIONS["nainital"] = [
    {"name": "Naini Lake", "rating": 4.7, "address": "Nainital, Uttarakhand 263001", "types": ["natural_feature", "tourist_attraction"], "price_level": 0, "latitude": 29.3909, "longitude": 79.4633, "description": "Iconic pear-shaped lake surrounded by seven hills — boating, horse rides and the famous lakeside promenade", "best_time": "Morning"},
    {"name": "Snow View Point", "rating": 4.4, "address": "Snow View, Nainital", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 29.3969, "longitude": 79.4641, "description": "Aerial ropeway to hilltop viewpoint at 2270m with panoramic views of Himalayas including Nanda Devi peak", "best_time": "Morning"},
    {"name": "Naina Devi Temple", "rating": 4.6, "address": "Mallital, Nainital", "types": ["place_of_worship", "tourist_attraction"], "price_level": 0, "latitude": 29.3946, "longitude": 79.4629, "description": "Ancient Shakti Peetha temple on the north shore of Naini Lake — one of the 64 Shaktipeeths", "best_time": "Morning"},
    {"name": "Eco Cave Gardens", "rating": 4.2, "address": "Mallital, Nainital", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 29.3960, "longitude": 79.4650, "description": "Network of interconnected natural caves named after animals — great for families and children", "best_time": "Morning"},
    {"name": "Tiffin Top (Dorothy's Seat)", "rating": 4.3, "address": "Ayarpatta Hill, Nainital", "types": ["tourist_attraction", "natural_feature"], "price_level": 1, "latitude": 29.3869, "longitude": 79.4647, "description": "Hilltop at 2292m reached by horse ride or trek — panoramic views of Kumaon Himalayas and Nainital town", "best_time": "Morning"},
    {"name": "Mall Road Nainital", "rating": 4.4, "address": "The Mall, Nainital", "types": ["tourist_attraction", "shopping_mall"], "price_level": 1, "latitude": 29.3900, "longitude": 79.4620, "description": "Main lakeside promenade with handicraft shops, local food stalls and colonial-era hotels", "best_time": "Afternoon"},
]

FALLBACK_ATTRACTIONS["mussoorie uttarakhand"] = FALLBACK_ATTRACTIONS["mussoorie"]
FALLBACK_ATTRACTIONS["nainital uttarakhand"] = FALLBACK_ATTRACTIONS["nainital"]
FALLBACK_ATTRACTIONS["dehradun uttarakhand"] = FALLBACK_ATTRACTIONS["dehradun"]
FALLBACK_ATTRACTIONS["haridwar uttarakhand"] = FALLBACK_ATTRACTIONS["haridwar"]
FALLBACK_ATTRACTIONS["roorkee uttarakhand"] = FALLBACK_ATTRACTIONS["roorkee"]


def geocode_nominatim(place_name: str) -> Optional[Dict[str, Any]]:
    """Resolve city name to lat/lon via OpenStreetMap Nominatim."""
    try:
        res = requests.get(
            OSM_NOMINATIM,
            params={"q": place_name, "format": "json", "limit": 1},
            headers=HEADERS, timeout=5,
        )
        if res.status_code == 200 and res.json():
            d = res.json()[0]
            return {"lat": float(d["lat"]), "lon": float(d["lon"])}
    except Exception as e:
        print(f"[PlacesService] Nominatim geocode error: {e}")
    return None


def _is_valid_place(name: str, types: List[str]) -> bool:
    """Return True only if the place passes both type and name filters."""
    # Must have at least one tourist-relevant type
    has_tourist_type = bool(TOURIST_TYPES & set(types))
    # Must not have any blocked type
    has_blocked_type = bool(BLOCKED_TYPES & set(types))
    # Name must not match blocked patterns
    name_blocked = bool(BLOCKED_NAME_PATTERNS.search(name))
    # Reject very short or generic names
    if len(name.strip()) < 4:
        return False
    return has_tourist_type and not has_blocked_type and not name_blocked


def _dedupe(places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate place names (case-insensitive)."""
    seen: set = set()
    out = []
    for p in places:
        key = p.get("name", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            out.append(p)
    return out


def _maps_url(lat: float, lon: float, name: str = "") -> str:
    """Build a direct Google Maps URL for a place."""
    if lat and lon:
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    return f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(name)}"


def _ensure_maps_url(place: Dict[str, Any]) -> Dict[str, Any]:
    """Guarantee every place dict has a non-empty maps_url."""
    if not place.get("maps_url"):
        place["maps_url"] = _maps_url(
            place.get("latitude", 0.0),
            place.get("longitude", 0.0),
            place.get("name", ""),
        )
    return place


def _type_description(types: List[str], name: str, destination: str) -> str:
    """Generate a brief, type-aware description when none is available."""
    t = set(types)
    if "museum" in t or "art_gallery" in t:
        return f"Museum and cultural institution in {destination} worth exploring"
    if "beach" in t:
        return f"Popular beach destination in {destination}"
    if "place_of_worship" in t or "church" in t or "mosque" in t or "hindu_temple" in t:
        return f"Important religious and heritage site in {destination}"
    if "natural_feature" in t or "peak" in t or "waterfall" in t:
        return f"Natural attraction and scenic spot near {destination}"
    if "park" in t:
        return f"Public park and green space popular among visitors to {destination}"
    if "historical" in t or "ruins" in t or "fort" in t or "castle" in t:
        return f"Historic landmark and heritage site in {destination}"
    if "shopping_mall" in t:
        return f"Well-known market and shopping area in {destination}"
    return f"Popular tourist attraction in {destination}"


def _score_place(place: Dict[str, Any]) -> float:
    """
    Popularity score for ranking Google Places results.
    Combines rating (0-5) and review count (log-scaled) and type bonus.
    Higher = better.
    """
    rating       = float(place.get("rating", 3.5))
    review_count = int(place.get("user_ratings_total", 0))
    types        = set(place.get("types", []))

    # Log-scale review count: 10k reviews ≈ 4 pts, 100 reviews ≈ 2 pts
    import math
    review_score = math.log10(max(review_count, 1)) * 1.0

    # Type bonus for iconic attraction types
    type_bonus = 0.5 if (
        "tourist_attraction" in types or "museum" in types or
        "natural_feature" in types or "historical" in types or
        "place_of_worship" in types
    ) else 0.0

    return rating + review_score + type_bonus


def _fetch_google_places(destination: str, max_results: int = 15) -> List[Dict[str, Any]]:
    """
    Fetch tourist attractions using 10 diverse keyword queries.

    Strategy:
    - Run up to 10 targeted queries so sparse destinations like Leh get enough results
    - Stop early once we have 3× max_results raw candidates (efficiency)
    - Dedupe by place_id during collection
    - Filter, rank by popularity score, return top max_results

    Every returned result has: name, rating, lat, lon, address, maps_url, description
    """
    if not GOOGLE_PLACES_API_KEY:
        print("[PlacesService] No Google API key — skipping Google Places")
        return []

    # 10 diverse queries — different keywords surface different results
    queries = [
        f"tourist attractions in {destination}",
        f"places to visit in {destination}",
        f"sightseeing in {destination}",
        f"famous places in {destination}",
        f"monuments in {destination}",
        f"nature attractions in {destination}",
        f"museums in {destination}",
        f"temples monasteries in {destination}",
        f"lakes viewpoints in {destination}",
        f"forts palaces in {destination}",
    ]

    seen_ids: set = set()
    raw_results: List[Dict] = []
    target_raw = max_results * 4   # collect more candidates than needed

    for query in queries:
        if len(raw_results) >= target_raw:
            break
        try:
            res = requests.get(
                PLACES_TEXT_SEARCH,
                params={"query": query, "key": GOOGLE_PLACES_API_KEY},
                timeout=8,
            )
            if res.status_code != 200:
                print(f"[PlacesService] HTTP {res.status_code} — {query[:50]}")
                continue

            data   = res.json()
            status = data.get("status", "")
            if status == "OVER_QUERY_LIMIT":
                print("[PlacesService] ⚠️  API quota exceeded — stopping queries")
                break
            if status not in ("OK", "ZERO_RESULTS"):
                print(f"[PlacesService] Status {status} — {query[:50]}")
                continue

            batch = data.get("results", [])
            added = 0
            for r in batch:
                pid = r.get("place_id", "")
                if pid and pid in seen_ids:
                    continue
                if pid:
                    seen_ids.add(pid)
                raw_results.append(r)
                added += 1

            print(f"[PlacesService] '{query[:40]}' → {len(batch)} results, {added} new")

        except Exception as e:
            print(f"[PlacesService] Query error: {e}")

    print(f"[PlacesService] Total raw candidates: {len(raw_results)} for '{destination}'")

    # ── Filter ───────────────────────────────────────────────────────────────
    valid: List[Dict[str, Any]] = []
    for r in raw_results:
        name  = r.get("name", "").strip()
        types = r.get("types", [])
        if not _is_valid_place(name, types):
            continue

        lat = r.get("geometry", {}).get("location", {}).get("lat", 0.0)
        lon = r.get("geometry", {}).get("location", {}).get("lng", 0.0)
        if not lat and not lon:
            continue   # no coordinates — can't put on map

        editorial   = (r.get("editorial_summary") or {}).get("overview", "")
        description = editorial or _type_description(types, name, destination)

        valid.append({
            "name":               name,
            "rating":             float(r.get("rating", 4.0)),
            "user_ratings_total": int(r.get("user_ratings_total", 0)),
            "address":            r.get("formatted_address", destination),
            "types":              types,
            "price_level":        int(r.get("price_level", 1)),
            "latitude":           lat,
            "longitude":          lon,
            "description":        description,
            "best_time":          "Morning",
            "photo_url":          "",
            "maps_url":           _maps_url(lat, lon, name),
        })

    # ── Rank by composite popularity score ───────────────────────────────────
    valid.sort(key=_score_place, reverse=True)

    # ── Dedupe by name (catches same place returned by multiple queries) ──────
    deduped = _dedupe(valid)

    print(
        f"[PlacesService] Google Places: {len(raw_results)} raw → "
        f"{len(valid)} filtered → {len(deduped)} deduped → "
        f"returning top {min(len(deduped), max_results)}"
    )
    return deduped[:max_results]


def get_places_for_destination(
    destination: str,
    preferences: Optional[List[str]] = None,
    max_places: int = 15,
) -> List[Dict[str, Any]]:
    """
    Main entry point — returns ONLY real, verified tourist attractions.

    Pipeline:
      0. Resolve state names → main tourist city (e.g. "Odisha" → "Puri")
      1. Google Places API (10 queries, ranked by rating + review count)
      2. Always check curated databases (WORLD_ATTRACTIONS + FALLBACK_ATTRACTIONS)
         and MERGE with Google results — never discard curated data
      3. If Google + curated together have ≥ 6 places, return them
      4. If still < 6, return whatever is available (never invent names)
      5. Planner never receives an empty list unless truly no data exists
    """
    normalized = destination.lower().strip()

    # ── Step 0: Resolve state names to their primary tourist city ─────────────
    resolved_destination = destination
    resolved_normalized  = normalized
    if normalized in STATE_TO_CITY:
        resolved_destination = STATE_TO_CITY[normalized].title()
        resolved_normalized  = STATE_TO_CITY[normalized]
        print(f"[PlacesService] State '{destination}' → redirected to city '{resolved_destination}'")
    else:
        # Also try first-word match for states like "Himachal Pradesh" → "himachal"
        first_word = normalized.split()[0]
        if first_word in STATE_TO_CITY:
            resolved_destination = STATE_TO_CITY[first_word].title()
            resolved_normalized  = STATE_TO_CITY[first_word]
            print(f"[PlacesService] State '{destination}' (first-word) → redirected to city '{resolved_destination}'")

    print(f"\n[PlacesService] ── Fetching '{destination}' → using '{resolved_destination}' (max={max_places}) ──")

    # ── Step 1: Google Places (use resolved city name for better results) ─────
    google_results = _fetch_google_places(resolved_destination, max_results=max_places)
    print(f"[PlacesService] Google returned {len(google_results)} valid places")

    # ── Step 2: curated_world.WORLD_ATTRACTIONS ──────────────────────────────
    curated: List[Dict[str, Any]] = []
    try:
        from services.curated_world import WORLD_ATTRACTIONS
        for key, places in WORLD_ATTRACTIONS.items():
            if key in resolved_normalized or resolved_normalized in key:
                curated = places
                print(f"[PlacesService] curated_world match: '{key}' → {len(places)} places")
                break
    except Exception as e:
        print(f"[PlacesService] curated_world error: {e}")

    # ── Step 3: FALLBACK_ATTRACTIONS (Indian cities + state names) ────────────
    fallback: List[Dict[str, Any]] = []
    rn_first = resolved_normalized.split()[0] if resolved_normalized.split() else resolved_normalized
    for key, places in FALLBACK_ATTRACTIONS.items():
        key_first = key.split()[0]
        if (key in resolved_normalized or resolved_normalized in key or
                key_first == rn_first or rn_first in key):
            fallback = places
            print(f"[PlacesService] FALLBACK match: '{key}' → {len(places)} places")
            break

    # ── Step 4: Merge — curated fills gaps in Google results ─────────────────
    all_verified = [_ensure_maps_url(p) for p in google_results + curated + fallback]
    merged = _dedupe(all_verified)
    print(f"[PlacesService] After merge: {len(merged)} unique verified places")

    if merged:
        final = merged[:max_places]
        print(f"[PlacesService] ✅ Returning {len(final)} places for '{destination}'")
        return final

    # ── Step 5: Truly nothing found ───────────────────────────────────────────
    print(f"[PlacesService] ⚠️  No verified places found for '{destination}' — returning empty")
    return []
