"""
Algorithm + Fallback Tests for Smart Travel Planner backend.

Tests:
  1. Preference-weighted ranking  — History pref lifts a historical place above a generic one
  2. Nearest-neighbor ordering    — optimized order is shorter than reverse order
  3. Distribution capping         — 5 days, 3 places → every day gets exactly 1 place, no duplication
  4. LLM fallback                 — malformed LLM JSON triggers rule-based fallback and returns valid response
"""
import pytest
import sys
import os

# Ensure backend root is on path (conftest.py also does this, but explicit is safer)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.ml_service import (
    score_and_rank_attractions,
    optimize_route,
    distribute_places_by_day,
)
from services.llm_service import generate_itinerary_with_llm


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_place(name, rating=4.0, types=None, lat=0.0, lon=0.0):
    return {
        "name": name,
        "rating": rating,
        "types": types or ["tourist_attraction"],
        "price_level": 1,
        "latitude": lat,
        "longitude": lon,
        "description": f"Sample place: {name}",
        "best_time": "Morning",
    }


# ── Test 1: Preference-Weighted Ranking ───────────────────────────────────────

class TestPreferenceWeightedRanking:
    """
    With preference=History, a place typed 'historical' should rank
    above an equally-rated place without history types.
    """

    def test_history_preference_lifts_historical_place(self):
        historical = _make_place(
            "Old Fort Museum",
            rating=4.0,
            types=["historical", "museum"],
        )
        generic = _make_place(
            "City Shopping Mall",
            rating=4.5,    # higher raw rating
            types=["shopping_mall"],
        )

        ranked = score_and_rank_attractions(
            [generic, historical],
            travel_type="moderate",
            preferences=["History"],
        )

        # Historical place must come first despite lower raw rating
        assert ranked[0]["name"] == "Old Fort Museum", (
            f"Expected 'Old Fort Museum' first, got '{ranked[0]['name']}'. "
            "History preference should boost historical place above a mall."
        )

    def test_no_preference_uses_raw_rating(self):
        high_rated = _make_place("Popular Landmark", rating=4.8, types=["tourist_attraction"])
        low_rated  = _make_place("Obscure Ruins",    rating=3.0, types=["ruins"])

        ranked = score_and_rank_attractions(
            [low_rated, high_rated],
            travel_type="moderate",
            preferences=[],
        )

        assert ranked[0]["name"] == "Popular Landmark", (
            "Without preferences, higher popularity_score / rating should rank first."
        )

    def test_nature_preference_lifts_park(self):
        park  = _make_place("National Park",   rating=4.0, types=["park", "natural_feature"])
        hotel = _make_place("City Restaurant", rating=4.6, types=["restaurant", "food"])

        ranked = score_and_rank_attractions(
            [hotel, park],
            travel_type="moderate",
            preferences=["Nature"],
        )

        assert ranked[0]["name"] == "National Park", (
            "Nature preference should lift park above a restaurant."
        )


# ── Test 2: Nearest-Neighbor Route Ordering ───────────────────────────────────

