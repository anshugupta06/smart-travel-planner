"""
Chat Router — Travel assistant chatbot.
Chain: Groq (primary, llama-3.1-8b-instant)
    → OpenRouter fallback (free Llama/Mistral models via httpx — no extra package)
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import os
import httpx

router = APIRouter(prefix="/api", tags=["Chat"])

# ── Free OpenRouter models to try in order ───────────────────────────────────
# All marked :free — no credit consumed
OPENROUTER_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
]

GROQ_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
]


# ── Pydantic models ───────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str       # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    destination: Optional[str] = None
    origin: Optional[str] = None
    days: Optional[int] = None
    budget: Optional[float] = None
    travel_type: Optional[str] = None
    num_people: Optional[int] = None
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    source: Optional[str] = None   # "groq" | "openrouter" — for debugging


# ── Prompt builder ────────────────────────────────────────────────────────────

def _build_prompt(req: ChatRequest) -> str:
    ctx_parts = []
    if req.destination:  ctx_parts.append(f"Destination: {req.destination}")
    if req.origin:       ctx_parts.append(f"Travelling from: {req.origin}")
    if req.days:         ctx_parts.append(f"Duration: {req.days} days")
    if req.budget:       ctx_parts.append(f"Budget: ₹{req.budget:,.0f}")
    if req.travel_type:  ctx_parts.append(f"Travel style: {req.travel_type}")
    if req.num_people:   ctx_parts.append(f"Travellers: {req.num_people}")

    trip_ctx = "\n".join(ctx_parts) or "No trip context provided."

    history_block = ""
    if req.history:
        lines = [
            f"{'User' if m.role == 'user' else 'Assistant'}: {m.content}"
            for m in req.history[-6:]
        ]
        history_block = "CONVERSATION HISTORY:\n" + "\n".join(lines) + "\n\n"

    dest = req.destination or "their destination"
    style = req.travel_type or "moderate"

    return f"""You are a friendly, knowledgeable travel assistant inside a Smart Travel Planner app.

CURRENT TRIP CONTEXT:
{trip_ctx}

{history_block}USER QUESTION: {req.message}

INSTRUCTIONS:
- Answer specifically about {dest}.
- Hotel prices: give realistic INR ranges for {dest} ({style} style).
- Transport: approximate fares between {req.origin or 'origin'} and {dest}.
- Attractions: entry fees, best visiting times, tips.
- Food: local dishes with cost per meal.
- Format lists with bullet points. Use ₹ for prices.
- If unsure of exact prices give a realistic range and note it may vary.
- Keep response under 300 words."""


# ── LLM callers ───────────────────────────────────────────────────────────────

def _try_groq(prompt: str) -> Optional[str]:
    """Try Groq models in sequence. Returns text or None."""
    try:
        from services.llm_service import _groq_client
        if not _groq_client:
            return None
        for model in GROQ_MODELS:
            try:
                resp = _groq_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=700,
                    temperature=0.6,
                )
                text = resp.choices[0].message.content.strip()
                print(f"[ChatRouter] ✅ Groq → {model}")
                return text
            except Exception as e:
                err = str(e)
                if "401" in err or "invalid_api_key" in err.lower():
                    print(f"[ChatRouter] Groq invalid key, skipping all models")
                    return None
                if "429" in err or "rate_limit" in err.lower():
                    print(f"[ChatRouter] Groq {model} rate limited, trying next…")
                    continue
                print(f"[ChatRouter] Groq {model} error: {e}")
                break
        return None
    except Exception as e:
        print(f"[ChatRouter] Groq setup error: {e}")
        return None


def _try_openrouter(prompt: str) -> Optional[str]:
    """Call OpenRouter with free Llama/Mistral models via httpx. Returns text or None."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        print("[ChatRouter] No OPENROUTER_API_KEY set")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",   # required by OpenRouter
        "X-Title": "Smart Travel Planner",
    }

    for model in OPENROUTER_MODELS:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 700,
                "temperature": 0.6,
            }
            r = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25.0,
            )
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"].strip()
                print(f"[ChatRouter] ✅ OpenRouter → {model}")
                return text
            elif r.status_code == 429:
                print(f"[ChatRouter] OpenRouter {model} rate limited, trying next…")
                continue
            else:
                print(f"[ChatRouter] OpenRouter {model} HTTP {r.status_code}: {r.text[:200]}")
                continue
        except Exception as e:
            print(f"[ChatRouter] OpenRouter {model} error: {e}")
            continue

    return None


# ── Health endpoint ───────────────────────────────────────────────────────────

@router.get("/chat/health")
async def chat_health():
    from services.llm_service import _groq_client
    or_key = os.getenv("OPENROUTER_API_KEY", "")
    return {
        "status": "ok",
        "groq_ready": bool(_groq_client),
        "openrouter_ready": bool(or_key),
        "openrouter_key_prefix": or_key[:12] + "…" if or_key else "not set",
    }


# ── Main chat endpoint ────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def travel_chat(req: ChatRequest):
    prompt = _build_prompt(req)

    # 1. Groq (fast, generous free tier)
    reply = _try_groq(prompt)
    if reply:
        return ChatResponse(reply=reply, source="groq")

    # 2. OpenRouter (free Llama / Mistral models)
    reply = _try_openrouter(prompt)
    if reply:
        return ChatResponse(reply=reply, source="openrouter")

    # 3. Both exhausted
    dest = req.destination or "your destination"
    return ChatResponse(
        reply=(
            f"Both AI services are temporarily unavailable (rate limits). "
            f"Please wait a minute and try again. "
            f"For now, you can check MakeMyTrip or Booking.com for {dest} prices."
        ),
        source="none",
    )
