"""
Offline Mode Tests for Smart Travel Planner backend.

Tests:
  1. Determinism     — same inputs → identical outputs every call
  2. Completeness    — all required TripResponse-compatible fields present
  3. Speed           — response built in < 2 seconds (no I/O)
  4. Budget math     — sum(day_costs) + intercity == total_estimated
  5. Hotel rate      — accommodation == selected hotel ppn × num_days exactly
  6. Shortfall block — budget too small → can_generate: False
  7. Unsupported route raises ValueError with a helpful message
  8. Mumbai→Goa smoke test — correct arrival point type and transport emoji
"""
import time
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.offline_service import build_offline_trip, build_offline_budget_check


# ─────────────────────────────────────────────────────────────────────────────
# Shared fixtures
# ─────────────────────────────────────────────────────────────────────────────

DELHI_AGRA_ARGS = dict(
    origin="Delhi",
    destination="Agra",
    num_days=2,
    num_people=2,
    travel_type="moderate",
    user_budget=15000,
    hotel_ppn=1200.0,
)

MUMBAI_GOA_ARGS = dict(
    origin="Mumbai",
    destination="Goa",
    num_days=3,
    num_people=2,
    travel_type="moderate",
    user_budget=30000,
    hotel_ppn=3000.0,
)

# Required top-level keys in a TripResponse-compatible dict
REQUIRED_TRIP_KEYS = {
    "destination", "origin", "days", "travel_type", "num_people",
    "budget_provided", "weather", "day_plans", "budget_estimate",
    "transport_options", "arrival_point", "travel_tips", "top_places",
    "itinerary_summary", "status", "planning_mode", "data_sources",
    "generated_at",
}

# Required keys in budget_estimate sub-dict
REQUIRED_BUDGET_KEYS = {
    "total_estimated", "per_person", "accommodation", "food",
    "transport", "activities", "misc", "intercity_transport",
    "intercity_transport_mode",
}


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Determinism
# ─────────────────────────────────────────────────────────────────────────────