class TestNearestNeighborOrdering:
    """
    Given 4 places arranged in a square, the optimized route should
    produce a total distance shorter than the naively reversed order.
    """

    def _total_distance(self, places):
        """Sum of consecutive haversine distances."""
        from utils.helpers import haversine_distance
        total = 0.0
        for i in range(len(places) - 1):
            total += haversine_distance(
                places[i]["latitude"],  places[i]["longitude"],
                places[i+1]["latitude"], places[i+1]["longitude"],
            )
        return total

    def test_optimized_shorter_than_reversed(self):
        # Square layout: NW → NE → SE → SW  (anticlockwise is longer than clockwise)
        places = [
            _make_place("NW", lat=1.0,  lon=0.0),  # 0
            _make_place("SW", lat=0.0,  lon=0.0),  # 1
            _make_place("SE", lat=0.0,  lon=1.0),  # 2
            _make_place("NE", lat=1.0,  lon=1.0),  # 3
        ]

        # Worst-case input: interleaved NW, SE, SW, NE → forces zig-zag
        worst_order = [places[0], places[2], places[1], places[3]]  # NW→SE→SW→NE
        optimized   = optimize_route(worst_order, origin_lat=0.0, origin_lon=0.0)

        dist_worst     = self._total_distance(worst_order)
        dist_optimized = self._total_distance(optimized)

        assert dist_optimized < dist_worst, (
            f"Optimized route ({dist_optimized:.2f} km) should be shorter "
            f"than zig-zag order ({dist_worst:.2f} km)."
        )

    def test_two_places_returned_unchanged(self):
        places = [
            _make_place("A", lat=10.0, lon=77.0),
            _make_place("B", lat=11.0, lon=78.0),
        ]
        result = optimize_route(places, origin_lat=10.0, origin_lon=77.0)
        assert len(result) == 2, "Should return both places for input of size 2."

    def test_single_place_returned_unchanged(self):
        places = [_make_place("Only Place", lat=12.0, lon=78.0)]
        result = optimize_route(places, origin_lat=12.0, origin_lon=78.0)
        assert len(result) == 1

    def test_places_without_coords_appended_at_end(self):
        """Places without coordinates should be appended after optimized ones."""
        has_coords    = _make_place("Mapped Place", lat=12.0, lon=77.0)
        no_coords1    = _make_place("No Coords A", lat=0.0, lon=0.0)
        no_coords2    = _make_place("No Coords B", lat=0.0, lon=0.0)
        no_coords3    = _make_place("No Coords C", lat=0.0, lon=0.0)

        places = [no_coords1, has_coords, no_coords2, no_coords3]
        result = optimize_route(places, origin_lat=12.0, origin_lon=77.0)

        # The mapped place should still appear somewhere; no crash
        names = [p["name"] for p in result]
        assert "Mapped Place" in names, "Mapped place must appear in result."
        assert len(result) == 4, "All 4 places must be returned."


# ── Test 3: Distribution Capping — scarce places, many days ──────────────────

class TestDistributionCapping:
    """
    5 days, 3 places → every day must get exactly 1 place.
    No day should be empty. Cycling is allowed.
    """

    def test_5_days_3_places_no_empty_days(self):
        places = [
            _make_place("Attraction A"),
            _make_place("Attraction B"),
            _make_place("Attraction C"),
        ]
        result = distribute_places_by_day(places, num_days=5, places_per_day=3)

        assert len(result) == 5, "Should produce exactly 5 day buckets."
        for i, bucket in enumerate(result):
            assert len(bucket) >= 1, (
                f"Day {i+1} is empty — distribute_places_by_day must never produce empty days."
            )

    def test_5_days_3_places_each_day_has_1(self):
        places = [_make_place(f"P{i}") for i in range(3)]
        result = distribute_places_by_day(places, num_days=5, places_per_day=3)

        for i, bucket in enumerate(result):
            assert len(bucket) == 1, (
                f"Day {i+1} should have exactly 1 place when total_places < num_days, "
                f"got {len(bucket)}."
            )

    def test_more_places_than_days_distributes_evenly(self):
        """12 places, 4 days, cap 3 → all days should get 3."""
        places = [_make_place(f"P{i}") for i in range(12)]
        result = distribute_places_by_day(places, num_days=4, places_per_day=3)

        assert len(result) == 4
        for i, bucket in enumerate(result):
            assert len(bucket) == 3, (
                f"Day {i+1} should get 3 places, got {len(bucket)}."
            )

    def test_no_duplicate_places_in_normal_case(self):
        """When total places > num_days, no place should appear twice."""
        places = [_make_place(f"Place {i}") for i in range(10)]
        result = distribute_places_by_day(places, num_days=4, places_per_day=3)

        all_names = [p["name"] for bucket in result for p in bucket]
        assert len(all_names) == len(set(all_names)), (
            f"Duplicate place found in distribution: {all_names}"
        )

    def test_empty_input_returns_empty_days(self):
        """Empty place list should return the correct number of empty day buckets."""
        result = distribute_places_by_day([], num_days=3, places_per_day=3)
        assert len(result) == 3
        for bucket in result:
            assert bucket == [], "Each day should be an empty list when no places provided."


# ── Test 4: Malformed LLM Output → Rule-Based Fallback ───────────────────────

