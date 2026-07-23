"""
Transport Live Service — Hybrid real/estimated transport data.

Strategy per mode:
  FLIGHTS:
    - Try Amadeus Flight Offers Search (2,000 free calls/month)
      Get free keys: https://developers.amadeus.com/register
    - Falls back to calibrated fare estimates if Amadeus unavailable
    - Always generates Google Flights / MakeMyTrip booking URLs

  TRAINS (India):
    - Try eRail.in API (free key, real train names + schedules)
    - Falls back to fare slab estimator if unavailable
    - Links to ixigo + IRCTC for booking

  BUSES:
    - No reliable free live API exists
    - RedBus + AbhiBus deep-links with route pre-filled
    - Fare stays Estimated

All results labelled: "Live" | "Estimated"
Never invents prices, routes, or availability.
"""
import os
import time
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

AMADEUS_CLIENT_ID     = os.getenv("AMADEUS_CLIENT_ID", "")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET", "")
ERAIL_API_KEY         = os.getenv("ERAIL_API_KEY", "")

# ── Amadeus OAuth token cache ─────────────────────────────────────────────────
_amadeus_token: Optional[str] = None
_amadeus_token_expiry: float  = 0.0

def _get_amadeus_token() -> Optional[str]:
    """
    Fetch (or return cached) Amadeus OAuth2 access token.
    Tokens last 30 minutes; we refresh 60 s before expiry.
    """
    global _amadeus_token, _amadeus_token_expiry
    if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
        return None
    if _amadeus_token and time.time() < _amadeus_token_expiry:
        return _amadeus_token
    try:
        r = requests.post(
            "https://test.api.amadeus.com/v1/security/oauth2/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     AMADEUS_CLIENT_ID,
                "client_secret": AMADEUS_CLIENT_SECRET,
            },
            timeout=5,
        )
        if r.status_code == 200:
            data = r.json()
            _amadeus_token        = data["access_token"]
            _amadeus_token_expiry = time.time() + data.get("expires_in", 1800) - 60
            print("[TransportLive] ✅ Amadeus token obtained")
            return _amadeus_token
        else:
            print(f"[TransportLive] Amadeus auth failed: {r.status_code} {r.text[:100]}")
            return None
    except Exception as e:
        print(f"[TransportLive] Amadeus auth error: {e}")
        return None

ERAIL_BASE = "https://erail.in/rail/getTrains.aspx"

# ── IATA / station code lookups ───────────────────────────────────────────────

IATA_CODES: Dict[str, str] = {
    "delhi":            "DEL",
    "new delhi":        "DEL",
    "mumbai":           "BOM",
    "goa":              "GOI",
    "bangalore":        "BLR",
    "bengaluru":        "BLR",
    "hyderabad":        "HYD",
    "chennai":          "MAA",
    "kolkata":          "CCU",
    "pune":             "PNQ",
    "ahmedabad":        "AMD",
    "jaipur":           "JAI",
    "lucknow":          "LKO",
    "varanasi":         "VNS",
    "amritsar":         "ATQ",
    "chandigarh":       "IXC",
    "srinagar":         "SXR",
    "leh":              "IXL",
    "ladakh":           "IXL",
    "jammu":            "IXJ",
    "kochi":            "COK",
    "thiruvananthapuram": "TRV",
    "trivandrum":       "TRV",
    "calicut":          "CCJ",
    "kozhikode":        "CCJ",
    "mangalore":        "IXE",
    "coimbatore":       "CJB",
    "madurai":          "IXM",
    "tirupati":         "TIR",
    "visakhapatnam":    "VTZ",
    "vizag":            "VTZ",
    "bhubaneswar":      "BBI",
    "patna":            "PAT",
    "ranchi":           "IXR",
    "raipur":           "RPR",
    "nagpur":           "NAG",
    "bhopal":           "BHO",
    "indore":           "IDR",
    "surat":            "STV",
    "vadodara":         "BDQ",
    "rajkot":           "RAJ",
    "port blair":       "IXZ",
    "agartala":         "IXA",
    "guwahati":         "GAU",
    "imphal":           "IMF",
    "aizawl":           "AJL",
    "shillong":         "SHL",
    "dimapur":          "DMU",
    "darjeeling":       "IXB",
    "bagdogra":         "IXB",
    "shimla":           "SLV",
    "dharamshala":      "DHM",
    "kulu manali":      "KUU",
    "manali":           "KUU",
    "dehradun":         "DED",
    "gorakhpur":        "GOP",
    "kanpur":           "KNU",
    "jabalpur":         "JLR",
    # International
    "dubai":            "DXB",
    "bangkok":          "BKK",
    "singapore":        "SIN",
    "paris":            "CDG",
    "london":           "LHR",
    "new york":         "JFK",
    "tokyo":            "NRT",
    "bali":             "DPS",
    "colombo":          "CMB",
    "kathmandu":        "KTM",
    "muscat":           "MCT",
    "istanbul":         "IST",
    "cairo":            "CAI",
    "amsterdam":        "AMS",
    "rome":             "FCO",
    "sydney":           "SYD",
}