class TestDeterminism:
    def test_delhi_agra_identical_on_repeat(self):
        r1 = build_offline_trip(**DELHI_AGRA_ARGS)
        r2 = build_offline_trip(**DELHI_AGRA_ARGS)

        assert r1["budget_estimate"]["total_estimated"] == r2["budget_estimate"]["total_estimated"], \
            "total_estimated must be identical on repeated calls."
        assert r1["generated_at"] == r2["generated_at"], \
            "generated_at must be a fixed timestamp (not datetime.now)."
        assert len(r1["day_plans"]) == len(r2["day_plans"]), \
            "Number of day plans must be identical."

    def test_mumbai_goa_identical_on_repeat(self):
        r1 = build_offline_trip(**MUMBAI_GOA_ARGS)
        r2 = build_offline_trip(**MUMBAI_GOA_ARGS)
        assert r1["budget_estimate"]["total_estimated"] == r2["budget_estimate"]["total_estimated"]
        assert r1["generated_at"] == r2["generated_at"]

    def test_budget_check_determinism(self):
        b1 = build_offline_budget_check(**DELHI_AGRA_ARGS)
        b2 = build_offline_budget_check(**DELHI_AGRA_ARGS)
        assert b1["min_required_budget"] == b2["min_required_budget"]
        assert b1["can_generate"] == b2["can_generate"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Completeness
# ─────────────────────────────────────────────────────────────────────────────

class TestCompleteness:
    def test_all_required_trip_keys_present(self):
        result = build_offline_trip(**DELHI_AGRA_ARGS)
        missing = REQUIRED_TRIP_KEYS - set(result.keys())
        assert not missing, f"Missing top-level keys: {missing}"

    def test_all_required_budget_keys_present(self):
        result = build_offline_trip(**DELHI_AGRA_ARGS)
        budget = result["budget_estimate"]
        missing = REQUIRED_BUDGET_KEYS - set(budget.keys())
        assert not missing, f"Missing budget keys: {missing}"

    def test_day_plans_have_required_fields(self):
        result = build_offline_trip(**DELHI_AGRA_ARGS)
        for i, day in enumerate(result["day_plans"]):
            for key in ("day", "date_label", "places", "morning", "afternoon", "evening", "estimated_cost"):
                assert key in day, f"Day {i+1} is missing '{key}' field."

    def test_arrival_point_has_required_fields(self):
        result = build_offline_trip(**DELHI_AGRA_ARGS)
        ap = result["arrival_point"]
        for key in ("name", "latitude", "longitude", "address", "type", "maps_url", "verified", "source"):
            assert key in ap, f"arrival_point missing '{key}'."

    def test_data_sources_labelled(self):
        result = build_offline_trip(**DELHI_AGRA_ARGS)
        ds = result["data_sources"]
        assert ds.get("attractions") in ("curated", "cached_estimate", "rule_based"), \
            "attractions data_source must have an offline label."
        assert ds.get("weather") in ("curated", "cached_estimate"), \
            "weather data_source must have an offline label."

    def test_planning_mode_is_offline(self):
        result = build_offline_trip(**DELHI_AGRA_ARGS)
        assert result["planning_mode"] == "offline", \
            "planning_mode must be 'offline' for offline trips."

    def test_status_is_success(self):
        result = build_offline_trip(**DELHI_AGRA_ARGS)
        assert result["status"] == "success"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Speed
# ─────────────────────────────────────────────────────────────────────────────

class TestSpeed:
    def test_delhi_agra_under_2_seconds(self):
        start = time.perf_counter()
        build_offline_trip(**DELHI_AGRA_ARGS)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, \
            f"build_offline_trip took {elapsed:.3f}s — must be < 2s (no I/O allowed)."

    def test_mumbai_goa_under_2_seconds(self):
        start = time.perf_counter()
        build_offline_trip(**MUMBAI_GOA_ARGS)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, \
            f"build_offline_trip took {elapsed:.3f}s — must be < 2s (no I/O allowed)."

    def test_budget_check_under_1_second(self):
        start = time.perf_counter()
        build_offline_budget_check(**DELHI_AGRA_ARGS)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, \
            f"build_offline_budget_check took {elapsed:.3f}s — must be < 1s."


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — Budget Reconciliation: sum(day_costs) + intercity == total
# ─────────────────────────────────────────────────────────────────────────────

class TestBudgetReconciliation:
    def _day_cost_sum(self, result):
        return sum(d["estimated_cost"] for d in result["day_plans"])

    def test_day_costs_plus_intercity_equals_total(self):
        result   = build_offline_trip(**DELHI_AGRA_ARGS)
        budget   = result["budget_estimate"]
        day_sum  = self._day_cost_sum(result)
        intercity = budget["intercity_transport"]
        total     = budget["total_estimated"]

        # Allow ₹1 rounding tolerance
        assert abs((day_sum + intercity) - total) <= 1.0, (
            f"sum(day_costs)={day_sum:.2f} + intercity={intercity:.2f} "
            f"should equal total={total:.2f}. "
            f"Got {day_sum + intercity:.2f}."
        )

    def test_per_person_is_total_divided_by_people(self):
        result  = build_offline_trip(**DELHI_AGRA_ARGS)
        budget  = result["budget_estimate"]
        num_p   = result["num_people"]
        expected_pp = round(budget["total_estimated"] / num_p)
        # Allow ±1 for rounding
        assert abs(budget["per_person"] - expected_pp) <= 1, (
            f"per_person={budget['per_person']:.0f} should be ≈ "
            f"total / {num_p} = {expected_pp:.0f}."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — Hotel rate drives accommodation cost exactly
# ─────────────────────────────────────────────────────────────────────────────

class TestHotelRateDrivesAccommodation:
    def test_accommodation_equals_ppn_times_days(self):
        hotel_ppn = 2500.0
        num_days  = 3
        result = build_offline_trip(
            origin="Delhi", destination="Agra",
            num_days=num_days, num_people=2,
            travel_type="moderate", user_budget=50000,
            hotel_ppn=hotel_ppn,
        )
        expected_accom = round(hotel_ppn * num_days)
        actual_accom   = result["budget_estimate"]["accommodation"]
        assert actual_accom == expected_accom, (
            f"accommodation={actual_accom} should be hotel_ppn × days "
            f"= {hotel_ppn} × {num_days} = {expected_accom}."
        )

    def test_zero_hotel_ppn_uses_default(self):
        """When hotel_ppn=0, should fall back to the first curated hotel's min price."""
        result = build_offline_trip(
            origin="Delhi", destination="Agra",
            num_days=2, num_people=2,
            travel_type="moderate", user_budget=20000,
            hotel_ppn=0.0,
        )
        # Accommodation must be > 0 — the fallback must kick in
        assert result["budget_estimate"]["accommodation"] > 0, \
            "accommodation must not be 0 even when hotel_ppn=0 (fallback expected)."

    def test_hotel_ppn_higher_raises_accommodation(self):
        """Luxury hotel ppn should produce higher accommodation than budget ppn."""
        budget_r = build_offline_trip(
            origin="Mumbai", destination="Goa",
            num_days=3, num_people=2, travel_type="moderate",
            user_budget=100000, hotel_ppn=2500.0,
        )
        luxury_r = build_offline_trip(
            origin="Mumbai", destination="Goa",
            num_days=3, num_people=2, travel_type="moderate",
            user_budget=100000, hotel_ppn=15000.0,
        )
        assert luxury_r["budget_estimate"]["accommodation"] > \
               budget_r["budget_estimate"]["accommodation"], \
            "Higher hotel_ppn must produce higher accommodation cost."


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — Shortfall blocks generation (can_generate: False)
# ─────────────────────────────────────────────────────────────────────────────

class TestShortfallBlocksGeneration:
    def test_tiny_budget_returns_can_generate_false(self):
        """₹100 budget should be insufficient for any supported route."""
        result = build_offline_budget_check(
            origin="Delhi", destination="Agra",
            num_days=2, num_people=2,
            travel_type="moderate",
            user_budget=100,       # absurdly low
            hotel_ppn=1200.0,
        )
        assert result["can_generate"] is False, \
            "A ₹100 budget should set can_generate=False."
        assert result["min_required_budget"] > 100, \
            "min_required_budget must exceed the budget provided."

    def test_generous_budget_returns_can_generate_true(self):
        """₹1,00,000 should comfortably cover Delhi→Agra 2-night moderate trip."""
        result = build_offline_budget_check(
            origin="Delhi", destination="Agra",
            num_days=2, num_people=2,
            travel_type="moderate",
            user_budget=100000,
            hotel_ppn=1200.0,
        )
        assert result["can_generate"] is True, \
            "A ₹1,00,000 budget should set can_generate=True."

    def test_shortfall_amount_is_non_negative(self):
        result = build_offline_budget_check(
            origin="Delhi", destination="Agra",
            num_days=2, num_people=2,
            travel_type="moderate",
            user_budget=100,
            hotel_ppn=1200.0,
        )
        assert result["suggestions"]["budget_needed"] >= 0, \
            "budget_needed must be ≥ 0."


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — Unsupported route raises ValueError with helpful message
# ─────────────────────────────────────────────────────────────────────────────

class TestUnsupportedRouteError:
    def test_unsupported_origin_raises_valueerror(self):
        with pytest.raises(ValueError) as exc_info:
            build_offline_trip(
                origin="Chennai", destination="Mysore",
                num_days=2, num_people=2,
                travel_type="moderate", user_budget=15000,
            )
        message = str(exc_info.value).lower()
        assert "offline" in message or "supported" in message or "route" in message, (
            "ValueError message should mention 'offline', 'supported routes', "
            f"or 'route'. Got: '{exc_info.value}'"
        )

    def test_unsupported_destination_raises_valueerror(self):
        with pytest.raises(ValueError):
            build_offline_trip(
                origin="Delhi", destination="Ladakh",
                num_days=3, num_people=2,
                travel_type="budget", user_budget=20000,
            )

    def test_budget_check_unsupported_route_raises_valueerror(self):
        with pytest.raises(ValueError):
            build_offline_budget_check(
                origin="Bangalore", destination="Ooty",
                num_days=2, num_people=2,
                travel_type="budget", user_budget=5000,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 8 — Mumbai → Goa smoke test
# ─────────────────────────────────────────────────────────────────────────────

class TestMumbaiGoaSmokeTest:
    def test_arrival_point_is_airport(self):
        result = build_offline_trip(**MUMBAI_GOA_ARGS)
        ap = result["arrival_point"]
        assert ap["type"] == "airport", \
            f"Mumbai→Goa arrival should be airport, got '{ap['type']}'."

    def test_transport_mode_is_flight(self):
        result = build_offline_trip(**MUMBAI_GOA_ARGS)
        transport = result["transport_options"][0]
        assert "Flight" in transport["mode"] or "flight" in transport["mode"].lower(), \
            f"Mumbai→Goa transport should be Flight, got '{transport['mode']}'."

    def test_transport_emoji_is_plane(self):
        result = build_offline_trip(**MUMBAI_GOA_ARGS)
        transport = result["transport_options"][0]
        assert transport.get("emoji") == "✈️", \
            f"Flight emoji should be ✈️, got '{transport.get('emoji')}'."

    def test_top_places_include_goa_attraction(self):
        result = build_offline_trip(**MUMBAI_GOA_ARGS)
        names = [p["name"] for p in result["top_places"]]
        known_goa = {"Baga Beach", "Basilica of Bom Jesus", "Fort Aguada",
                     "Dudhsagar Waterfalls", "Palolem Beach", "Anjuna Flea Market"}
        matches = known_goa & set(names)
        assert matches, (
            f"top_places should include at least one verified Goa attraction. "
            f"Got: {names}"
        )

    def test_day_plans_count_matches_requested_days(self):
        result = build_offline_trip(**MUMBAI_GOA_ARGS)
        assert len(result["day_plans"]) == MUMBAI_GOA_ARGS["num_days"], \
            f"Expected {MUMBAI_GOA_ARGS['num_days']} day plans, got {len(result['day_plans'])}."

    def test_arrival_point_coordinates_are_valid(self):
        result = build_offline_trip(**MUMBAI_GOA_ARGS)
        ap = result["arrival_point"]
        assert 8 < ap["latitude"] < 25, \
            f"Goa airport latitude {ap['latitude']} is out of expected range (8°N–25°N)."
        assert 70 < ap["longitude"] < 80, \
            f"Goa airport longitude {ap['longitude']} is out of expected range (70°E–80°E)."

    def test_budget_over_budget_field_correct(self):
        """Generous budget → over_budget must be False."""
        result = build_offline_trip(**MUMBAI_GOA_ARGS)
        # ₹30,000 for Mumbai→Goa 3 nights moderate — check if budget field matches math
        budget = result["budget_estimate"]
        is_over = budget["total_estimated"] > MUMBAI_GOA_ARGS["user_budget"]
        assert budget["over_budget"] == is_over, \
            f"over_budget={budget['over_budget']} does not match actual math: "  \
            f"total={budget['total_estimated']} vs user_budget={MUMBAI_GOA_ARGS['user_budget']}."
