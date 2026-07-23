"""
LLM Service — Hybrid: Groq (primary, free) → Gemini (fallback) → Rule-based (final fallback)

Groq provides free access to Llama 3.3 70B with 14,400 requests/day — no billing needed.
Gemini is kept as a secondary fallback if Groq is unavailable.
"""
import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Groq client ───────────────────────────────────────────────────────────
_groq_client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
        print("[LLMService] ✅ Groq client initialized")
    except Exception as e:
        print(f"[LLMService] Groq init error: {e}")

# ── Gemini client (fallback) ───────────────────────────────────────────────
_gemini_available = False
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_available = True
        print("[LLMService] ✅ Gemini fallback available")
    except Exception:
        pass


def _call_groq(prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
    """Call Groq API with Llama 3.3 70B. Returns raw text."""
    if not _groq_client:
        raise RuntimeError("Groq client not initialized")
    response = _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
    """Call Gemini as fallback. Returns raw text."""
    if not _gemini_available:
        raise RuntimeError("Gemini not available")
    import google.generativeai as genai
    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=temperature, max_output_tokens=max_tokens)
    )
    return resp.text.strip()


def _call_llm(prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
    """Try Groq first, fall back to Gemini, raise if both unavailable."""
    if _groq_client:
        try:
            result = _call_groq(prompt, max_tokens, temperature)
            print("[LLMService] ✅ Groq responded")
            return result
        except Exception as e:
            print(f"[LLMService] Groq error: {e}, trying Gemini...")

    if _gemini_available:
        try:
            result = _call_gemini(prompt, max_tokens, temperature)
            print("[LLMService] ✅ Gemini responded")
            return result
        except Exception as e:
            print(f"[LLMService] Gemini error: {e}")

    raise RuntimeError("Both Groq and Gemini unavailable")


def _clean_json(raw: str) -> str:
    """Strip markdown code fences from LLM response."""
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    return raw.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Generate places for unknown destinations (fallback when curated data missing)
# ─────────────────────────────────────────────────────────────────────────────

def generate_places_with_llm(
    destination: str,
    preferences: List[str] = None,
    max_places: int = 12,
) -> List[Dict[str, Any]]:
    """
    Ask LLM to list top tourist attractions for any destination.
    Used only when Google Places API and curated data both fail.
    """
    prefs_text = ", ".join(preferences) if preferences else "general sightseeing"

    prompt = f"""You are a travel expert. List the top {max_places} real tourist attractions in {destination} for a first-time visitor.

Preferences: {prefs_text}

Return ONLY a valid JSON array, no markdown, no explanation:
[
  {{
    "name": "Exact Real Place Name",
    "rating": 4.5,
    "address": "Full address, {destination}",
    "types": ["tourist_attraction", "historical"],
    "price_level": 1,
    "latitude": 20.1234,
    "longitude": 85.8765,
    "description": "One sentence about why tourists visit this place",
    "best_time": "Morning"
  }}
]

Rules:
- ONLY include real, well-known tourist attractions — never invent names
- Include temples, forts, beaches, parks, monuments, markets — genuine tourist spots
- Ratings 4.0–4.9 for famous places
- Coordinates must be accurate for {destination}
- best_time: one of Morning, Afternoon, Evening, Sunrise, Sunset
- price_level: 0=free, 1=cheap, 2=moderate, 3=expensive
- Return exactly {max_places} places"""

    try:
        raw = _call_llm(prompt, max_tokens=2000, temperature=0.3)
        raw = _clean_json(raw)
        places = json.loads(raw)
        if isinstance(places, list):
            valid = []
            for p in places:
                if p.get("name") and p.get("latitude"):
                    p.setdefault("types", ["tourist_attraction"])
                    p.setdefault("rating", 4.2)
                    p.setdefault("price_level", 1)
                    p.setdefault("description", f"Popular attraction in {destination}")
                    p.setdefault("best_time", "Morning")
                    p.setdefault("address", destination)
                    p.setdefault("photo_url", "")
                    p.setdefault("opening_hours", "9:00 AM – 6:00 PM")
                    p.setdefault("entry_fee", "Free" if p.get("price_level", 0) == 0 else "Check website")
                    p.setdefault("visit_duration_minutes", 60)
                    p.setdefault("crowd_level", "Medium")
                    valid.append(p)
            print(f"[LLMService] Generated {len(valid)} places for '{destination}'")
            return valid[:max_places]
    except json.JSONDecodeError as e:
        print(f"[LLMService] JSON parse error for places: {e}")
    except Exception as e:
        print(f"[LLMService] generate_places error: {e}")
    return []


# ─────────────────────────────────────────────────────────────────────────────
# Main itinerary generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_itinerary_with_llm(
    origin: str,
    destination: str,
    days: int,
    budget: float,
    travel_type: str,
    num_people: int,
    preferences: List[str],
    top_places: List[Dict[str, Any]],
    day_places_for_llm: List[Dict[str, Any]] = None,
    weather_info: Optional[Dict[str, Any]] = None,
    budget_estimate: Optional[Dict[str, Any]] = None,
    transport_mode: Optional[Dict[str, Any]] = None,
    distance_km: float = 0.0,
    llm_only_mode: bool = False,
) -> Dict[str, Any]:
    """
    Generate a complete day-wise itinerary using Groq (primary) or Gemini (fallback).
    Falls back to rule-based generation if both LLMs are unavailable.
    """
    if not _groq_client and not _gemini_available:
        return _fallback_itinerary(origin, destination, days, travel_type, top_places, num_people, preferences)

    # Weather
    weather_text = ""
    if weather_info:
        weather_text = (f"Weather: {weather_info.get('temperature','?')}°C, "
                        f"{weather_info.get('description','')}, "
                        f"Humidity: {weather_info.get('humidity','?')}%")

    # Budget breakdown
    budget_text = ""
    per_day = {}
    if budget_estimate:
        total  = budget_estimate.get("total_estimated", "?")
        per_p  = budget_estimate.get("per_person", "?")
        per_day = budget_estimate.get("per_day", {})
        eff_tier = budget_estimate.get("effective_tier", travel_type)
        t_mode   = budget_estimate.get("transport_mode", "")
        budget_text = (
            f"BUDGET: Total ₹{total} | Per person ₹{per_p} | "
            f"Accommodation/day ₹{per_day.get('accommodation','?')} | "
            f"Food/day ₹{per_day.get('food','?')} | "
            f"Activities/day ₹{per_day.get('activities','?')} | "
            f"Transport: {t_mode} (already deducted) | Style: {eff_tier}"
        )

    # Transport
    transport_text = ""
    if transport_mode:
        mode = transport_mode.get("mode", "") if isinstance(transport_mode, dict) else str(transport_mode)
        dur  = transport_mode.get("duration", "") if isinstance(transport_mode, dict) else ""
        transport_text = f"{mode} ({dur}) from {origin}"

    prefs_text = ", ".join(preferences) if preferences else "General sightseeing, culture, food"
    daily_cost = per_day.get("total_per_day", round(budget / max(days, 1)))

    # ── Build structured per-day prompt instructions ────────────────────────
    # Each day gets explicit slot assignments so LLM never needs to guess

    TIME_SLOTS = ["Morning", "Afternoon", "Evening", "Morning", "Morning", "Afternoon"]

    def _slot_for_place(place: Dict[str, Any], idx: int) -> str:
        """Pick time slot — prefer the place's own best_time, else alternate."""
        bt = place.get("best_time", "")
        if bt in ("Morning", "Sunrise"):   return "Morning"
        if bt in ("Afternoon",):           return "Afternoon"
        if bt in ("Evening", "Sunset"):    return "Evening"
        return TIME_SLOTS[idx % len(TIME_SLOTS)]

    day_prompt_blocks = []
    for dp in (day_places_for_llm or []):
        day_num = dp["day"]
        day_ps  = dp["places"]   # list of place dicts

        if not day_ps:
            # Empty day — only rest/travel, strictly no invented attraction names
            day_prompt_blocks.append(
                f"Day {day_num}: NO attractions assigned for this day. "
                f"Write ONLY about: arrival/departure logistics, hotel check-in/check-out, "
                f"meal breaks at unnamed local restaurants, rest, or travel between points. "
                f"Do NOT mention any attraction names, landmark names, or sightseeing activities. "
                f"Do NOT invent places to visit."
            )
            continue

        # Assign each place to a time slot
        slot_map = {"Morning": [], "Afternoon": [], "Evening": []}
        for i, p in enumerate(day_ps):
            slot = _slot_for_place(p, i)
            slot_map[slot].append(p)

        # If all places pile into one slot, spread them
        if len(slot_map["Morning"]) > 1 and not slot_map["Afternoon"]:
            slot_map["Afternoon"].append(slot_map["Morning"].pop())
        if len(slot_map["Morning"]) > 1 and not slot_map["Evening"]:
            slot_map["Evening"].append(slot_map["Morning"].pop())
        if len(slot_map["Afternoon"]) > 1 and not slot_map["Evening"]:
            slot_map["Evening"].append(slot_map["Afternoon"].pop())

        def fmt_place(p: Dict) -> str:
            free  = " (free entry)" if p.get("price_level") == 0 else ""
            stars = f"⭐{p.get('rating','?')}"
            desc  = p.get("description", "")
            return f'"{p["name"]}" {stars}{free} — {desc}'

        lines = [f"Day {day_num}:"]
        for slot in ("Morning", "Afternoon", "Evening"):
            ps = slot_map[slot]
            if ps:
                place_descs = " | ".join(fmt_place(p) for p in ps)
                lines.append(f"  {slot}: Visit {place_descs}")
            else:
                # Empty slot — give a non-inventive instruction
                if slot == "Morning":
                    lines.append(f"  Morning: Describe arrival / check-in / breakfast "
                                  f"near the places assigned to this day.")
                elif slot == "Afternoon":
                    lines.append(f"  Afternoon: Describe lunch at a local restaurant "
                                  f"near the morning attractions and optional rest.")
                else:
                    lines.append(f"  Evening: Describe dinner and evening ambience "
                                  f"in the {destination} area near today's attractions.")

        # Single-place day: extra instruction
        if len(day_ps) == 1:
            p = day_ps[0]
            lines.append(
                f"  NOTE: Only 1 attraction for this day. "
                f"Expand description of \"{p['name']}\" (explore surroundings, "
                f"nearby streets, local food). Do NOT invent other landmark names."
            )

        day_prompt_blocks.append("\n".join(lines))

    per_day_block = "\n\n".join(day_prompt_blocks) if day_prompt_blocks else (
        "\n".join([
            f"- {p.get('name','?')} | ⭐{p.get('rating','?')} | {p.get('description','')}"
            for p in top_places[:15]
        ]) if top_places else f"Use your knowledge of real attractions in {destination}."
    )

    # ── Build day_plans JSON template for the prompt ─────────────────────────
    day_template_lines = []
    for dp in (day_places_for_llm or [{"day": i+1, "places": []} for i in range(days)]):
        day_num = dp["day"]
        ps      = dp["places"]
        names   = [f'"{p["name"]}"' for p in ps] if ps else []
        names_str = ", ".join(names) if names else '[]'
        day_template_lines.append(
            f'    {{"day": {day_num}, "date_label": "Day {day_num} – <theme>", '
            f'"narrative": "<2-3 sentences>", '
            f'"morning": "<describe morning slot>", '
            f'"afternoon": "<describe afternoon slot>", '
            f'"evening": "<describe evening slot>", '
            f'"estimated_cost": {daily_cost}, '
            f'"place_names": [{names_str}]}}'
        )
    day_template = ",\n".join(day_template_lines)

    prompt = f"""You are a senior travel writer. Create a detailed {days}-day itinerary for {destination}.

TRIP:
- From: {origin} | {num_people} traveler(s) | Style: {travel_type} | Budget: ₹{budget:,.0f}
- Interests: {prefs_text}
- Transport: {transport_text}
- {weather_text}
- {budget_text}

━━━ DAILY ATTRACTION ASSIGNMENTS ━━━
These are the ONLY real attractions to mention. Describe them — do not rename or replace them.

{per_day_block}

━━━ OUTPUT FORMAT ━━━
Return ONLY valid JSON (no markdown, no explanation):
{{
  "itinerary_summary": "2-3 sentences covering transport, budget, travel style and highlights",
  "travel_tips": [
    "Tip 1 specific to {destination} (safety/etiquette)",
    "Tip 2 (best local food to try)",
    "Tip 3 (transport within {destination})",
    "Tip 4 (best time/season)",
    "Tip 5 (money/budget saving)"
  ],
  "day_plans": [
{day_template}
  ]
}}

━━━ STRICT RULES ━━━
1. Generate EXACTLY {days} day plans (day 1 through day {days})
2. place_names must list ONLY the attraction names shown in the daily assignments above
3. morning/afternoon/evening text must be about THOSE specific places — never other landmarks
4. If a day has only 1 attraction: describe it in depth (history, what to see, nearby streets/food) — do NOT invent other attraction names
5. If a slot has no attraction: write about food, local streets, rest, or travel logistics — NO invented landmark names whatsoever
6. If a day has NO attractions: write only about travel logistics, meals and rest — do NOT mention any attraction or landmark by name
7. Day 1 morning: mention arriving by {(transport_text[:60] + '...') if len(transport_text) > 60 else transport_text}, hotel check-in
8. Day {days} evening: mention departure preparation
9. estimated_cost = ₹{daily_cost} for EVERY day (do not change this number)
10. Never use names like "City Tour", "Local Viewpoint", "Heritage Walk", "Cultural District", "Local Market", "Night Bazaar" unless those exact names appear in the assignment above """

    try:
        raw = _call_llm(prompt, max_tokens=5000, temperature=0.7)
        raw = _clean_json(raw)
        result = json.loads(raw)
        print(f"[LLMService] ✅ Generated itinerary for {destination}")
        return result
    except json.JSONDecodeError as e:
        print(f"[LLMService] JSON parse error: {e}")
        return _fallback_itinerary(origin, destination, days, travel_type, top_places, num_people, preferences)
    except Exception as e:
        print(f"[LLMService] Error: {e}")
        return _fallback_itinerary(origin, destination, days, travel_type, top_places, num_people, preferences)