# Indian Railways station codes (for eRail)
RAILWAY_STATION_CODES: Dict[str, str] = {
    "delhi":          "NDLS",
    "new delhi":      "NDLS",
    "old delhi":      "DLI",
    "mumbai":         "CSTM",
    "mumbai central": "BCT",
    "goa":            "MAO",
    "madgaon":        "MAO",
    "jaipur":         "JP",
    "agra":           "AGC",
    "varanasi":       "BSB",
    "bangalore":      "SBC",
    "bengaluru":      "SBC",
    "hyderabad":      "HYB",
    "secunderabad":   "SC",
    "chennai":        "MAS",
    "kolkata":        "HWH",
    "howrah":         "HWH",
    "pune":           "PUNE",
    "ahmedabad":      "ADI",
    "lucknow":        "LKO",
    "amritsar":       "ASR",
    "chandigarh":     "CDG",
    "srinagar":       "SVDK",
    "patna":          "PNBE",
    "ranchi":         "RNC",
    "bhopal":         "BPL",
    "indore":         "INDB",
    "nagpur":         "NGP",
    "raipur":         "R",
    "bhubaneswar":    "BBS",
    "puri":           "PURI",
    "coimbatore":     "CBE",
    "madurai":        "MDU",
    "tirupati":       "TPTY",
    "kochi":          "ERS",
    "thiruvananthapuram": "TVC",
    "visakhapatnam":  "VSKP",
    "vizag":          "VSKP",
    "guwahati":       "GHY",
    "gorakhpur":      "GKP",
    "dehradun":       "DDN",
    "haridwar":       "HW",
    "rishikesh":      "RKSH",
    "mathura":        "MTJ",
    "kanpur":         "CNB",
    "allahabad":      "ALD",
    "prayagraj":      "ALD",
    "kanyakumari":    "CAPE",
    "jodhpur":        "JU",
    "udaipur":        "UDZ",
    "ajmer":          "AII",
    "shimla":         "SML",
    "manali":         "SVDK",   # nearest railhead is Pathankot/Chandigarh
    "darjeeling":     "NJP",    # NJP is nearest mainline station
    "leh":            "JAT",    # nearest railhead is Jammu Tawi
    "ladakh":         "JAT",
}


def _get_iata(city: str) -> Optional[str]:
    return IATA_CODES.get(city.lower().strip())


def _get_station_code(city: str) -> Optional[str]:
    return RAILWAY_STATION_CODES.get(city.lower().strip())


