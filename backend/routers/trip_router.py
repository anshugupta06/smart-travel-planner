"""
Trip Router: Main endpoint for generating travel itineraries.
Orchestrates: Places → ML Ranking → Route Optimization → Budget (validated) → LLM Itinerary
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import math

from database import get_db
from models import TripRequest, TripResponse, DayPlan, Place, WeatherInfo, BudgetEstimate, BudgetFitResult, TransportOption, TripRecord, ArrivalPoint, Hotel, LocalTransit
from services.places_service import get_places_for_destination, geocode_nominatim
from services.weather_service import get_weather_for_destination
from services.arrival_service import get_arrival_point
from services.hotel_service import search_hotels_near_arrival
from services.ml_service import (
    score_and_rank_attractions, optimize_route,
    distribute_places_by_day, predict_budget,
    get_transport_options, _places_per_day_target,
    compute_local_route,
)
from services.llm_service import generate_itinerary_with_llm
from utils.helpers import geocode_city, normalize_city_name, haversine_distance, get_route_distance

router = APIRouter(prefix="/api", tags=["Trip Planning"])


def _save_trip_record(db: Session, req: TripRequest, response: TripResponse) -> int:
    """Save trip to DB synchronously. Returns the new record ID."""
    try:
        # Save response_json without id first (id not known yet)
        record = TripRecord(
            origin=req.origin,
            destination=req.destination,
            budget=req.budget,
            days=req.days,
            travel_type=req.travel_type,
            num_people=req.num_people,
            preferences=req.preferences,
            response_json=response.model_dump_json(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        # Now update response_json with the real id
        import json
        try:
            rj = json.loads(record.response_json)
            rj["id"] = record.id
            record.response_json = json.dumps(rj)
            db.commit()
        except Exception:
            pass
        print(f"[TripRouter] Saved trip #{record.id} for {req.destination}")
        return record.id
    except Exception as e:
        print(f"[TripRouter] DB save error: {e}")
        db.rollback()
        return None


def _resolve_coordinates(place_name: str):
    """Try helpers dict first, then Nominatim."""
    coords = geocode_city(place_name)
    if coords:
        return coords
    geo = geocode_nominatim(place_name)
    if geo:
        return (geo["lat"], geo["lon"])
    return None


@router.post("/plan-trip", response_model=TripResponse)
async def plan_trip(
    request: TripRequest,
    db: Session = Depends(get_db),
):
    destination = normalize_city_name(request.destination)
    origin      = normalize_city_name(request.origin)

    # ── Step 1: Validate destination ─────────────────────────────────────────
    dest_coords = _resolve_coordinates(request.destination)
    if dest_coords is None:
        raise HTTPException(status_code=422,
                            detail=f"Could not locate '{request.destination}'. Try 'Paris, France' style.")

    # ── Step 2: Fetch REAL places (never invent names) ────────────────────────
    raw_places = get_places_for_destination(
        request.destination,
        preferences=request.preferences,
        max_places=15,
    )
    # Last resort: ask LLM to name real attractions if all databases are empty
    if len(raw_places) == 0:
        try:
            from services.llm_service import generate_places_with_llm
            llm_places = generate_places_with_llm(
                destination=request.destination,
                preferences=request.preferences,
                max_places=10,
            )
            if llm_places:
                print(f"[Router] LLM generated {len(llm_places)} places for '{destination}' as last resort")
                raw_places = llm_places
        except Exception as _lpe:
            print(f"[Router] LLM place generation failed: {_lpe}")

    llm_only_mode = len(raw_places) == 0

    # ── Step 3: ML Ranking + Route Optimization ───────────────────────────────
    if not llm_only_mode:
        ranked_places    = score_and_rank_attractions(raw_places, travel_type=request.travel_type, preferences=request.preferences)
        optimized_places = optimize_route(ranked_places, dest_coords[0], dest_coords[1])
    else:
        optimized_places = []

    # ── Step 4: Weather ───────────────────────────────────────────────────────
    weather_data = get_weather_for_destination(request.destination)
    weather_info = WeatherInfo(
        temperature=weather_data.get("temperature", 25.0),
        feels_like =weather_data.get("feels_like",  23.0),
        description=weather_data.get("description", "Clear sky"),
        humidity   =weather_data.get("humidity",    60),
        wind_speed =weather_data.get("wind_speed",  10.0),
        icon       =weather_data.get("icon",        "☀️"),
        forecast   =weather_data.get("forecast",    []),
    )

    # ── Step 5: Transport + Arrival Point + Budget ────────────────────────────
    distance_km, _ = get_route_distance(request.origin, request.destination)

    transport_options_raw = get_transport_options(
        origin=request.origin, destination=request.destination,
        distance_km=distance_km, num_people=request.num_people,
        num_days=request.days,
        preferred=request.preferred_transport,
    )

    # Enrich with live/cached prices where available
    try:
        from services.transport_live_service import enrich_transport_options
        transport_options_raw = enrich_transport_options(
            transport_options_raw, request.origin, request.destination, request.num_people,
            distance_km=distance_km,
        )
    except Exception as _te:
        print(f"[Router] Transport enrichment skipped: {_te}")

    # Determine arrival point from selected transport mode
    selected_mode_str = request.preferred_transport or (
        transport_options_raw[0]["mode"] if transport_options_raw else "Car"
    )
    arrival_point_data = get_arrival_point(request.destination, selected_mode_str)
    arrival_point_obj  = ArrivalPoint(
        name      = arrival_point_data["name"],
        latitude  = arrival_point_data["latitude"],
        longitude = arrival_point_data["longitude"],
        address   = arrival_point_data["address"],
        type      = arrival_point_data["type"],
        maps_url  = arrival_point_data["maps_url"],
        verified  = arrival_point_data["verified"],
        source    = arrival_point_data["source"],
    )
    print(f"[Router] Arrival point: {arrival_point_obj.name} ({arrival_point_obj.type})")

    transport_option_objs = [
        TransportOption(
            mode             = o["mode"],
            emoji            = o["emoji"],
            duration         = o["duration"],
            cost_per_person  = o["cost_per_person"],
            cost_total       = o["cost_total"],
            fare_min         = o.get("fare_min",   o["cost_per_person"]),
            fare_max         = o.get("fare_max",   o["cost_per_person"]),
            fare_label       = o.get("fare_label", ""),
            price_source     = o.get("price_source", "Estimated"),
            price_note       = o.get("price_note", ""),
            available        = o["available"],
            recommended      = o["recommended"],
            tip              = o["tip"],
            booking_link     = o["booking_link"],
            booking_link_alt = o.get("booking_link_alt", ""),
        )
        for o in transport_options_raw
    ]

    # ── CRITICAL: use the actual effective tier ──
    # Use exact hotel price if the frontend passed it; otherwise fall back to matrix
    hotel_cost_actual = 0.0
    hotel_name_actual = ""
    if getattr(request, 'selected_hotel_name', None):
        hotel_name_actual = request.selected_hotel_name
        if getattr(request, 'selected_hotel_price_per_night', None):
            # Exact price passed from the hotel card the user selected
            hotel_cost_actual = float(request.selected_hotel_price_per_night) * request.days
            print(f"[Router] Hotel exact price: {hotel_name_actual} ₹{request.selected_hotel_price_per_night}/night × {request.days} nights = ₹{hotel_cost_actual:,}")
        else:
            # Fall back to destination matrix minimum
            from services.hotel_service import PRICE_RANGES
            from services.ml_service import _classify_destination
            cat   = _classify_destination(request.destination)
            style = request.travel_type if request.travel_type in ("budget", "moderate", "luxury") else "moderate"
            lo, _hi = PRICE_RANGES.get(cat, PRICE_RANGES["default"]).get(style, (1500, 5000))
            hotel_cost_actual = lo * request.days
            print(f"[Router] Hotel matrix fallback: {hotel_name_actual} ₹{lo}/night × {request.days} nights = ₹{hotel_cost_actual:,}")

    budget_data = predict_budget(
        origin=request.origin, destination=request.destination,
        num_days=request.days, num_people=request.num_people,
        travel_type=request.travel_type,
        distance_km=distance_km,
        preferred_transport=request.preferred_transport,
        transport_options=transport_options_raw,
        user_budget=request.budget,
        hotel_cost_actual=hotel_cost_actual,
        hotel_name_actual=hotel_name_actual,
    )

    bf            = budget_data.get("budget_fit", {})
    effective_tier = bf.get("actual_tier", request.travel_type) if bf else request.travel_type

    # ── Build per-day cost distribution based on effective_days ──────────────
    # Note: effective_days computed after place distribution, use request.days for now
    # Will be recalculated below after we know effective_days
    total_trip_cost   = budget_data["total_estimated"]
    transport_cost    = budget_data["transport"]
    daily_budget_pool = (total_trip_cost - transport_cost) / max(request.days, 1)

    selected_transport_info = {"mode": budget_data.get("transport_mode", request.preferred_transport or ""),
                                "tip": "", "duration": ""}
    for opt in transport_options_raw:
        if opt["mode"].lower() == budget_data.get("transport_mode", "").lower():
            selected_transport_info = opt
            break

    # ── Step 6: Distribute places FIRST, then pass to LLM ───────────────────
    total_places = len(optimized_places)

    # Determine effective trip days:
    # If we have fewer verified places than requested days, cap days to places
    # (so no day is ever left completely empty of verified attractions).
    # Exception: if we have 0 places entirely, keep days as-is and let LLM
    # generate a travel/rest narrative only.
    if total_places == 0:
        effective_days = request.days   # will produce rest/travel days
        print(f"[Router] Zero places — keeping {effective_days} days as rest/travel days")
    elif total_places < request.days:
        effective_days = total_places
        print(f"[Router] Only {total_places} place(s) — capping to {effective_days} day(s)")
    else:
        effective_days = request.days

    # Duration-aware per-day target (uses requirements schedule)
    if total_places == 0:
        places_per_day = 0
    else:
        places_per_day = _places_per_day_target(effective_days, total_places)

    print(f"[Router] {total_places} places, {effective_days} days, "
          f"target {places_per_day} places/day")

    day_buckets = distribute_places_by_day(
        optimized_places, effective_days, places_per_day
    )

    # Recalculate per-day costs now that we know effective_days
    daily_budget_pool = (total_trip_cost - transport_cost) / max(effective_days, 1)
    day_costs = []
    for i in range(effective_days):
        if i == 0 or i == effective_days - 1:
            day_costs.append(round(daily_budget_pool * 0.9, 2))
        else:
            day_costs.append(round(daily_budget_pool, 2))
    if day_costs:
        drift = round(total_trip_cost - transport_cost - sum(day_costs), 2)
        day_costs[-1] = round(day_costs[-1] + drift, 2)

    # Build structured per-day place list to pass to LLM
    day_places_for_llm = []
    for i, bucket in enumerate(day_buckets):
        day_places_for_llm.append({
            "day": i + 1,
            "places": [
                {
                    "name":        p.get("name", ""),
                    "rating":      p.get("rating", 0),
                    "types":       p.get("types", [])[:2],
                    "best_time":   p.get("best_time", "Morning"),
                    "description": p.get("description", ""),
                    "price_level": p.get("price_level", 1),
                }
                for p in bucket
            ]
        })
        print(f"[Router] Day {i+1} places assigned: {[p.get('name') for p in bucket]}")

    # ── Step 7: LLM Itinerary Generation ─────────────────────────────────────
    per_day_breakdown = {
        "accommodation": round(budget_data["accommodation"] / max(effective_days, 1), 2),
        "food":          round(budget_data["food"]          / max(effective_days, 1), 2),
        "activities":    round(budget_data["activities"]    / max(effective_days, 1), 2),
        "misc":          round(budget_data["misc"]          / max(effective_days, 1), 2),
        "total_per_day": round(daily_budget_pool, 2),
    }
    budget_data_for_llm = {**budget_data, "per_day": per_day_breakdown, "effective_tier": effective_tier}

    llm_result = generate_itinerary_with_llm(
        origin=request.origin,
        destination=request.destination,
        days=effective_days,
        budget=request.budget,
        travel_type=effective_tier,
        num_people=request.num_people,
        preferences=request.preferences,
        top_places=optimized_places,
        day_places_for_llm=day_places_for_llm,
        weather_info=weather_data,
        budget_estimate=budget_data_for_llm,
        transport_mode=selected_transport_info,
        distance_km=distance_km,
        llm_only_mode=llm_only_mode,
    )

    llm_day_plans  = llm_result.get("day_plans", [])

    # ── Step 8: Build DayPlan objects with EXACT validated daily costs ────────
    seen_place_names: set = set()
    day_plans = []

    for i in range(effective_days):
        day_num  = i + 1
        llm_day  = llm_day_plans[i] if i < len(llm_day_plans) else {}
        bucket   = day_buckets[i]   if i < len(day_buckets)    else []

        day_place_objs = []
        if bucket:
            for p in bucket:
                pname = p.get("name", "")
                if pname.lower() in seen_place_names:
                    continue          
                seen_place_names.add(pname.lower())
                day_place_objs.append(Place(
                    name=pname, rating=p.get("rating", 0.0),
                    address=p.get("address", ""),
                    types=p.get("types", []),
                    price_level=p.get("price_level", 0),
                    latitude=p.get("latitude", 0.0), longitude=p.get("longitude", 0.0),
                    description=p.get("description", ""), best_time=p.get("best_time", "Morning"),
                    popularity_score=p.get("popularity_score", 0.0),
                    opening_hours=p.get("opening_hours", ""),
                    entry_fee=p.get("entry_fee", ""),
                    visit_duration_minutes=p.get("visit_duration_minutes", 60),
                    crowd_level=p.get("crowd_level", "Medium"),
                ))
        elif llm_day.get("place_names"):
            # Only accept place_names that appear in our verified optimized_places list
            verified_names_lower = {p.get("name", "").lower() for p in optimized_places}
            for pname in llm_day["place_names"][:4]:
                if not pname or len(pname.strip()) < 3:
                    continue
                if pname.lower() in seen_place_names:
                    continue
                # Reject names invented by LLM that aren't in our verified list
                if optimized_places and pname.lower() not in verified_names_lower:
                    print(f"[Router] Rejected unverified LLM place: '{pname}' (not in verified list)")
                    continue
                seen_place_names.add(pname.lower())
                # Look up full details from optimized_places if available
                matched = next((p for p in optimized_places if p.get("name", "").lower() == pname.lower()), None)
                if matched:
                    day_place_objs.append(Place(
                        name=matched.get("name", pname),
                        rating=matched.get("rating", 4.2),
                        address=matched.get("address", destination),
                        types=matched.get("types", ["tourist_attraction"]),
                        price_level=matched.get("price_level", 0),
                        latitude=matched.get("latitude", 0.0),
                        longitude=matched.get("longitude", 0.0),
                        description=matched.get("description", f"A must-visit attraction in {destination}"),
                        best_time=matched.get("best_time", "Morning"),
                        popularity_score=matched.get("popularity_score", 0.0),
                        opening_hours=matched.get("opening_hours", ""),
                        entry_fee=matched.get("entry_fee", ""),
                        visit_duration_minutes=matched.get("visit_duration_minutes", 60),
                        crowd_level=matched.get("crowd_level", "Medium"),
                    ))
                else:
                    day_place_objs.append(Place(
                        name=pname, rating=4.2, address=destination,
                        types=["tourist_attraction"],
                        description=f"A must-visit attraction in {destination}",
                        best_time="Morning",
                    ))

        # ── Compute local route segments between stops ────────────────────────
        raw_places_for_route = [
            {"name": p.name, "latitude": p.latitude, "longitude": p.longitude}
            for p in day_place_objs
        ]
        try:
            segs_raw = compute_local_route(
                raw_places_for_route, destination,
                hotel_name=request.selected_hotel_name or "Your Hotel"
            )
            route_segs = [
                LocalTransit(
                    from_name    = s.get("from_name", ""),
                    to_name      = s.get("to_name", ""),
                    mode         = s.get("mode", ""),
                    emoji        = s.get("emoji", ""),
                    distance_km  = s.get("distance_km", 0.0),
                    duration_min = s.get("duration_min", 0),
                    cost_inr     = s.get("cost_inr", 0),
                    note         = s.get("note", ""),
                )
                for s in segs_raw
            ]
        except Exception as _re:
            print(f"[Router] compute_local_route error day {day_num}: {_re}")
            route_segs = []

        # ── Post-LLM text validation: sanitize day narrative ─────────────────
        # Check if LLM invented attraction names not in the verified list for this day
        verified_day_names = {p.name.lower() for p in day_place_objs}
        all_verified_lower  = {p.get("name", "").lower() for p in optimized_places}

        def _sanitize_text(text: str, day_num: int) -> str:
            """
            If LLM text is present and places are assigned to this day,
            ensure the text is not empty. If text is empty, generate a
            safe rule-based narrative referencing only verified places.
            """
            if text and text.strip():
                return text.strip()
            return ""

        safe_morning   = _sanitize_text(llm_day.get("morning",   ""), day_num)
        safe_afternoon = _sanitize_text(llm_day.get("afternoon", ""), day_num)
        safe_evening   = _sanitize_text(llm_day.get("evening",   ""), day_num)

        # If day has verified places but LLM produced no morning/afternoon/evening,
        # generate a safe rule-based fallback from the verified place names
        if day_place_objs and not safe_morning:
            p0 = day_place_objs[0].name
            safe_morning = (
                f"Arrive at {p0}. Explore the surroundings and take your time — "
                f"this is one of the best attractions in {destination}."
                if day_num > 1 else
                f"Arrive in {destination} and check in to your accommodation. "
                f"Head to {p0} for your first experience of the destination."
            )
        if day_place_objs and not safe_afternoon:
            p_mid = day_place_objs[min(1, len(day_place_objs)-1)].name
            safe_afternoon = (
                f"Continue exploring {p_mid} and the surrounding area. "
                f"Have lunch at a local restaurant nearby."
            )
        if not safe_evening:
            if day_num == effective_days:
                safe_evening = f"Wrap up your visit to {destination}. Pack your bags and prepare for departure."
            else:
                safe_evening = f"Enjoy the evening atmosphere of {destination}. Try local street food and relax."

        day_plans.append(DayPlan(
            day=day_num,
            date_label=llm_day.get("date_label", f"Day {day_num}"),
            places=day_place_objs,
            narrative=llm_day.get("narrative", ""),
            morning  =safe_morning,
            afternoon=safe_afternoon,
            evening  =safe_evening,
            estimated_cost=day_costs[i],
            route_segments=route_segs,
        ))

    # ── Step 9: Top places (real data only, no dupes) ─────────────────────────
    top_place_objs = [
        Place(name=p.get("name",""), rating=p.get("rating",0.0),
              address=p.get("address",""),
              types=p.get("types",[]), price_level=p.get("price_level",0),
              latitude=p.get("latitude",0.0), longitude=p.get("longitude",0.0),
              description=p.get("description",""), best_time=p.get("best_time","Morning"),
              popularity_score=p.get("popularity_score",0.0),
              opening_hours=p.get("opening_hours",""),
              entry_fee=p.get("entry_fee",""),
              visit_duration_minutes=p.get("visit_duration_minutes",60),
              crowd_level=p.get("crowd_level","Medium"))
        for p in optimized_places[:6]
    ]

    # ── Step 10: Build BudgetEstimate with BudgetFitResult ────────────────────
    fit_obj = None
    if bf:
        fit_obj = BudgetFitResult(
            fits_budget      =bf.get("fits_budget", True),
            original_estimate=bf.get("original_estimate", total_trip_cost),
            adjusted_estimate=bf.get("adjusted_estimate", total_trip_cost),
            budget_provided  =bf.get("budget_provided",   request.budget),
            shortfall        =bf.get("shortfall",    0.0),
            savings          =bf.get("savings",      0.0),
            utilization_pct  =bf.get("utilization_pct", 0.0),
            adjustments_made =bf.get("adjustments_made", []),
            recommendation   =bf.get("recommendation",   ""),
            upgrade_plan     =bf.get("upgrade_plan"),
        )

    budget_estimate = BudgetEstimate(
        total_estimated            = total_trip_cost,
        total_min                  = budget_data.get("total_min",   round(total_trip_cost * 0.85)),
        total_max                  = budget_data.get("total_max",   round(total_trip_cost * 1.25)),
        per_person                 = budget_data["per_person"],
        original_budget            = request.budget,
        remaining_budget           = budget_data.get("remaining_budget", round(request.budget - total_trip_cost)),
        over_budget                = budget_data.get("over_budget", total_trip_cost > request.budget),
        accommodation              = budget_data["accommodation"],
        hotel_name                 = budget_data.get("hotel_name", ""),
        hotel_cost_source          = budget_data.get("hotel_cost_source", "Estimated"),
        food                       = budget_data["food"],
        transport                  = transport_cost,
        intercity_transport        = budget_data.get("intercity_transport", 0),
        intercity_transport_mode   = budget_data.get("intercity_transport_mode", budget_data.get("transport_mode", "")),
        intercity_transport_label  = budget_data.get("intercity_transport_label", "Estimated"),
        local_transport            = budget_data.get("local_transport", 0),
        activities                 = budget_data["activities"],
        entry_tickets              = budget_data.get("entry_tickets", round(budget_data["activities"] * 0.6)),
        shopping                   = budget_data.get("shopping",      round(budget_data["activities"] * 0.2)),
        misc                       = budget_data["misc"],
        budget_tips                = budget_data["budget_tips"],
        transport_mode             = budget_data.get("transport_mode", ""),
        daily_breakdown            = budget_data.get("daily_breakdown"),
        budget_fit                 = fit_obj,
    )

    from datetime import datetime, timezone

    # Build data_sources provenance map
    data_sources = {
        "attractions": "google_places" if not llm_only_mode else "curated",
        "weather":     "openweathermap",
        "transport":   "estimated",
        "hotels":      "openstreetmap",
        "itinerary":   "llm_generated",
        "budget":      "estimated",
    }

    response = TripResponse(
        destination      = destination,
        origin           = origin,
        days             = request.days,
        travel_type      = effective_tier,
        num_people       = request.num_people,
        budget_provided  = request.budget,
        weather          = weather_info,
        day_plans        = day_plans,
        budget_estimate  = budget_estimate,
        transport_options= transport_option_objs,
        arrival_point    = arrival_point_obj,
        travel_tips      = llm_result.get("travel_tips", []),
        top_places       = top_place_objs,
        itinerary_summary= llm_result.get("itinerary_summary", ""),
        status           = "success",
        planning_mode    = getattr(request, "planning_mode", "live"),
        data_sources     = data_sources,
        generated_at     = datetime.now(timezone.utc).isoformat(),
        message          = (
            f"Itinerary for {destination} — {request.days} days · "
            f"{budget_data.get('transport_mode', '')} · "
            f"Total ₹{total_trip_cost:,.0f}"
        ),
    )

    # Save synchronously so we get the DB ID back for rating/sharing
    trip_id = _save_trip_record(db, request, response)
    if trip_id:
        response.id = trip_id

    return response


@router.post("/check-budget")
async def check_budget(request: TripRequest):
    """
    Step 4 of planning flow: validate budget BEFORE generating itinerary.
    """
    dest_coords = _resolve_coordinates(request.destination)
    if dest_coords is None:
        raise HTTPException(status_code=422, detail=f"Could not locate '{request.destination}'.")

    distance_km, _ = get_route_distance(request.origin, request.destination)

    transport_options_raw = get_transport_options(
        origin=request.origin,
        destination=request.destination,
        distance_km=distance_km,
        num_people=request.num_people,
        num_days=request.days,
        preferred=request.preferred_transport,
    )

    selected_transport = None
    transport_cost = 0.0
    for opt in transport_options_raw:
        if request.preferred_transport and request.preferred_transport.lower() in opt["mode"].lower():
            selected_transport = opt
            transport_cost = opt["cost_total"]
            break
    if not selected_transport and transport_options_raw:
        selected_transport = transport_options_raw[0]
        transport_cost = selected_transport["cost_total"]

    remaining_budget = request.budget - transport_cost

    levels = ["luxury", "moderate", "budget"]
    if request.travel_type == "budget":
        levels = ["budget"]
    elif request.travel_type == "moderate":
        levels = ["moderate", "budget"]
    else:
        levels = ["luxury", "moderate", "budget"]

    feasible_tier = None
    feasible_data = None

    for tier in levels:
        data = predict_budget(
            origin=request.origin,
            destination=request.destination,
            num_days=request.days,
            num_people=request.num_people,
            travel_type=tier,
            distance_km=distance_km,
            preferred_transport=request.preferred_transport,
            transport_options=transport_options_raw,
            user_budget=request.budget,
        )
        if data["budget_fit"] and data["budget_fit"]["adjusted_estimate"] <= request.budget:
            feasible_tier = tier
            feasible_data = data
            break
        elif data["budget_fit"] and data["budget_fit"]["fits_budget"]:
            feasible_tier = tier
            feasible_data = data
            break

    if feasible_data is None:
        feasible_data = predict_budget(
            origin=request.origin,
            destination=request.destination,
            num_days=request.days,
            num_people=request.num_people,
            travel_type="budget",
            distance_km=distance_km,
            preferred_transport=request.preferred_transport,
            transport_options=transport_options_raw,
            user_budget=request.budget,
        )

    bf = feasible_data["budget_fit"]
    can_fit = bf and bf["adjusted_estimate"] <= request.budget
    min_required = feasible_data["budget_fit"]["adjusted_estimate"] if feasible_data["budget_fit"] else feasible_data["total_estimated"]

    cheaper_transport = None
    for opt in sorted(transport_options_raw, key=lambda x: x["cost_total"]):
        if opt["mode"] != (selected_transport["mode"] if selected_transport else ""):
            alt_data = predict_budget(
                origin=request.origin,
                destination=request.destination,
                num_days=request.days,
                num_people=request.num_people,
                travel_type="budget",
                distance_km=distance_km,
                preferred_transport=opt["mode"],
                transport_options=transport_options_raw,
                user_budget=request.budget,
            )
            alt_bf = alt_data.get("budget_fit", {})
            if alt_bf and alt_bf.get("adjusted_estimate", 999999) <= request.budget:
                cheaper_transport = {
                    "mode": opt["mode"],
                    "emoji": opt["emoji"],
                    "saves": round((selected_transport["cost_total"] if selected_transport else 0) - opt["cost_total"]),
                    "cost_total": opt["cost_total"],
                }
                break

    days_suggestion = None
    if not can_fit and request.days > 1:
        for try_days in range(request.days - 1, 0, -1):
            d = predict_budget(
                origin=request.origin,
                destination=request.destination,
                num_days=try_days,
                num_people=request.num_people,
                travel_type="budget",
                distance_km=distance_km,
                preferred_transport=request.preferred_transport,
                transport_options=transport_options_raw,
                user_budget=request.budget,
            )
            dbf = d.get("budget_fit", {})
            if dbf and dbf.get("adjusted_estimate", 999999) <= request.budget:
                days_suggestion = {"days": try_days, "estimated": dbf["adjusted_estimate"]}
                break

    return {
        "can_generate": can_fit,
        "selected_transport": selected_transport,
        "transport_cost": round(transport_cost, 2),
        "remaining_after_transport": round(remaining_budget, 2),
        "feasible_tier": feasible_tier,
        "original_travel_type": request.travel_type,
        "budget_breakdown": {
            "total_estimated": feasible_data["total_estimated"],
            "adjusted_estimate": bf["adjusted_estimate"] if bf else feasible_data["total_estimated"],
            "accommodation": feasible_data["accommodation"],
            "food": feasible_data["food"],
            "transport": feasible_data["transport"],
            "activities": feasible_data["activities"],
            "misc": feasible_data["misc"],
        },
        "adjustments": bf["adjustments_made"] if bf else [],
        "recommendation": bf["recommendation"] if bf else "",
        "upgrade_plan": bf["upgrade_plan"] if bf else None,
        "min_required_budget": round(min_required, 2),
        "suggestions": {
            "cheaper_transport": cheaper_transport,
            "days_reduction": days_suggestion,
            "budget_needed": round(feasible_data["total_estimated"] - request.budget, 2) if not can_fit else 0,
        }
    }


@router.get("/transport-options")
async def get_transport_options_api(
    origin: str,
    destination: str,
    num_people: int = 2,
    num_days: int = 2,
):
    """Returns available transport modes with real cost estimates."""
    distance_km, _ = get_route_distance(origin, destination)

    options = get_transport_options(
        origin=origin,
        destination=destination,
        distance_km=distance_km,
        num_people=num_people,
        num_days=num_days,
    )

    # Enrich with live prices
    try:
        from services.transport_live_service import enrich_transport_options
        options = enrich_transport_options(options, origin, destination, num_people, distance_km=distance_km)
    except Exception as _te:
        print(f"[TransportAPI] Enrichment skipped: {_te}")

    return {
        "origin": origin,
        "destination": destination,
        "distance_km": round(distance_km, 1),
        "options": options,
    }


@router.get("/arrival-point")
async def get_arrival_point_api(
    destination: str,
    transport_mode: str,
):
    """Returns the verified arrival terminal for a destination based on transport mode."""
    point = get_arrival_point(destination, transport_mode)
    return {
        "destination":    destination,
        "transport_mode": transport_mode,
        "arrival_point":  point,
    }


@router.get("/hotels")
async def get_hotels_api(
    destination: str,
    arrival_lat: float,
    arrival_lon: float,
    travel_style: str = "moderate",
    num_people: int = 2,
    num_days: int = 3,
    radius_m: int = 6000,
):
    """
    Returns real hotels near the arrival point, sorted by popularity.
    
    If no hotels found near arrival point, automatically falls back to city center.
    Returns:
      - hotels: List of hotel objects
      - fallback_used: bool
      - fallback_reason: str (message if fallback was triggered)
      - search_center_name: str

    Example:
      /api/hotels?destination=Manali&arrival_lat=32.2396&arrival_lon=77.1887&travel_style=moderate
    """
    from services.ml_service import _classify_destination
    dest_category = _classify_destination(destination)

    result = search_hotels_near_arrival(
        arrival_lat   = arrival_lat,
        arrival_lon   = arrival_lon,
        destination   = destination,
        travel_style  = travel_style,
        dest_category = dest_category,
        radius_m      = radius_m,
        max_results   = 12,
    )

    return {
        "destination":        destination,
        "arrival_lat":        arrival_lat,
        "arrival_lon":        arrival_lon,
        "travel_style":       travel_style,
        "hotels_count":       len(result["hotels"]),
        "hotels":             result["hotels"],
        "fallback_used":      result.get("fallback_used", False),
        "fallback_reason":    result.get("fallback_reason", ""),
        "search_center_name": result.get("search_center_name", "Near Arrival Point"),
    }


@router.get("/destinations/popular")
async def get_popular_destinations():
    return {
        "destinations": [
            {"name": "Delhi", "state": "Delhi", "type": "Heritage", "emoji": "🏛️"},
            {"name": "Goa", "state": "Goa", "type": "Beach", "emoji": "🏖️"},
            {"name": "Jaipur", "state": "Rajasthan", "type": "Heritage", "emoji": "🏰"},
            {"name": "Mumbai", "state": "Maharashtra", "type": "Cosmopolitan", "emoji": "🌆"},
            {"name": "Manali", "state": "Himachal Pradesh", "type": "Hill Station", "emoji": "⛰️"},
            {"name": "Agra", "state": "Uttar Pradesh", "type": "Heritage", "emoji": "🕌"},
            {"name": "Varanasi", "state": "Uttar Pradesh", "type": "Spiritual", "emoji": "🙏"},
            {"name": "Kerala", "state": "Kerala", "type": "Nature", "emoji": "🌿"},
            {"name": "Shimla", "state": "Himachal Pradesh", "type": "Hill Station", "emoji": "🏔️"},
            {"name": "Rishikesh", "state": "Uttarakhand", "type": "Adventure", "emoji": "🏄"},
            {"name": "Udaipur", "state": "Rajasthan", "type": "Heritage", "emoji": "🏯"},
            {"name": "Andaman", "state": "Andaman & Nicobar", "type": "Beach", "emoji": "🐠"},
            {"name": "Paris", "state": "France", "type": "Romantic", "emoji": "🗼"},
            {"name": "Bangkok", "state": "Thailand", "type": "Cultural", "emoji": "🛕"},
            {"name": "Bali", "state": "Indonesia", "type": "Beach", "emoji": "🌴"},
            {"name": "Dubai", "state": "UAE", "type": "Luxury", "emoji": "🏙️"},
            {"name": "Singapore", "state": "Singapore", "type": "City", "emoji": "🦁"},
        ]
    }

@router.post("/compare-budgets")
async def compare_budgets(request: TripRequest):
    """
    Feature 4: Compare budget vs moderate vs luxury costs for the same trip.
    Returns a lightweight breakdown for each tier — no LLM call needed.
    """
    dest_coords = _resolve_coordinates(request.destination)
    if dest_coords is None:
        raise HTTPException(status_code=422, detail=f"Could not locate '{request.destination}'.")

    distance_km, _ = get_route_distance(request.origin, request.destination)
    transport_options_raw = get_transport_options(
        origin=request.origin, destination=request.destination,
        distance_km=distance_km, num_people=request.num_people,
        num_days=request.days, preferred=request.preferred_transport,
    )

    tiers = {}
    for tier in ["budget", "moderate", "luxury"]:
        data = predict_budget(
            origin=request.origin, destination=request.destination,
            num_days=request.days, num_people=request.num_people,
            travel_type=tier, distance_km=distance_km,
            preferred_transport=request.preferred_transport,
            transport_options=transport_options_raw,
            user_budget=request.budget,
        )

        # Budget tips must reflect the current tier being displayed,
        # not the "cheapest fitting tier" that predict_budget resolves internally.
        intl_cats = {
            "europe_expensive", "europe_moderate", "europe_budget",
            "north_america", "australia", "east_asia", "east_asia_expensive",
            "middle_east", "luxury_island",
        }
        dest_cat = data.get("destination_category", "")
        is_intl  = dest_cat in intl_cats

        if tier == "budget":
            tier_tips = [
                "Book hostels or guesthouses — check Hostelworld or Booking.com",
                "Eat at local markets and street stalls — authentic and affordable",
                "Use public transport: metro, bus, or shared rides",
            ]
            if is_intl:
                tier_tips.insert(0, "Travel in shoulder season for 30–40% lower costs")
        elif tier == "moderate":
            tier_tips = [
                "Book mid-range hotels mid-week for 15–20% savings",
                "Mix restaurant dining with local street food",
                "Use ride-hailing apps (Uber/Grab/Ola) for local travel",
            ]
        else:
            tier_tips = [
                "Book luxury hotels and flights 4–6 weeks in advance",
                "Hire a private car or driver for full-day sightseeing",
                "Pre-book premium experiences and guided tours",
            ]

        tiers[tier] = {
            "tier":              tier,
            "total_estimated":   data["total_estimated"],
            "per_person":        data["per_person"],
            "accommodation":     data["accommodation"],
            "food":              data["food"],
            "transport":         data["transport"],
            "activities":        data["activities"],
            "misc":              data["misc"],
            "fits_budget":       data["total_estimated"] <= request.budget if request.budget > 0 else True,
            "transport_mode":    data.get("transport_mode", ""),
            "budget_tips":       tier_tips[:2],
        }

    return {
        "origin":      request.origin,
        "destination": request.destination,
        "days":        request.days,
        "num_people":  request.num_people,
        "your_budget": request.budget,
        "tiers":       tiers,
    }


@router.get("/surprise-destination")
async def surprise_destination(
    origin: str,
    budget: float,
    days: int,
    travel_type: str = "moderate",
):
    """
    Feature 6: Suggest a random destination matching budget and travel style.
    Uses a curated list of destinations matched to budget tiers.
    """
    import random

    BUDGET_DESTINATIONS = {
        "budget": [
            {"destination": "Rishikesh", "vibe": "Adventure & Spirituality", "emoji": "🏔️"},
            {"destination": "Varanasi",  "vibe": "Culture & Heritage",        "emoji": "🛕"},
            {"destination": "Hampi",     "vibe": "Ancient Ruins & History",   "emoji": "🏛️"},
            {"destination": "Darjeeling","vibe": "Tea Gardens & Mountains",   "emoji": "🍵"},
            {"destination": "Pushkar",   "vibe": "Spiritual & Colourful",     "emoji": "🌈"},
            {"destination": "Puri",      "vibe": "Beach & Temple",            "emoji": "🏖️"},
            {"destination": "Amritsar",  "vibe": "Faith & Food",              "emoji": "🌟"},
            {"destination": "McLeod Ganj","vibe": "Himalayan Peace",          "emoji": "🏔️"},
        ],
        "moderate": [
            {"destination": "Goa",       "vibe": "Beach & Nightlife",         "emoji": "🌊"},
            {"destination": "Jaipur",    "vibe": "Royal Palaces & Culture",   "emoji": "🏰"},
            {"destination": "Manali",    "vibe": "Snow & Adventure",          "emoji": "❄️"},
            {"destination": "Coorg",     "vibe": "Coffee & Rainforest",       "emoji": "☕"},
            {"destination": "Munnar",    "vibe": "Tea Hills & Mist",          "emoji": "🌿"},
            {"destination": "Udaipur",   "vibe": "Lake City & Romance",       "emoji": "💙"},
            {"destination": "Jaisalmer", "vibe": "Desert & Dunes",            "emoji": "🐪"},
            {"destination": "Ooty",      "vibe": "Nilgiri Hills & Trains",    "emoji": "🚂"},
            {"destination": "Shimla",    "vibe": "Colonial Charm & Snow",     "emoji": "🏔️"},
        ],
        "luxury": [
            {"destination": "Maldives",  "vibe": "Overwater Bungalows",       "emoji": "🏝️"},
            {"destination": "Dubai",     "vibe": "Skyscrapers & Luxury",      "emoji": "✨"},
            {"destination": "Bangkok",   "vibe": "Street Food & Temples",     "emoji": "🛕"},
            {"destination": "Singapore", "vibe": "Modern City & Gardens",     "emoji": "🌆"},
            {"destination": "Leh",       "vibe": "Raw Himalayan Adventure",   "emoji": "🏔️"},
            {"destination": "Kerala",    "vibe": "Backwaters & Ayurveda",     "emoji": "🌴"},
            {"destination": "Bali",      "vibe": "Temples & Rice Terraces",   "emoji": "🌺"},
        ],
    }

    pool = BUDGET_DESTINATIONS.get(travel_type, BUDGET_DESTINATIONS["moderate"])

    # Exclude origin from suggestions
    pool = [d for d in pool if d["destination"].lower() != origin.lower()]

    if not pool:
        pool = BUDGET_DESTINATIONS["moderate"]

    pick = random.choice(pool)
    return {
        "destination": pick["destination"],
        "vibe":        pick["vibe"],
        "emoji":       pick["emoji"],
        "origin":      origin,
        "budget":      budget,
        "days":        days,
        "travel_type": travel_type,
    }
