# Smart Travel Planner 🌍✈️

An AI-powered travel planning system using a hybrid LLM + Machine Learning approach.

## Features
- **Day-wise itinerary generation** using Google Gemini AI
- **Attraction ranking** with ML-based multi-criteria scoring
- **Route optimization** using nearest-neighbor TSP algorithm
- **Budget estimation** with distance-based regression model
- **Live weather** via OpenWeatherMap API
- **Google Places API** with comprehensive fallback data
- **Trip history** stored in SQLite

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite + TailwindCSS |
| Backend | FastAPI (Python) |
| Database | SQLite + SQLAlchemy |
| AI | Google Gemini 1.5 Flash |
| ML | scikit-learn, numpy, pandas |
| APIs | Google Places, OpenWeatherMap |

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
# Add your API keys to .env
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Quick Start (Windows)
Double-click `start_backend.bat` and `start_frontend.bat` in two separate terminals.

## API Keys (.env)
```
GEMINI_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_key
GOOGLE_PLACES_API_KEY=your_google_places_key
DATABASE_URL=sqlite:///./travel_planner.db
```

## API Endpoints
- `POST /api/plan-trip` — Generate full itinerary
- `GET /api/destinations/popular` — Popular destinations list
- `GET /api/history` — Trip history
- `GET /api/history/{id}` — Single trip details
- `GET /docs` — Interactive API documentation

## Hybrid AI Architecture

```
User Input
    │
    ▼
Google Places API ──► Fallback Curated Data
    │
    ▼
ML Scoring (Multi-criteria weighted ranking)
    │
    ▼
Route Optimization (Nearest-neighbor TSP)
    │
    ▼
Budget Prediction (Regression-based model)
    │
    ▼
Gemini LLM (Narrative itinerary generation)
    │
    ▼
Complete Personalized Itinerary
```
Live demo: https://smart-travel-planner-gules-one.vercel.app