def _try_amadeus_flight_prices(
    origin: str,
    destination: str,
    num_people: int,
    distance_km: float = 0,
) -> Optional[Dict[str, Any]]:
    """
    Fetch real flight prices from Amadeus Flight Offers Search API.
    Free tier: 2,000 calls/month — much more generous than Sky Scrapper.
    Returns fare data or None if unavailable/no flights found.

    Register free at: https://developers.amadeus.com/register
    """
    # Skip short domestic routes — no real direct flights
    if distance_km > 0 and distance_km < 400:
        return None

    token = _get_amadeus_token()
    if not token:
        return None

    orig_iata = _get_iata(origin)
    dest_iata = _get_iata(destination)
    if not orig_iata or not dest_iata:
        print(f"[TransportLive] Amadeus: no IATA for {origin}→{destination}")
        return None

    import datetime
    travel_date = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")

    try:
        r = requests.get(
            "https://test.api.amadeus.com/v2/shopping/flight-offers",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "originLocationCode":      orig_iata,
                "destinationLocationCode": dest_iata,
                "departureDate":           travel_date,
                "adults":                  str(min(num_people, 9)),  # Amadeus max 9
                "currencyCode":            "INR",
                "max":                     10,  # limit results to save quota
                "nonStop":                 "false",
            },
            timeout=8,
        )

        if r.status_code == 401:
            # Token expired mid-request, clear cache so next call refreshes
            global _amadeus_token
            _amadeus_token = None
            print("[TransportLive] Amadeus 401 — token cleared for refresh")
            return None

        if r.status_code == 429:
            print("[TransportLive] Amadeus quota exceeded")
            return None

        if r.status_code != 200:
            print(f"[TransportLive] Amadeus HTTP {r.status_code}: {r.text[:150]}")
            return None

        offers = r.json().get("data", [])
        if not offers:
            print(f"[TransportLive] Amadeus: no offers for {orig_iata}→{dest_iata}")
            return None

        prices = []
        airlines_seen: Dict[str, Dict] = {}

        for offer in offers:
            raw = offer.get("price", {}).get("total")
            if not raw:
                continue
            try:
                # Amadeus returns total for all passengers; divide to get per-person
                total_price = float(raw)
                per_person  = round(total_price / max(num_people, 1))
            except (ValueError, TypeError):
                continue

            prices.append(per_person)

            # Extract airline from first itinerary first segment
            itinerary = (offer.get("itineraries") or [{}])[0]
            segment   = (itinerary.get("segments") or [{}])[0]
            carrier   = segment.get("carrierCode", "")

            # Map IATA carrier code → name
            CARRIER_NAMES = {
                "AI": "Air India", "6E": "IndiGo", "SG": "SpiceJet",
                "UK": "Vistara", "G8": "Go First", "I5": "Air Asia India",
                "IX": "Air India Express", "QP": "Akasa Air",
                "EK": "Emirates", "QR": "Qatar Airways", "EY": "Etihad",
                "SQ": "Singapore Airlines", "TG": "Thai Airways",
                "BA": "British Airways", "LH": "Lufthansa",
            }
            airline_name = CARRIER_NAMES.get(carrier, carrier or "Unknown Airline")
            duration_str = itinerary.get("duration", "")  # e.g. "PT2H30M"

            if airline_name not in airlines_seen:
                airlines_seen[airline_name] = {
                    "airline":    airline_name,
                    "fare_min":   per_person,
                    "fare_max":   per_person,
                    "fare_label": f"₹{per_person:,}",
                    "note":       "One-way per person (indicative, 14 days ahead)",
                    "duration":   duration_str,
                }
            else:
                airlines_seen[airline_name]["fare_min"] = min(airlines_seen[airline_name]["fare_min"], per_person)
                airlines_seen[airline_name]["fare_max"] = max(airlines_seen[airline_name]["fare_max"], per_person)
                lo = airlines_seen[airline_name]["fare_min"]
                hi = airlines_seen[airline_name]["fare_max"]
                airlines_seen[airline_name]["fare_label"] = (
                    f"₹{lo:,}–₹{hi:,}" if lo != hi else f"₹{lo:,}"
                )

        if not prices:
            return None

        prices.sort()
        fare_min = prices[0]
        fare_max = prices[-1]
        airline_list = sorted(airlines_seen.values(), key=lambda x: x["fare_min"])

        print(
            f"[TransportLive] ✅ Amadeus: {orig_iata}→{dest_iata} "
            f"₹{fare_min:,}–₹{fare_max:,} | {len(prices)} offers | {len(airline_list)} airlines"
        )

        return {
            "fare_min":     fare_min,
            "fare_max":     fare_max,
            "fare_label":   f"₹{fare_min:,}–₹{fare_max:,}",
            "price_source": "Live",
            "source_note":  f"Live prices via Amadeus for {travel_date} · {len(prices)} options",
            "sample_count": len(prices),
            "airlines":     airline_list,
        }

    except Exception as e:
        print(f"[TransportLive] Amadeus error: {e}")
        return None


