"""History Router: Fetch past trip plans, ratings, and sharing."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json
import secrets

from database import get_db
from models import TripRecord, TripRating

router = APIRouter(prefix="/api", tags=["Trip History"])


# ── Pydantic schemas for rating ───────────────────────────────────────────────
class RatingRequest(BaseModel):
    trip_id: int
    rating: int       # 1–5
    review: Optional[str] = ""


@router.get("/history")
async def get_trip_history(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent trip plans."""
    try:
        records = (
            db.query(TripRecord)
            .order_by(TripRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        result = []
        for r in records:
            result.append({
                "id": r.id,
                "origin": r.origin,
                "destination": r.destination,
                "budget": r.budget,
                "days": r.days,
                "travel_type": r.travel_type,
                "num_people": r.num_people,
                "preferences": r.preferences or [],
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })
        return {"trips": result, "total": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{trip_id}")
async def get_trip_by_id(trip_id: int, db: Session = Depends(get_db)):
    """Get a specific trip by ID including full response."""
    record = db.query(TripRecord).filter(TripRecord.id == trip_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {
        "id": record.id,
        "origin": record.origin,
        "destination": record.destination,
        "budget": record.budget,
        "days": record.days,
        "travel_type": record.travel_type,
        "num_people": record.num_people,
        "preferences": record.preferences or [],
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "response": json.loads(record.response_json) if record.response_json else None,
    }


@router.delete("/history/{trip_id}")
async def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    """Delete a trip record."""
    record = db.query(TripRecord).filter(TripRecord.id == trip_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(record)
    db.commit()
    return {"message": "Trip deleted successfully"}


@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Feature 7: Aggregate stats from trip history for the dashboard."""
    try:
        records = db.query(TripRecord).all()
        if not records:
            return {"total_trips": 0, "destinations": [], "travel_styles": {}, "avg_budget": 0, "avg_days": 0, "top_origins": []}

        from collections import Counter

        destinations  = [r.destination for r in records]
        origins       = [r.origin      for r in records]
        styles        = [r.travel_type for r in records]
        budgets       = [r.budget      for r in records if r.budget]
        days_list     = [r.days        for r in records if r.days]

        dest_counts   = Counter(destinations).most_common(8)
        origin_counts = Counter(origins).most_common(5)
        style_counts  = dict(Counter(styles))

        return {
            "total_trips":    len(records),
            "destinations":   [{"name": d, "count": c} for d, c in dest_counts],
            "top_origins":    [{"name": o, "count": c} for o, c in origin_counts],
            "travel_styles":  style_counts,
            "avg_budget":     round(sum(budgets) / len(budgets)) if budgets else 0,
            "avg_days":       round(sum(days_list) / len(days_list), 1) if days_list else 0,
            "total_budget":   round(sum(budgets)) if budgets else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Rating endpoints ──────────────────────────────────────────────────────────

@router.post("/ratings")
async def save_rating(req: RatingRequest, db: Session = Depends(get_db)):
    """Save or update a star rating + review for a trip."""
    if not (1 <= req.rating <= 5):
        raise HTTPException(status_code=422, detail="Rating must be 1–5")

    # Check trip exists
    trip = db.query(TripRecord).filter(TripRecord.id == req.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Upsert: update if already rated, else create
    existing = db.query(TripRating).filter(TripRating.trip_id == req.trip_id).first()
    if existing:
        existing.rating = req.rating
        existing.review = req.review or ""
    else:
        db.add(TripRating(trip_id=req.trip_id, rating=req.rating, review=req.review or ""))
    db.commit()
    return {"success": True, "trip_id": req.trip_id, "rating": req.rating}


@router.get("/ratings/{trip_id}")
async def get_rating(trip_id: int, db: Session = Depends(get_db)):
    """Get the rating for a specific trip."""
    r = db.query(TripRating).filter(TripRating.trip_id == trip_id).first()
    if not r:
        return {"trip_id": trip_id, "rating": None, "review": None}
    return {"trip_id": trip_id, "rating": r.rating, "review": r.review}


# ── Share link endpoints ──────────────────────────────────────────────────────

@router.post("/history/{trip_id}/share")
async def create_share_link(trip_id: int, db: Session = Depends(get_db)):
    """Generate a unique share ID for a trip. Returns a shareable URL token."""
    trip = db.query(TripRecord).filter(TripRecord.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if not trip.share_id:
        trip.share_id = secrets.token_urlsafe(16)
        db.commit()

    return {"share_id": trip.share_id, "trip_id": trip_id}


@router.get("/shared/{share_id}")
async def get_shared_trip(share_id: str, db: Session = Depends(get_db)):
    """Load a trip by its public share ID (no auth required)."""
    trip = db.query(TripRecord).filter(TripRecord.share_id == share_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Shared trip not found")
    return {
        "id":          trip.id,
        "origin":      trip.origin,
        "destination": trip.destination,
        "days":        trip.days,
        "travel_type": trip.travel_type,
        "num_people":  trip.num_people,
        "created_at":  trip.created_at.isoformat() if trip.created_at else None,
        "response":    json.loads(trip.response_json) if trip.response_json else None,
    }