def _fallback_itinerary(
    origin: str,
    destination: str,
    days: int,
    travel_type: str,
    places: List[Dict[str, Any]],
    num_people: int,
    preferences: List[str],
) -> Dict[str, Any]:
    """
    Rule-based itinerary when both LLMs are unavailable.
    Uses ONLY verified place names from the `places` list.
    Never invents attraction names — fills empty slots with food/rest descriptions.
    """
    places_per_day = 3
    day_plans = []
    place_idx = 0

    for day in range(1, days + 1):
        # Collect up to places_per_day verified place names for this day
        day_place_names = []
        for _ in range(places_per_day):
            if place_idx < len(places):
                pname = places[place_idx].get("name", "")
                if pname:
                    day_place_names.append(pname)
                place_idx += 1

        has_places = len(day_place_names) > 0
        p1 = day_place_names[0] if has_places else None
        p2 = day_place_names[1] if len(day_place_names) > 1 else None

        if day == 1:
            label = f"Day {day} – Arrival & First Impressions"
            if p1:
                morning = (
                    f"Arrive in {destination} and check in to your accommodation. "
                    f"Head to {p1} — visit early morning to beat the crowds. "
                    f"Have breakfast at a local cafe nearby."
                )
            else:
                morning = (
                    f"Arrive in {destination} and check in to your accommodation. "
                    f"Freshen up and take a short walk through the local neighbourhood."
                )
            if p2:
                afternoon = (
                    f"Explore {p2} in the afternoon. Try local cuisine for lunch — "
                    f"ask locals for the best nearby restaurants."
                )
            else:
                afternoon = (
                    f"Afternoon at leisure. Explore the local market or nearby streets. "
                    f"Have lunch at a restaurant of your choice."
                )
            evening = (
                f"Enjoy the evening atmosphere of {destination}. "
                f"Try local street food and soak in the surroundings."
            )
        elif day == days:
            label = f"Day {day} – Final Exploration & Departure"
            if p1:
                morning = (
                    f"Early morning visit to {p1}. Pick up souvenirs and local handicrafts."
                )
            else:
                morning = f"Leisurely morning in {destination}. Pick up any remaining souvenirs."
            if p2:
                afternoon = (
                    f"Lunch at a popular local restaurant. Visit {p2} if time permits "
                    f"before heading to your departure point."
                )
            else:
                afternoon = f"Lunch at a local restaurant. Pack up and prepare for your return journey."
            evening = f"Head back from {destination}. Reflect on the experiences from your trip."
        else:
            label = f"Day {day} – Exploring {destination}"
            if p1:
                morning = (
                    f"Start the day with a visit to {p1}. "
                    f"Have breakfast before heading out. Carry water and sunscreen."
                )
            else:
                morning = (
                    f"Leisurely morning in {destination}. Have breakfast at a local café "
                    f"and explore the neighbourhood."
                )
            if p2:
                afternoon = (
                    f"Explore {p2} after a light lunch at a local eatery. "
                    f"This is one of the must-visit spots in {destination}."
                )
            else:
                afternoon = (
                    f"Afternoon exploring the local area. Have lunch at a restaurant "
                    f"and take it easy before the evening."
                )
            evening = (
                f"Evening in {destination}. Try local street food and relax after a full day."
            )

        day_plans.append({
            "day": day,
            "date_label": label,
            "narrative": (
                f"A day of authentic experiences in {destination}."
                if has_places else
                f"A relaxed day in {destination} — explore at your own pace."
            ),
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "estimated_cost": 0,  # overridden by router
            "place_names": day_place_names,
        })

    # If zero places were available, set a clear status message
    no_places_note = ""
    if not places:
        no_places_note = (
            f" Note: No verified tourist attractions were found in our database "
            f"for {destination}. The itinerary describes a general visit experience."
        )

    return {
        "itinerary_summary": (
            f"Discover {destination} over {days} days from {origin}. "
            f"This {travel_type} trip covers local sights and authentic cultural experiences "
            f"for {num_people} traveler{'s' if num_people > 1 else ''}.{no_places_note}"
        ),
        "travel_tips": [
            f"Book accommodation in {destination} at least 1 week in advance",
            "Carry cash — many local attractions and eateries don't accept cards",
            "Use Google Maps offline — download the area before your trip",
            "Try local street food — it's the most authentic and affordable option",
            "Start sightseeing early (before 9 AM) to avoid crowds and heat",
        ],
        "day_plans": day_plans,
    }