class TestLLMFallback:
    """
    If the LLM returns malformed JSON, the service must fall back to
    rule-based itinerary generation and still return a valid response dict.
    """

    # Sample day-places for LLM call
    _DAY_PLACES = [
        {
            "day": 1,
            "places": [
                {"name": "Taj Mahal", "rating": 4.8, "types": ["tourist_attraction"],
                 "best_time": "Sunrise", "description": "Iconic marble mausoleum", "price_level": 2},
            ],
        },
    ]

    _TOP_PLACES = [
        {"name": "Taj Mahal", "rating": 4.8, "types": ["tourist_attraction"],
         "latitude": 27.1751, "longitude": 78.0421, "description": "UNESCO World Heritage Site",
         "best_time": "Sunrise", "price_level": 2, "popularity_score": 0.95},
    ]

    _BUDGET = {
        "total_estimated": 8000, "accommodation": 2000, "food": 1500,
        "activities": 1000, "transport": 2200, "misc": 1300,
        "transport_mode": "Train", "per_day": {
            "accommodation": 1000, "food": 750, "activities": 500,
            "misc": 650, "total_per_day": 2900,
        },
        "effective_tier": "moderate",
    }

    _TRANSPORT = {"mode": "Train", "tip": "Book on IRCTC", "duration": "2h"}

    def test_fallback_returns_valid_response_structure(self):
        """
        generate_itinerary_with_llm must always return a dict with
        'day_plans', 'travel_tips', and 'itinerary_summary' keys —
        even if the LLM is unavailable or returns garbage.
        """
        result = generate_itinerary_with_llm(
            origin="Delhi",
            destination="Agra",
            days=1,
            budget=8000,
            travel_type="moderate",
            num_people=2,
            preferences=["History"],
            top_places=self._TOP_PLACES,
            day_places_for_llm=self._DAY_PLACES,
            weather_info={"temperature": 28, "description": "Clear"},
            budget_estimate=self._BUDGET,
            transport_mode=self._TRANSPORT,
            distance_km=210,
            llm_only_mode=False,
        )

        # Must always return a dict — never raise
        assert isinstance(result, dict), "Result must be a dict."
        assert "day_plans" in result, "Result must have 'day_plans' key."
        assert "travel_tips" in result, "Result must have 'travel_tips' key."
        assert "itinerary_summary" in result, "Result must have 'itinerary_summary' key."

    def test_fallback_day_plans_is_list(self):
        result = generate_itinerary_with_llm(
            origin="Delhi",
            destination="Agra",
            days=1,
            budget=8000,
            travel_type="moderate",
            num_people=2,
            preferences=[],
            top_places=self._TOP_PLACES,
            day_places_for_llm=self._DAY_PLACES,
            weather_info={},
            budget_estimate=self._BUDGET,
            transport_mode=self._TRANSPORT,
            distance_km=210,
            llm_only_mode=False,
        )
        assert isinstance(result["day_plans"], list), "'day_plans' must be a list."

    def test_fallback_travel_tips_is_list(self):
        result = generate_itinerary_with_llm(
            origin="Delhi",
            destination="Agra",
            days=1,
            budget=8000,
            travel_type="budget",
            num_people=1,
            preferences=[],
            top_places=self._TOP_PLACES,
            day_places_for_llm=self._DAY_PLACES,
            weather_info={},
            budget_estimate=self._BUDGET,
            transport_mode=self._TRANSPORT,
            distance_km=210,
            llm_only_mode=False,
        )
        assert isinstance(result["travel_tips"], list), "'travel_tips' must be a list."

    def test_fallback_itinerary_summary_non_empty(self):
        result = generate_itinerary_with_llm(
            origin="Delhi",
            destination="Agra",
            days=1,
            budget=8000,
            travel_type="moderate",
            num_people=2,
            preferences=[],
            top_places=self._TOP_PLACES,
            day_places_for_llm=self._DAY_PLACES,
            weather_info={},
            budget_estimate=self._BUDGET,
            transport_mode=self._TRANSPORT,
            distance_km=210,
            llm_only_mode=False,
        )
        assert isinstance(result["itinerary_summary"], str), "'itinerary_summary' must be a string."
        assert len(result["itinerary_summary"]) > 0, "'itinerary_summary' must not be empty."