# ── Train: Try eRail.in API ───────────────────────────────────────────────────

def _try_erail_trains(
    origin: str,
    destination: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch real train list between stations from eRail.in.
    Returns list of train dicts with name/number, or None if unavailable.
    API key is free at https://erail.in/data
    """
    if not ERAIL_API_KEY:
        return None

    orig_code = _get_station_code(origin)
    dest_code = _get_station_code(destination)
    if not orig_code or not dest_code:
        return None

    try:
        response = requests.get(
            ERAIL_BASE,
            params={
                "Station1":  orig_code,
                "Station2":  dest_code,
                "Key":       ERAIL_API_KEY,
                "Operator":  "2",   # 2 = all operators
            },
            timeout=6,
        )

        if response.status_code != 200:
            print(f"[TransportLive] eRail HTTP {response.status_code}")
            return None

        # eRail returns pipe-delimited text lines
        lines = response.text.strip().split("\r\n") if response.text else []
        if not lines or lines[0].startswith("0^"):
            return None

        trains = []
        for line in lines[:8]:    # max 8 trains
            parts = line.split("^")
            if len(parts) < 5:
                continue
            trains.append({
                "number":   parts[0],
                "name":     parts[1],
                "from":     parts[2],
                "to":       parts[3],
                "duration": parts[5] if len(parts) > 5 else "",
            })

        if trains:
            print(f"[TransportLive] eRail: {len(trains)} trains {orig_code}→{dest_code}")
            return trains
        return None

    except Exception as e:
        print(f"[TransportLive] eRail error: {e}")
        return None


# ── Build booking deep-links ──────────────────────────────────────────────────

def _google_flights_url(origin: str, destination: str) -> str:
    """Pre-filled Google Flights search URL."""
    orig_iata = _get_iata(origin) or origin.replace(" ", "+")
    dest_iata = _get_iata(destination) or destination.replace(" ", "+")
    return f"https://www.google.com/travel/flights?q=flights+from+{orig_iata}+to+{dest_iata}"


def _makemytrip_flights_url(origin: str, destination: str) -> str:
    """Pre-filled MakeMyTrip flight search URL (good for Indian routes)."""
    orig_iata = _get_iata(origin) or ""
    dest_iata = _get_iata(destination) or ""
    if orig_iata and dest_iata:
        import datetime
        date_str = (datetime.date.today() + datetime.timedelta(days=14)).strftime("%m%d%Y")
        return (
            f"https://www.makemytrip.com/flight/search"
            f"?tripType=O&itinerary={orig_iata}-{dest_iata}-{date_str}"
            f"&paxType=A-1_C-0_I-0&cabinClass=E"
        )
    return "https://www.makemytrip.com/flights/"


def _redbus_url(origin: str, destination: str) -> str:
    """Pre-filled RedBus bus search URL."""
    o = origin.lower().replace(" ", "-")
    d = destination.lower().replace(" ", "-")
    return f"https://www.redbus.in/bus-tickets/{o}-to-{d}"


def _abhibus_url(origin: str, destination: str) -> str:
    """Pre-filled AbhiBus search URL — alternative to RedBus."""
    o = origin.lower().replace(" ", "-")
    d = destination.lower().replace(" ", "-")
    return f"https://www.abhibus.com/bus/{o}-to-{d}"


def _ixigo_trains_url(origin: str, destination: str) -> str:
    """Pre-filled ixigo train search URL."""
    orig_code = _get_station_code(origin) or origin.replace(" ", "+")
    dest_code = _get_station_code(destination) or destination.replace(" ", "+")
    return f"https://www.ixigo.com/trains/results/{orig_code}/{dest_code}"


# ── Main enrichment function ──────────────────────────────────────────────────

def enrich_transport_options(
    options: List[Dict[str, Any]],
    origin: str,
    destination: str,
    num_people: int,
    distance_km: float = 0,
) -> List[Dict[str, Any]]:
    """
    Enrich transport options with live/cached prices when available.
    Falls back to existing estimated data if live APIs fail.
    Always adds proper booking URLs and price_source labels.

    Never replaces existing data — only enriches it.
    """
    enriched = []

    # Try live flight prices via Amadeus (2,000 free calls/month)
    flight_data = _try_amadeus_flight_prices(origin, destination, num_people, distance_km)

    erail_data = _try_erail_trains(origin, destination)

    # Build booking URLs
    gf_url       = _google_flights_url(origin, destination)
    mmt_url      = _makemytrip_flights_url(origin, destination)
    redbus_url   = _redbus_url(origin, destination)
    abhibus_url  = _abhibus_url(origin, destination)
    ixigo_url    = _ixigo_trains_url(origin, destination)

    for opt in options:
        opt = dict(opt)   # copy to avoid mutation
        mode = opt.get("mode", "")

        if "Flight" in mode:
            if flight_data:
                # Only use if prices are in a plausible range (sanity check)
                if 500 <= flight_data["fare_min"] <= 200000:
                    opt["fare_min"]    = flight_data["fare_min"]
                    opt["fare_max"]    = flight_data["fare_max"]
                    opt["fare_label"]  = flight_data["fare_label"]
                    opt["price_source"] = flight_data["price_source"]   # "Live"
                    opt["estimated_fare"] = flight_data["fare_min"]
                    opt["cost_per_person"] = flight_data["fare_min"]
                    opt["cost_total"] = flight_data["fare_min"] * num_people * 2
                    opt["price_note"] = flight_data.get("source_note", "")
                    if flight_data.get("airlines"):
                        opt["airlines"] = flight_data["airlines"]
                    print(f"[TransportLive] Enriched Flight: ₹{flight_data['fare_min']:,} [{flight_data['price_source']}]")
                else:
                    print(f"[TransportLive] Flight price out of range, keeping estimate")
                    opt["price_source"] = "Estimated"
            else:
                opt["price_source"] = opt.get("price_source", "Estimated")

            # Always set Google Flights + MakeMyTrip links
            opt["booking_link"]     = gf_url
            opt["booking_link_alt"] = mmt_url

        elif "Train" in mode:
            if erail_data:
                train_names = ", ".join(
                    f"{t['name']} ({t['number']})"
                    for t in erail_data[:3]
                )
                opt["tip"] = (
                    f"Trains on this route include: {train_names}. "
                    f"Book on IRCTC for exact fares and availability."
                )
                opt["price_source"] = "Estimated"
                opt["real_trains"]  = erail_data
                print(f"[TransportLive] Enriched Train with eRail: {len(erail_data)} trains")
            else:
                opt["price_source"] = opt.get("price_source", "Estimated")

            opt["booking_link"]     = ixigo_url
            opt["booking_link_alt"] = "https://www.irctc.co.in/"

        elif "Bus" in mode:
            opt["price_source"]     = "Estimated"
            opt["booking_link"]     = redbus_url
            opt["booking_link_alt"] = abhibus_url

        elif "Taxi" in mode or "Cab" in mode:
            opt["price_source"]     = "Estimated"
            opt["booking_link_alt"] = "https://www.olacabs.com/"

        elif "Self-Drive" in mode:
            opt["price_source"]     = "Estimated"
            opt["booking_link"]     = opt.get("booking_link", "https://www.zoomcar.com/")

        enriched.append(opt)

    return enriched
