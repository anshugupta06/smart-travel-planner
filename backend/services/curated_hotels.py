"""
Curated hotel database for Indian destinations.
Used as the PRIMARY source for Indian cities — faster and more reliable than OSM/Google.
All hotels are real, well-known properties with verified coordinates and realistic INR prices.
"""
from typing import List, Dict, Any

CURATED_HOTELS: Dict[str, List[Dict[str, Any]]] = {

    "delhi": [
        {"name": "The Imperial New Delhi",        "rating": 4.7, "address": "Janpath, New Delhi 110001",                     "latitude": 28.6222, "longitude": 77.2197, "price_per_night_min": 12000, "price_per_night_max": 35000},
        {"name": "Taj Mahal Hotel New Delhi",      "rating": 4.6, "address": "1 Mansingh Road, New Delhi 110011",             "latitude": 28.6008, "longitude": 77.2197, "price_per_night_min": 10000, "price_per_night_max": 30000},
        {"name": "Lemon Tree Hotel Aerocity",      "rating": 4.2, "address": "Aerocity, New Delhi 110037",                    "latitude": 28.5546, "longitude": 77.1208, "price_per_night_min": 3500,  "price_per_night_max": 8000},
        {"name": "Ibis New Delhi Aerocity",        "rating": 4.1, "address": "Aerocity, New Delhi 110037",                    "latitude": 28.5557, "longitude": 77.1218, "price_per_night_min": 2500,  "price_per_night_max": 6000},
        {"name": "OYO Rooms Paharganj",            "rating": 3.8, "address": "Main Bazaar, Paharganj, New Delhi 110055",       "latitude": 28.6429, "longitude": 77.2154, "price_per_night_min": 800,   "price_per_night_max": 2500},
    ],

    "agra": [
        {"name": "The Oberoi Amarvilas",           "rating": 4.9, "address": "Taj East Gate Road, Agra 282001",               "latitude": 27.1705, "longitude": 78.0465, "price_per_night_min": 18000, "price_per_night_max": 40000},
        {"name": "ITC Mughal Agra",                "rating": 4.7, "address": "Taj Ganj, Agra 282001",                        "latitude": 27.1680, "longitude": 78.0420, "price_per_night_min": 8000,  "price_per_night_max": 20000},
        {"name": "Crystal Sarovar Premiere Agra",  "rating": 4.2, "address": "Fatehabad Road, Agra 282001",                   "latitude": 27.1655, "longitude": 78.0368, "price_per_night_min": 2500,  "price_per_night_max": 6000},
        {"name": "Hotel Amar Yatri Niwas",         "rating": 4.0, "address": "Fatehabad Road, Agra 282001",                   "latitude": 27.1660, "longitude": 78.0380, "price_per_night_min": 800,   "price_per_night_max": 2500},
    ],

    "jaipur": [
        {"name": "Rambagh Palace",                 "rating": 4.8, "address": "Bhawani Singh Road, Jaipur 302005",             "latitude": 26.8958, "longitude": 75.8169, "price_per_night_min": 20000, "price_per_night_max": 60000},
        {"name": "ITC Rajputana Jaipur",           "rating": 4.6, "address": "Palace Road, Jaipur 302006",                   "latitude": 26.9130, "longitude": 75.8053, "price_per_night_min": 6000,  "price_per_night_max": 18000},
        {"name": "Jai Mahal Palace",               "rating": 4.6, "address": "Jacob Road, Jaipur 302006",                    "latitude": 26.9271, "longitude": 75.8042, "price_per_night_min": 8000,  "price_per_night_max": 22000},
        {"name": "Hotel Pearl Palace",             "rating": 4.4, "address": "Hathroi Fort, Amer Road, Jaipur 302001",       "latitude": 26.9157, "longitude": 75.8282, "price_per_night_min": 1200,  "price_per_night_max": 4000},
        {"name": "Zostel Jaipur",                  "rating": 4.2, "address": "Ramganj Bazaar, Jaipur 302003",                "latitude": 26.9228, "longitude": 75.8339, "price_per_night_min": 500,   "price_per_night_max": 1800},
    ],

    "mumbai": [
        {"name": "The Taj Mahal Palace Mumbai",    "rating": 4.8, "address": "Apollo Bunder, Colaba, Mumbai 400001",          "latitude": 18.9220, "longitude": 72.8332, "price_per_night_min": 15000, "price_per_night_max": 45000},
        {"name": "The Oberoi Mumbai",              "rating": 4.8, "address": "Nariman Point, Mumbai 400021",                  "latitude": 18.9267, "longitude": 72.8226, "price_per_night_min": 12000, "price_per_night_max": 40000},
        {"name": "Trident Nariman Point",          "rating": 4.5, "address": "Nariman Point, Mumbai 400021",                  "latitude": 18.9249, "longitude": 72.8233, "price_per_night_min": 7000,  "price_per_night_max": 20000},
        {"name": "Hotel Sea Princess",             "rating": 4.2, "address": "Juhu Beach, Mumbai 400049",                    "latitude": 19.0979, "longitude": 72.8262, "price_per_night_min": 3500,  "price_per_night_max": 9000},
        {"name": "Zostel Mumbai",                  "rating": 4.1, "address": "Backbay Reclamation, Mumbai 400020",            "latitude": 18.9400, "longitude": 72.8316, "price_per_night_min": 600,   "price_per_night_max": 2500},
    ],

    "goa": [
        {"name": "Taj Fort Aguada Resort & Spa",   "rating": 4.7, "address": "Sinquerim, North Goa 403519",                  "latitude": 15.4951, "longitude": 73.7730, "price_per_night_min": 10000, "price_per_night_max": 30000},
        {"name": "The Leela Goa",                  "rating": 4.8, "address": "Mobor, Cavelossim, South Goa 403731",          "latitude": 15.1689, "longitude": 73.9440, "price_per_night_min": 12000, "price_per_night_max": 35000},
        {"name": "Resort Rio Goa",                 "rating": 4.5, "address": "Arpora, Baga, North Goa 403518",               "latitude": 15.5562, "longitude": 73.7606, "price_per_night_min": 2500,  "price_per_night_max": 8000},
        {"name": "Lemon Tree Hotel Candolim",      "rating": 4.3, "address": "Candolim, North Goa 403515",                   "latitude": 15.5172, "longitude": 73.7610, "price_per_night_min": 3000,  "price_per_night_max": 9000},
        {"name": "Zostel Panjim",                  "rating": 4.1, "address": "Fontainhas, Panaji, Goa 403001",               "latitude": 15.4978, "longitude": 73.8335, "price_per_night_min": 500,   "price_per_night_max": 2000},
    ],

    "mussoorie": [
        {"name": "Jaypee Residency Manor",         "rating": 4.5, "address": "System of Badrivishal, Mussoorie 248179",       "latitude": 30.4636, "longitude": 78.0804, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "The Kasmanda Palace Hotel",      "rating": 4.4, "address": "The Mall Road, Mussoorie 248179",               "latitude": 30.4579, "longitude": 78.0718, "price_per_night_min": 4000,  "price_per_night_max": 12000},
        {"name": "Savoy Hotel Mussoorie",          "rating": 4.3, "address": "Library Chowk, Mussoorie 248179",               "latitude": 30.4564, "longitude": 78.0688, "price_per_night_min": 5000,  "price_per_night_max": 14000},
        {"name": "Hotel Padmini Nivas",            "rating": 4.2, "address": "The Mall Road, Mussoorie 248179",               "latitude": 30.4581, "longitude": 78.0722, "price_per_night_min": 2500,  "price_per_night_max": 7000},
        {"name": "Hotel Broadway Mussoorie",       "rating": 4.0, "address": "Camel's Back Road, Mussoorie 248179",           "latitude": 30.4602, "longitude": 78.0753, "price_per_night_min": 1500,  "price_per_night_max": 4500},
        {"name": "Zostel Mussoorie",               "rating": 4.1, "address": "Landour, Mussoorie 248179",                    "latitude": 30.4638, "longitude": 78.1002, "price_per_night_min": 500,   "price_per_night_max": 1800},
    ],

    "shimla": [
        {"name": "Oberoi Cecil Shimla",            "rating": 4.8, "address": "Chaura Maidan, Shimla 171004",                 "latitude": 31.1073, "longitude": 77.1606, "price_per_night_min": 10000, "price_per_night_max": 30000},
        {"name": "Wildflower Hall Shimla",         "rating": 4.9, "address": "Mashobra, Shimla 171012",                      "latitude": 31.1400, "longitude": 77.2100, "price_per_night_min": 15000, "price_per_night_max": 45000},
        {"name": "Hotel Combermere",               "rating": 4.2, "address": "The Mall, Shimla 171001",                      "latitude": 31.1042, "longitude": 77.1714, "price_per_night_min": 2500,  "price_per_night_max": 7000},
        {"name": "Hotel Woodville Palace",         "rating": 4.3, "address": "Raj Bhavan Road, Shimla 171001",               "latitude": 31.1080, "longitude": 77.1620, "price_per_night_min": 3000,  "price_per_night_max": 8000},
        {"name": "YMCA Shimla",                    "rating": 3.8, "address": "The Ridge, Shimla 171001",                     "latitude": 31.1052, "longitude": 77.1730, "price_per_night_min": 600,   "price_per_night_max": 2000},
    ],

    "manali": [
        {"name": "Span Resort & Spa",              "rating": 4.6, "address": "Kullu-Manali Highway, Manali 175131",           "latitude": 32.1984, "longitude": 77.1690, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Holiday Inn Manali",             "rating": 4.2, "address": "Manali-Leh Highway, Manali 175131",             "latitude": 32.2396, "longitude": 77.1887, "price_per_night_min": 3500,  "price_per_night_max": 10000},
        {"name": "Apple Country Resorts",          "rating": 4.3, "address": "Nagar Road, Manali 175131",                    "latitude": 32.2480, "longitude": 77.2020, "price_per_night_min": 2500,  "price_per_night_max": 7000},
        {"name": "Hotel Piccadily Manali",         "rating": 4.1, "address": "Log Huts Area, Manali 175131",                 "latitude": 32.2440, "longitude": 77.1900, "price_per_night_min": 1500,  "price_per_night_max": 5000},
        {"name": "Zostel Manali",                  "rating": 4.2, "address": "Old Manali Road, Manali 175131",               "latitude": 32.2519, "longitude": 77.1835, "price_per_night_min": 400,   "price_per_night_max": 1800},
    ],

    "rishikesh": [
        {"name": "Ananda in the Himalayas",        "rating": 4.9, "address": "Narendra Nagar, Rishikesh 249175",             "latitude": 30.1527, "longitude": 78.3069, "price_per_night_min": 20000, "price_per_night_max": 60000},
        {"name": "Taj Rishikesh Resort & Spa",     "rating": 4.8, "address": "Shyampur, Rishikesh 249203",                   "latitude": 30.1950, "longitude": 78.4050, "price_per_night_min": 12000, "price_per_night_max": 35000},
        {"name": "Glasshouse on the Ganges",       "rating": 4.6, "address": "Rishikesh-Badrinath Road",                     "latitude": 30.1869, "longitude": 78.3551, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Hotel Ganga Kinare",             "rating": 4.3, "address": "16 Virbhadra Road, Rishikesh 249201",          "latitude": 30.1041, "longitude": 78.3010, "price_per_night_min": 2500,  "price_per_night_max": 8000},
        {"name": "Zostel Rishikesh",               "rating": 4.3, "address": "Tapovan, Rishikesh 249192",                   "latitude": 30.1428, "longitude": 78.3268, "price_per_night_min": 400,   "price_per_night_max": 1500},
    ],

    "haridwar": [
        {"name": "Radisson Blu Haridwar",          "rating": 4.4, "address": "Bypass Road, Haridwar 249401",                 "latitude": 29.9462, "longitude": 78.1642, "price_per_night_min": 4000,  "price_per_night_max": 12000},
        {"name": "Haveli Hari Ganga",              "rating": 4.5, "address": "21 Ramghat, Haridwar 249401",                  "latitude": 29.9588, "longitude": 78.1645, "price_per_night_min": 5000,  "price_per_night_max": 14000},
        {"name": "Hotel Ganga Lahari",             "rating": 4.2, "address": "Subhash Ghat, Haridwar 249401",                "latitude": 29.9576, "longitude": 78.1638, "price_per_night_min": 2000,  "price_per_night_max": 6000},
        {"name": "GMVN Haridwar",                  "rating": 3.8, "address": "Near Har ki Pauri, Haridwar 249401",           "latitude": 29.9581, "longitude": 78.1621, "price_per_night_min": 800,   "price_per_night_max": 2500},
    ],

    "varanasi": [
        {"name": "Taj Nadesar Palace",             "rating": 4.8, "address": "Nadesar Palace Grounds, Varanasi 221002",      "latitude": 25.3264, "longitude": 83.0021, "price_per_night_min": 12000, "price_per_night_max": 35000},
        {"name": "BrijRama Palace",                "rating": 4.7, "address": "Darbhanga Ghat, Varanasi 221001",              "latitude": 25.3079, "longitude": 83.0120, "price_per_night_min": 8000,  "price_per_night_max": 25000},
        {"name": "Radisson Hotel Varanasi",        "rating": 4.3, "address": "The Mall, Cantonment, Varanasi 221002",        "latitude": 25.3340, "longitude": 83.0100, "price_per_night_min": 3500,  "price_per_night_max": 9000},
        {"name": "Hotel Ganges View",              "rating": 4.2, "address": "Assi Ghat, Varanasi 221005",                   "latitude": 25.2990, "longitude": 83.0063, "price_per_night_min": 1500,  "price_per_night_max": 5000},
        {"name": "Zostel Varanasi",                "rating": 4.0, "address": "Assi Ghat, Varanasi 221005",                  "latitude": 25.2985, "longitude": 83.0060, "price_per_night_min": 400,   "price_per_night_max": 1500},
    ],

    "udaipur": [
        {"name": "Taj Lake Palace",                "rating": 4.9, "address": "Lake Pichola, Udaipur 313001",                 "latitude": 24.5769, "longitude": 73.6812, "price_per_night_min": 25000, "price_per_night_max": 75000},
        {"name": "The Oberoi Udaivilas",           "rating": 4.9, "address": "Haridasji Ki Magri, Udaipur 313001",           "latitude": 24.5810, "longitude": 73.6753, "price_per_night_min": 30000, "price_per_night_max": 90000},
        {"name": "Fateh Garh Udaipur",             "rating": 4.5, "address": "Fatehsagar Lake, Udaipur 313001",              "latitude": 24.6010, "longitude": 73.6752, "price_per_night_min": 5000,  "price_per_night_max": 18000},
        {"name": "Hotel Mahendra Prakash",         "rating": 4.1, "address": "Outside Chandpole, Udaipur 313001",            "latitude": 24.5846, "longitude": 73.6895, "price_per_night_min": 1500,  "price_per_night_max": 4500},
        {"name": "Zostel Udaipur",                 "rating": 4.2, "address": "Gangaur Ghat, Udaipur 313001",                "latitude": 24.5786, "longitude": 73.6830, "price_per_night_min": 400,   "price_per_night_max": 1800},
    ],

    "jodhpur": [
        {"name": "Umaid Bhawan Palace",            "rating": 4.9, "address": "Circuit House Road, Jodhpur 342006",           "latitude": 26.2889, "longitude": 73.0553, "price_per_night_min": 30000, "price_per_night_max": 100000},
        {"name": "Vivanta Jodhpur",                "rating": 4.6, "address": "Air Force Area, Jodhpur 342011",               "latitude": 26.2631, "longitude": 73.0490, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "RAAS Jodhpur",                   "rating": 4.7, "address": "Tunwarji Ka Jhalra, Old City, Jodhpur 342001", "latitude": 26.2980, "longitude": 73.0230, "price_per_night_min": 8000,  "price_per_night_max": 25000},
        {"name": "Hotel Haveli Inn Pal",           "rating": 4.3, "address": "Gulab Sagar, Jodhpur 342001",                  "latitude": 26.2945, "longitude": 73.0227, "price_per_night_min": 2000,  "price_per_night_max": 6000},
        {"name": "Zostel Jodhpur",                 "rating": 4.2, "address": "Near Clock Tower, Jodhpur 342001",             "latitude": 26.2960, "longitude": 73.0210, "price_per_night_min": 400,   "price_per_night_max": 1800},
    ],

    "jaisalmer": [
        {"name": "Suryagarh Jaisalmer",            "rating": 4.8, "address": "Sam Road, Jaisalmer 345001",                   "latitude": 26.9100, "longitude": 70.8700, "price_per_night_min": 10000, "price_per_night_max": 30000},
        {"name": "The Serai Jaisalmer",            "rating": 4.9, "address": "Kanoi Village, Jaisalmer 345001",              "latitude": 26.9210, "longitude": 70.7810, "price_per_night_min": 20000, "price_per_night_max": 60000},
        {"name": "Hotel Nachana Haveli",           "rating": 4.4, "address": "Gandhi Chowk, Jaisalmer 345001",               "latitude": 26.9147, "longitude": 70.9139, "price_per_night_min": 3000,  "price_per_night_max": 9000},
        {"name": "Hotel Rang Mahal",               "rating": 4.2, "address": "Near Amar Sagar Pol, Jaisalmer 345001",        "latitude": 26.9138, "longitude": 70.9121, "price_per_night_min": 1500,  "price_per_night_max": 5000},
        {"name": "Zostel Jaisalmer",               "rating": 4.2, "address": "Dhibba Para, Jaisalmer 345001",                "latitude": 26.9143, "longitude": 70.9098, "price_per_night_min": 400,   "price_per_night_max": 1800},
    ],

    "kanyakumari": [
        {"name": "Hotel Sparsa Kanyakumari",       "rating": 4.5, "address": "East Car Street, Kanyakumari 629702",          "latitude": 8.0885,  "longitude": 77.5390, "price_per_night_min": 3000,  "price_per_night_max": 8000},
        {"name": "The Seashore Hotel",             "rating": 4.3, "address": "North Car Street, Kanyakumari 629702",         "latitude": 8.0876,  "longitude": 77.5380, "price_per_night_min": 2000,  "price_per_night_max": 6000},
        {"name": "Hotel Sangam Kanyakumari",       "rating": 4.1, "address": "Sannathi Street, Kanyakumari 629702",          "latitude": 8.0861,  "longitude": 77.5378, "price_per_night_min": 1500,  "price_per_night_max": 4500},
        {"name": "TTDC Hotel Tamilnadu",           "rating": 3.9, "address": "Beach Road, Kanyakumari 629702",               "latitude": 8.0870,  "longitude": 77.5365, "price_per_night_min": 800,   "price_per_night_max": 2500},
    ],

    "munnar": [
        {"name": "Windermere Estate",              "rating": 4.7, "address": "Pothamedu, Munnar 685612",                     "latitude": 10.0885, "longitude": 77.0587, "price_per_night_min": 6000,  "price_per_night_max": 18000},
        {"name": "Spice Tree Munnar",              "rating": 4.7, "address": "Bison Valley Road, Munnar 685612",             "latitude": 10.0834, "longitude": 77.0611, "price_per_night_min": 7000,  "price_per_night_max": 20000},
        {"name": "Blanket Hotel & Spa",            "rating": 4.5, "address": "Devikulam Road, Munnar 685616",                "latitude": 10.0545, "longitude": 77.0616, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Hotel Munnar Castle",            "rating": 4.2, "address": "Kannan Devan Hills, Munnar 685612",            "latitude": 10.0891, "longitude": 77.0609, "price_per_night_min": 2500,  "price_per_night_max": 7000},
        {"name": "KTDC Tea County",                "rating": 4.0, "address": "Devikulam Road, Munnar 685616",                "latitude": 10.0559, "longitude": 77.0629, "price_per_night_min": 2000,  "price_per_night_max": 6000},
    ],

    "kodaikanal": [
        {"name": "Carlton Hotel Kodaikanal",       "rating": 4.5, "address": "Lake Road, Kodaikanal 624101",                 "latitude": 10.2368, "longitude": 77.4899, "price_per_night_min": 5000,  "price_per_night_max": 14000},
        {"name": "Sterling Kodai Lake",            "rating": 4.4, "address": "Le Providence Road, Kodaikanal 624101",        "latitude": 10.2336, "longitude": 77.4921, "price_per_night_min": 4000,  "price_per_night_max": 12000},
        {"name": "Hotel Kodai International",      "rating": 4.1, "address": "PT Road, Kodaikanal 624101",                   "latitude": 10.2359, "longitude": 77.4890, "price_per_night_min": 2000,  "price_per_night_max": 6000},
        {"name": "TTDC Hotel Tamil Nadu",          "rating": 3.8, "address": "Fern Hill, Kodaikanal 624101",                 "latitude": 10.2351, "longitude": 77.4876, "price_per_night_min": 800,   "price_per_night_max": 2500},
    ],

    "coorg": [
        {"name": "Orange County Coorg",            "rating": 4.8, "address": "Siddapur, Coorg 571253",                      "latitude": 12.3720, "longitude": 75.7340, "price_per_night_min": 12000, "price_per_night_max": 35000},
        {"name": "Tamara Coorg",                   "rating": 4.7, "address": "Galibeedu, Madikeri, Coorg 571201",            "latitude": 12.4325, "longitude": 75.7545, "price_per_night_min": 10000, "price_per_night_max": 30000},
        {"name": "Evolve Back Coorg",              "rating": 4.9, "address": "Napoklu, Kodagu, Coorg 571201",                "latitude": 12.3612, "longitude": 75.8205, "price_per_night_min": 15000, "price_per_night_max": 45000},
        {"name": "Hotel Coorg International",      "rating": 4.1, "address": "Main Road, Madikeri, Coorg 571201",            "latitude": 12.4218, "longitude": 75.7380, "price_per_night_min": 2500,  "price_per_night_max": 7000},
    ],

    "amritsar": [
        {"name": "Taj Swarna Amritsar",            "rating": 4.7, "address": "Opp. Passport Office, Amritsar 143001",        "latitude": 31.6340, "longitude": 74.8723, "price_per_night_min": 6000,  "price_per_night_max": 18000},
        {"name": "Hyatt Amritsar",                 "rating": 4.6, "address": "Adjoining Passport Office, Amritsar 143001",   "latitude": 31.6350, "longitude": 74.8735, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Hotel Mohan International",      "rating": 4.0, "address": "Albert Road, Amritsar 143001",                 "latitude": 31.6340, "longitude": 74.8752, "price_per_night_min": 1500,  "price_per_night_max": 4500},
        {"name": "Zostel Amritsar",                "rating": 4.1, "address": "Near Golden Temple, Amritsar 143006",          "latitude": 31.6193, "longitude": 74.8772, "price_per_night_min": 400,   "price_per_night_max": 1500},
    ],

    "bangalore": [
        {"name": "The Leela Palace Bengaluru",     "rating": 4.8, "address": "23 HAL Airport Road, Bengaluru 560008",        "latitude": 12.9649, "longitude": 77.6499, "price_per_night_min": 12000, "price_per_night_max": 40000},
        {"name": "ITC Windsor Bengaluru",          "rating": 4.6, "address": "25 Golf Course Road, Bengaluru 560052",        "latitude": 12.9977, "longitude": 77.5935, "price_per_night_min": 7000,  "price_per_night_max": 20000},
        {"name": "Taj MG Road Bengaluru",          "rating": 4.5, "address": "41/3 MG Road, Bengaluru 560001",               "latitude": 12.9741, "longitude": 77.6143, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Ibis Bengaluru City Centre",     "rating": 4.1, "address": "Vittal Mallya Road, Bengaluru 560001",         "latitude": 12.9725, "longitude": 77.5980, "price_per_night_min": 2500,  "price_per_night_max": 6000},
        {"name": "Zostel Bengaluru",               "rating": 4.0, "address": "Indiranagar, Bengaluru 560038",               "latitude": 12.9784, "longitude": 77.6408, "price_per_night_min": 500,   "price_per_night_max": 2000},
    ],

    "hyderabad": [
        {"name": "Taj Falaknuma Palace",           "rating": 4.9, "address": "Engine Bowli, Hyderabad 500053",               "latitude": 17.3313, "longitude": 78.4668, "price_per_night_min": 20000, "price_per_night_max": 60000},
        {"name": "ITC Kohenur Hyderabad",          "rating": 4.7, "address": "HITEC City, Hyderabad 500084",                 "latitude": 17.4486, "longitude": 78.3771, "price_per_night_min": 8000,  "price_per_night_max": 25000},
        {"name": "Marriott Hyderabad",             "rating": 4.5, "address": "Tank Bund Road, Hyderabad 500080",             "latitude": 17.4225, "longitude": 78.4740, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Hotel Golkonda Hyderabad",       "rating": 4.1, "address": "Masab Tank, Hyderabad 500028",                 "latitude": 17.3965, "longitude": 78.4577, "price_per_night_min": 2000,  "price_per_night_max": 6000},
    ],

    "chennai": [
        {"name": "The Leela Palace Chennai",       "rating": 4.8, "address": "Adyar Seaface, Chennai 600020",                "latitude": 13.0010, "longitude": 80.2571, "price_per_night_min": 10000, "price_per_night_max": 35000},
        {"name": "ITC Grand Chola Chennai",        "rating": 4.8, "address": "63 Mount Road, Chennai 600032",                "latitude": 13.0116, "longitude": 80.2280, "price_per_night_min": 10000, "price_per_night_max": 30000},
        {"name": "Taj Coromandel Chennai",         "rating": 4.7, "address": "37 MG Road, Chennai 600034",                   "latitude": 13.0618, "longitude": 80.2490, "price_per_night_min": 8000,  "price_per_night_max": 25000},
        {"name": "Ibis Chennai City Centre",       "rating": 4.1, "address": "Montieth Road, Egmore, Chennai 600008",        "latitude": 13.0729, "longitude": 80.2606, "price_per_night_min": 2500,  "price_per_night_max": 6000},
    ],

    "kolkata": [
        {"name": "The Oberoi Grand Kolkata",       "rating": 4.8, "address": "15 Jawaharlal Nehru Road, Kolkata 700013",     "latitude": 22.5601, "longitude": 88.3499, "price_per_night_min": 8000,  "price_per_night_max": 25000},
        {"name": "Taj Bengal Kolkata",             "rating": 4.7, "address": "34B Belvedere Road, Alipore, Kolkata 700027",  "latitude": 22.5332, "longitude": 88.3329, "price_per_night_min": 7000,  "price_per_night_max": 22000},
        {"name": "ITC Royal Bengal Kolkata",       "rating": 4.7, "address": "1 JBS Haldane Avenue, Kolkata 700046",         "latitude": 22.5497, "longitude": 88.3714, "price_per_night_min": 7000,  "price_per_night_max": 20000},
        {"name": "Hotel Hindusthan International", "rating": 4.0, "address": "235/1 AJC Bose Road, Kolkata 700020",          "latitude": 22.5459, "longitude": 88.3553, "price_per_night_min": 2500,  "price_per_night_max": 7000},
    ],

    "leh": [
        {"name": "The Grand Dragon Ladakh",        "rating": 4.7, "address": "Old Road, Leh 194101",                        "latitude": 34.1626, "longitude": 77.5879, "price_per_night_min": 5000,  "price_per_night_max": 18000},
        {"name": "Stok Palace Heritage Hotel",     "rating": 4.5, "address": "Stok Village, Leh 194101",                    "latitude": 34.0924, "longitude": 77.5758, "price_per_night_min": 4000,  "price_per_night_max": 14000},
        {"name": "Hotel Ladakh Residency",         "rating": 4.2, "address": "Fort Road, Leh 194101",                       "latitude": 34.1638, "longitude": 77.5853, "price_per_night_min": 2000,  "price_per_night_max": 6000},
        {"name": "Zostel Leh",                     "rating": 4.3, "address": "Near Shanti Stupa, Leh 194101",               "latitude": 34.1590, "longitude": 77.5685, "price_per_night_min": 500,   "price_per_night_max": 2000},
    ],

    "srinagar": [
        {"name": "Lalit Grand Palace Srinagar",    "rating": 4.7, "address": "Gupkar Road, Srinagar 190001",                "latitude": 34.0933, "longitude": 74.8485, "price_per_night_min": 8000,  "price_per_night_max": 25000},
        {"name": "Houseboat New Palace",           "rating": 4.5, "address": "Dal Lake, Srinagar 190001",                   "latitude": 34.0837, "longitude": 74.8320, "price_per_night_min": 3000,  "price_per_night_max": 10000},
        {"name": "Hotel Broadway Srinagar",        "rating": 4.2, "address": "Maulana Azad Road, Srinagar 190001",          "latitude": 34.0836, "longitude": 74.8037, "price_per_night_min": 2500,  "price_per_night_max": 7000},
        {"name": "Akbar Dal View Srinagar",        "rating": 4.2, "address": "Dal Lake Boulevard, Srinagar 190001",         "latitude": 34.0850, "longitude": 74.8342, "price_per_night_min": 2000,  "price_per_night_max": 6000},
    ],

    "puri": [
        {"name": "Mayfair Heritage Puri",          "rating": 4.6, "address": "Sea Beach Road, Puri 752001",                 "latitude": 19.8060, "longitude": 85.8328, "price_per_night_min": 4000,  "price_per_night_max": 12000},
        {"name": "Toshali Sands Puri",             "rating": 4.4, "address": "Sipasarubali, Puri 752002",                   "latitude": 19.7890, "longitude": 85.8240, "price_per_night_min": 3000,  "price_per_night_max": 9000},
        {"name": "Hotel Hans Coco Palms",          "rating": 4.2, "address": "Sea Beach Road, Puri 752001",                 "latitude": 19.8043, "longitude": 85.8307, "price_per_night_min": 1500,  "price_per_night_max": 5000},
        {"name": "Zostel Puri",                    "rating": 4.1, "address": "Near Swargadwar, Puri 752001",                "latitude": 19.8028, "longitude": 85.8292, "price_per_night_min": 400,   "price_per_night_max": 1500},
    ],

    "darjeeling": [
        {"name": "Mayfair Darjeeling",             "rating": 4.7, "address": "The Mall, Darjeeling 734101",                 "latitude": 27.0446, "longitude": 88.2621, "price_per_night_min": 6000,  "price_per_night_max": 20000},
        {"name": "Elgin Darjeeling",               "rating": 4.6, "address": "HD Lama Road, Darjeeling 734101",             "latitude": 27.0438, "longitude": 88.2638, "price_per_night_min": 5000,  "price_per_night_max": 16000},
        {"name": "Cedar Inn Darjeeling",           "rating": 4.3, "address": "The Mall, Darjeeling 734101",                 "latitude": 27.0418, "longitude": 88.2652, "price_per_night_min": 2500,  "price_per_night_max": 8000},
        {"name": "Zostel Darjeeling",              "rating": 4.2, "address": "Dr. Zakir Hussain Road, Darjeeling 734101",   "latitude": 27.0413, "longitude": 88.2660, "price_per_night_min": 400,   "price_per_night_max": 1800},
    ],

    "ooty": [
        {"name": "Savoy Hotel Ooty",               "rating": 4.6, "address": "77 Sylks Road, Ooty 643001",                  "latitude": 11.4067, "longitude": 76.7016, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Sterling Ooty Fern Hill",        "rating": 4.4, "address": "Fern Hill, Ooty 643001",                      "latitude": 11.4082, "longitude": 76.7035, "price_per_night_min": 3500,  "price_per_night_max": 10000},
        {"name": "Hotel Tamil Nadu Ooty",          "rating": 4.0, "address": "Charing Cross, Ooty 643001",                  "latitude": 11.4091, "longitude": 76.6953, "price_per_night_min": 1200,  "price_per_night_max": 4000},
        {"name": "YMCA Ooty",                      "rating": 3.9, "address": "Ettines Road, Ooty 643001",                   "latitude": 11.4102, "longitude": 76.6947, "price_per_night_min": 600,   "price_per_night_max": 2000},
    ],

    "mysore": [
        {"name": "Lalitha Mahal Palace Hotel",     "rating": 4.6, "address": "T Narasipur Road, Mysuru 570011",             "latitude": 12.2946, "longitude": 76.6848, "price_per_night_min": 5000,  "price_per_night_max": 18000},
        {"name": "Radisson Blu Mysore",            "rating": 4.4, "address": "3 Nazarabad Mohalla, Mysuru 570010",          "latitude": 12.3065, "longitude": 76.6534, "price_per_night_min": 4000,  "price_per_night_max": 12000},
        {"name": "Hotel Mayura Hoysala",           "rating": 4.0, "address": "2 JLB Road, Mysuru 570005",                   "latitude": 12.3047, "longitude": 76.6561, "price_per_night_min": 1500,  "price_per_night_max": 4500},
    ],

    "pushkar": [
        {"name": "Ananta Spa & Resorts Pushkar",   "rating": 4.5, "address": "Ganahera Road, Pushkar 305022",               "latitude": 26.4978, "longitude": 74.5579, "price_per_night_min": 5000,  "price_per_night_max": 15000},
        {"name": "Hotel Brahma Horizon",           "rating": 4.2, "address": "Old Rangji Mandir Road, Pushkar 305022",      "latitude": 26.4874, "longitude": 74.5501, "price_per_night_min": 2000,  "price_per_night_max": 6000},
        {"name": "Zostel Pushkar",                 "rating": 4.3, "address": "Near Pushkar Lake, Pushkar 305022",           "latitude": 26.4891, "longitude": 74.5521, "price_per_night_min": 400,   "price_per_night_max": 1800},
        {"name": "Hotel White House Pushkar",      "rating": 4.0, "address": "Choti Basti, Pushkar 305022",                 "latitude": 26.4882, "longitude": 74.5533, "price_per_night_min": 800,   "price_per_night_max": 3000},
    ],

}

# ── Aliases for alternate spellings ──────────────────────────────────────────
CURATED_HOTELS["new delhi"]          = CURATED_HOTELS["delhi"]
CURATED_HOTELS["bengaluru"]          = CURATED_HOTELS["bangalore"]
CURATED_HOTELS["bombay"]             = CURATED_HOTELS["mumbai"]
CURATED_HOTELS["calcutta"]           = CURATED_HOTELS["kolkata"]
CURATED_HOTELS["madras"]             = CURATED_HOTELS["chennai"]
CURATED_HOTELS["mysuru"]             = CURATED_HOTELS["mysore"]
CURATED_HOTELS["banaras"]            = CURATED_HOTELS["varanasi"]
CURATED_HOTELS["kashi"]              = CURATED_HOTELS["varanasi"]
CURATED_HOTELS["ladakh"]             = CURATED_HOTELS["leh"]
CURATED_HOTELS["leh ladakh"]         = CURATED_HOTELS["leh"]
CURATED_HOTELS["gulmarg"]            = CURATED_HOTELS["srinagar"]
CURATED_HOTELS["pahalgam"]           = CURATED_HOTELS["srinagar"]
CURATED_HOTELS["ooti"]               = CURATED_HOTELS["ooty"]
CURATED_HOTELS["udhagamandalam"]     = CURATED_HOTELS["ooty"]
CURATED_HOTELS["konark"]             = CURATED_HOTELS["puri"]
CURATED_HOTELS["cape comorin"]       = CURATED_HOTELS["kanyakumari"]
CURATED_HOTELS["kerala"]             = CURATED_HOTELS["munnar"]
CURATED_HOTELS["coorg karnataka"]    = CURATED_HOTELS["coorg"]
CURATED_HOTELS["kodaikanal hills"]   = CURATED_HOTELS["kodaikanal"]


# ── Helper: detect if destination is Indian ──────────────────────────────────
_INDIA_KEYWORDS = [
    "delhi", "mumbai", "goa", "jaipur", "agra", "varanasi", "shimla", "manali",
    "rishikesh", "haridwar", "mussoorie", "ooty", "munnar", "coorg", "mysore",
    "mysuru", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata",
    "amritsar", "udaipur", "jodhpur", "jaisalmer", "leh", "ladakh", "srinagar",
    "darjeeling", "puri", "kanyakumari", "kodaikanal", "pushkar",
    "allahabad", "prayagraj", "lucknow", "bhopal", "indore", "nagpur",
    "visakhapatnam", "vizag", "kochi", "trivandrum", "madurai", "tirupati",
]

def is_indian_destination(destination: str) -> bool:
    d = destination.lower().strip()
    return any(k in d for k in _INDIA_KEYWORDS)


def get_curated_hotels(
    destination: str,
    dest_lat: float,
    dest_lon: float,
    dest_category: str = "default",
    travel_style: str = "moderate",
    max_results: int = 8,
) -> list:
    """
    Return curated hotels for a destination, formatted as standard hotel dicts.
    Primary source for Indian destinations — instant, no API calls needed.
    """
    key = destination.lower().strip()

    # Try exact match first, then partial match
    hotels_raw = CURATED_HOTELS.get(key)
    if not hotels_raw:
        for k, v in CURATED_HOTELS.items():
            if k in key or key in k:
                hotels_raw = v
                break

    if not hotels_raw:
        return []

    result = []
    for h in hotels_raw[:max_results]:
        # Derive price label from travel style if not budget-filtered
        price_min = h["price_per_night_min"]
        price_max = h["price_per_night_max"]
        if travel_style == "budget":
            price_min = min(price_min, 1500)
            price_max = min(price_max, 4000)
        elif travel_style == "luxury":
            price_min = max(price_min, 5000)

        result.append({
            "name":                     h["name"],
            "rating":                   h["rating"],
            "user_ratings_total":       0,
            "address":                  h["address"],
            "latitude":                 h["latitude"],
            "longitude":                h["longitude"],
            "distance_from_arrival_km": round(
                ((h["latitude"] - dest_lat) ** 2 + (h["longitude"] - dest_lon) ** 2) ** 0.5 * 111, 2
            ),
            "price_per_night_min":      price_min,
            "price_per_night_max":      price_max,
            "price_label":              f"₹{price_min:,}–₹{price_max:,}/night",
            "price_source":             "Curated",
            "maps_url":                 f"https://www.google.com/maps/search/?api=1&query={h['latitude']},{h['longitude']}",
            "website":                  "",
            "phone":                    "",
            "tourism_type":             "hotel",
            "place_id":                 f"curated_{h['name'].lower().replace(' ', '_')}",
        })

    print(f"[CuratedHotels] ✅ {len(result)} hotels for '{destination}'")
    return result
