from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base


# ─────────────────────────────────────────────
#  SQLAlchemy ORM Models
# ─────────────────────────────────────────────

class TripRecord(Base):
    """Stores every trip-plan request + its generated response."""
    __tablename__ = "trip_records"

    id            = Column(Integer, primary_key=True, index=True)
    origin        = Column(String(200), nullable=False)
    destination   = Column(String(200), nullable=False)
    budget        = Column(Float, nullable=False)
    days          = Column(Integer, nullable=False)
    travel_type   = Column(String(50), nullable=False)
    num_people    = Column(Integer, nullable=False)
    preferences   = Column(JSON, default=list)
    response_json = Column(Text, nullable=True)
    share_id      = Column(String(32), nullable=True, unique=True, index=True)  # for sharing
    created_at    = Column(DateTime(timezone=True), server_default=func.now())


class TripRating(Base):
    """User rating and review for a trip itinerary."""
    __tablename__ = "trip_ratings"

    id         = Column(Integer, primary_key=True, index=True)
    trip_id    = Column(Integer, nullable=False, index=True)
    rating     = Column(Integer, nullable=False)   # 1–5
    review     = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────────
#  Pydantic Request / Response models
# ─────────────────────────────────────────────

class TripRequest(BaseModel):
    origin: str = Field(..., example="Mumbai")
    destination: str = Field(..., example="Goa")
    budget: float = Field(..., gt=0, example=15000)
    days: int = Field(..., ge=1, le=30, example=3)
    travel_type: str = Field(..., example="moderate")
    num_people: int = Field(..., ge=1, le=20, example=2)
    preferences: List[str] = Field(default_factory=list, example=["Nature", "Food"])
    preferred_transport: Optional[str] = Field(default=None, example="train")
    # Hotel selection (optional — passed from Step 4)
    selected_hotel_name: Optional[str] = Field(default=None)
    selected_hotel_lat: Optional[float] = Field(default=None)
    selected_hotel_lon: Optional[float] = Field(default=None)
    # Actual nightly rate from the hotel shown to the user (not the matrix estimate)
    selected_hotel_price_per_night: Optional[float] = Field(default=None)
    # Planning mode — safe default keeps existing flow unchanged
    planning_mode: str = Field(default="live")   # "live" | "offline"


class WeatherInfo(BaseModel):
    temperature: float
    feels_like: float
    description: str
    humidity: int
    wind_speed: float
    icon: str
    forecast: List[Dict[str, Any]] = []


class Place(BaseModel):
    name: str
    rating: float = 0.0
    address: str = ""
    types: List[str] = []
    opening_hours: str = ""
    price_level: int = 0
    entry_fee: str = ""
    visit_duration_minutes: int = 60
    crowd_level: str = "Medium"
    latitude: float = 0.0
    longitude: float = 0.0
    description: str = ""
    best_time: str = "Morning"
    popularity_score: float = 0.0


class LocalTransit(BaseModel):
    """Travel segment between two stops on a day's itinerary."""
    from_name: str = ""
    to_name: str = ""
    mode: str = ""
    emoji: str = ""
    distance_km: float = 0.0
    duration_min: int = 0
    cost_inr: int = 0
    note: str = ""


class Hotel(BaseModel):
    """A real hotel returned from Google Places near the arrival point."""
    name: str
    rating: float = 0.0
    user_ratings_total: int = 0
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    distance_from_arrival_km: float = 0.0
    price_per_night_min: int = 0
    price_per_night_max: int = 0
    price_label: str = ""          # e.g. "₹1,500–₹4,500/night"
    price_source: str = "Estimated"
    maps_url: str = ""
    place_id: str = ""


class ArrivalPoint(BaseModel):
    """The terminal/point where the traveller arrives at the destination."""
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    address: str = ""
    type: str = ""            # airport | railway | bus | port | city_center
    maps_url: str = ""
    verified: bool = False
    source: str = ""          # curated | google_places | geocode | unknown


class DayPlan(BaseModel):
    day: int
    date_label: str
    places: List[Place] = []
    narrative: str = ""
    morning: str = ""
    afternoon: str = ""
    evening: str = ""
    estimated_cost: float = 0.0
    route_segments: List[LocalTransit] = []   # transit between consecutive stops


class TransportOption(BaseModel):
    mode: str
    emoji: str
    duration: str
    cost_per_person: float
    cost_total: float
    fare_min: float = 0.0
    fare_max: float = 0.0
    fare_label: str = ""
    price_source: str = "Estimated"   # "Live" | "Cached" | "Estimated"
    price_note: str = ""              # e.g. "Prices from Skyscanner cache"
    available: bool = True
    recommended: bool = False
    tip: str = ""
    booking_link: str = ""
    booking_link_alt: str = ""        # secondary booking option


class BudgetFitResult(BaseModel):
    fits_budget: bool
    original_estimate: float
    adjusted_estimate: float
    budget_provided: float
    shortfall: float = 0.0
    savings: float = 0.0
    utilization_pct: float = 0.0
    adjustments_made: List[Dict[str, Any]] = []
    recommendation: str = ""
    upgrade_plan: Optional[Dict[str, Any]] = None


class DailyBudgetBreakdown(BaseModel):
    """Detailed per-day budget with meal + activity sub-categories."""
    breakfast: float = 0.0
    lunch: float = 0.0
    dinner: float = 0.0
    local_transport: float = 0.0
    entry_tickets: float = 0.0
    shopping: float = 0.0
    misc: float = 0.0
    total: float = 0.0
    # Min/Max ranges (±20% for budget, ±35% for moderate/luxury)
    min_total: float = 0.0
    max_total: float = 0.0


class BudgetEstimate(BaseModel):
    total_estimated: float
    total_min: float = 0.0
    total_max: float = 0.0
    per_person: float
    original_budget: float = 0.0
    remaining_budget: float = 0.0
    over_budget: bool = False
    # Line items
    accommodation: float
    hotel_name: str = ""
    hotel_cost_source: str = "Estimated"
    food: float
    transport: float
    intercity_transport: float = 0.0
    intercity_transport_mode: str = ""
    intercity_transport_label: str = "Estimated"
    local_transport: float = 0.0
    activities: float
    entry_tickets: float = 0.0
    shopping: float = 0.0
    misc: float
    budget_tips: List[str] = []
    transport_mode: str = ""
    daily_breakdown: Optional[DailyBudgetBreakdown] = None
    budget_fit: Optional["BudgetFitResult"] = None


class TripResponse(BaseModel):
    id: Optional[int] = None          # DB record ID — used for rating/sharing
    destination: str
    origin: str
    days: int
    travel_type: str
    num_people: int
    budget_provided: float
    weather: Optional[WeatherInfo] = None
    day_plans: List[DayPlan] = []
    budget_estimate: Optional[BudgetEstimate] = None
    transport_options: List[TransportOption] = []
    arrival_point: Optional["ArrivalPoint"] = None
    travel_tips: List[str] = []
    top_places: List[Place] = []
    itinerary_summary: str = ""
    status: str = "success"
    message: str = ""
    # Metadata — safe defaults so existing frontend ignores them gracefully
    planning_mode: str = "live"
    data_sources: Dict[str, str] = Field(default_factory=dict)
    generated_at: Optional[str] = None
