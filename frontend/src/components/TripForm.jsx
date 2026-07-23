/**
 * TripForm — 4-step planning wizard
 * Step 1: Source + Destination
 * Step 2: Budget + Days + Travelers + Travel Style + Trip Type
 * Step 3: Transport Selection (fetched live for the route)
 * Step 4: Hotel Selection (fetched near arrival point)
 * Step 5: Budget Check → either "Generate Itinerary" or "Cannot Fit" screen
 */
import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'
import { API_BASE } from '../config'
const fmt = (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`

/* Rotating background slides for TripForm */
const FORM_BG_SLIDES = [
  'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1600&q=70',
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1600&q=70',
  'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1600&q=70',
  'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1600&q=70',
]

const POPULAR_DESTINATIONS = [
  { name: 'Delhi', emoji: '🏛️' }, { name: 'Goa', emoji: '🏖️' },
  { name: 'Jaipur', emoji: '🏰' }, { name: 'Mumbai', emoji: '🌆' },
  { name: 'Manali', emoji: '⛰️' }, { name: 'Agra', emoji: '🕌' },
  { name: 'Varanasi', emoji: '🙏' }, { name: 'Kerala', emoji: '🌿' },
  { name: 'Shimla', emoji: '🏔️' }, { name: 'Rishikesh', emoji: '🏄' },
  { name: 'Paris', emoji: '🗼' }, { name: 'Dubai', emoji: '🏙️' },
  { name: 'Bangkok', emoji: '🛕' }, { name: 'Bali', emoji: '🌴' },
  { name: 'Istanbul', emoji: '🕌' }, { name: 'Tokyo', emoji: '⛩️' },
  { name: 'Singapore', emoji: '🦁' }, { name: 'New York', emoji: '🗽' },
]

const PREFERENCES_LIST = [
  { id: 'nature',     label: 'Nature',       emoji: '🌿' },
  { id: 'history',    label: 'History',      emoji: '🏛️' },
  { id: 'adventure',  label: 'Adventure',    emoji: '🧗' },
  { id: 'food',       label: 'Food',         emoji: '🍜' },
  { id: 'shopping',   label: 'Shopping',     emoji: '🛍️' },
  { id: 'beach',      label: 'Beach',        emoji: '🏖️' },
  { id: 'spiritual',  label: 'Spiritual',    emoji: '🙏' },
  { id: 'art',        label: 'Art & Culture',emoji: '🎨' },
  { id: 'family',     label: 'Family',       emoji: '👨‍👩‍👧' },
  { id: 'photography',label: 'Photography',  emoji: '📸' },
  { id: 'nightlife',  label: 'Nightlife',    emoji: '🌃' },
  { id: 'luxury',     label: 'Luxury',       emoji: '💎' },
]

const TRAVEL_TYPES = [
  { id: 'budget',   label: 'Budget',   desc: 'Hostels, street food, local transport', emoji: '💚' },
  { id: 'moderate', label: 'Moderate', desc: '3-star hotels, mix of dining & travel',  emoji: '💛' },
  { id: 'luxury',   label: 'Luxury',   desc: '5-star hotels, fine dining, private cabs', emoji: '💎' },
]

const TRIP_TYPES = [
  { id: 'solo', label: 'Solo', emoji: '🧍' }, { id: 'couple', label: 'Couple', emoji: '👫' },
  { id: 'family', label: 'Family', emoji: '👨‍👩‍👧' }, { id: 'friends', label: 'Friends', emoji: '👥' },
]

const STEP_LABELS = ['Destination', 'Trip Details', 'Transport', 'Hotel', 'Review & Generate']

// ── Step indicator ────────────────────────────────────────────────────────
function StepBar({ step, total = 5 }) {
  return (
    <div className="mb-10">
      <div className="flex items-center justify-center gap-2 mb-4">
        {Array.from({ length: total }, (_, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-black transition-all duration-300 ${
              step > i + 1
                ? 'text-white shadow-lg'
                : step === i + 1
                ? 'text-white shadow-xl scale-110'
                : 'text-white/30'
            }`} style={{
              background: step > i + 1
                ? 'linear-gradient(135deg,#34d399,#059669)'
                : step === i + 1
                ? 'linear-gradient(135deg,#f59e0b,#ea580c)'
                : 'rgba(255,255,255,0.08)',
              boxShadow: step === i + 1 ? '0 0 20px rgba(245,158,11,0.5)' : 'none',
            }}>
              {step > i + 1 ? '✓' : i + 1}
            </div>
            {i < total - 1 && (
              <div className="w-14 h-0.5 rounded-full transition-all duration-500"
                style={{ background: step > i + 1 ? 'linear-gradient(90deg,#34d399,#f59e0b)' : 'rgba(255,255,255,0.08)' }} />
            )}
          </div>
        ))}
      </div>
      <div className="flex justify-center">
        <span className="text-amber-400 text-sm font-bold tracking-wide">{STEP_LABELS[step - 1]}</span>
      </div>
    </div>
  )
}

// ── Card wrapper ──────────────────────────────────────────────────────────
function Card({ children, className = '' }) {
  return (
    <div className={`rounded-3xl p-7 ${className}`}
      style={{
        background: 'rgba(6,9,24,0.75)',
        border: '1px solid rgba(255,255,255,0.08)',
        backdropFilter: 'blur(24px)',
        boxShadow: '0 8px 40px rgba(0,0,0,0.5)',
      }}>
      {children}
    </div>
  )
}

function SectionTitle({ step, children }) {
  return (
    <h2 className="font-outfit font-black text-white text-xl mb-5 flex items-center gap-3">
      <span className="w-8 h-8 rounded-xl flex items-center justify-center text-white text-sm shrink-0 font-black"
        style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>{step}</span>
      {children}
    </h2>
  )
}

// ── Cannot-Fit screen ─────────────────────────────────────────────────────
function CannotFitScreen({ budgetCheck, form, onAdjust }) {
  const s = budgetCheck.suggestions || {}
  const bd = budgetCheck.budget_breakdown || {}

  return (
    <Card>
      {/* Big warning header */}
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">😔</div>
        <h2 className="text-2xl font-black text-white mb-2">Budget Too Low for This Trip</h2>
        <p className="text-blue-300/70 text-sm max-w-md mx-auto">
          Even at the most budget-friendly level, this trip needs more than you've entered.
          Here's what you can do:
        </p>
      </div>

      {/* Current vs required */}
      <div className="grid grid-cols-2 gap-4 mb-7">
        <div className="text-center p-5 rounded-2xl" style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)' }}>
          <p className="text-xs font-black text-red-400/60 uppercase tracking-widest mb-1">Your Budget</p>
          <p className="text-3xl font-black text-red-400">{fmt(form.budget)}</p>
        </div>
        <div className="text-center p-5 rounded-2xl" style={{ background: 'rgba(251,146,60,0.12)', border: '1px solid rgba(251,146,60,0.3)' }}>
          <p className="text-xs font-black text-amber-400/60 uppercase tracking-widest mb-1">Minimum Needed</p>
          <p className="text-3xl font-black text-amber-400">{fmt(budgetCheck.min_required_budget)}</p>
        </div>
      </div>

      {/* Suggestions */}
      <div className="space-y-3 mb-7">
        <p className="text-xs font-black text-cyan-400/60 uppercase tracking-widest mb-3">💡 Suggested Actions</p>

        {/* Increase budget */}
        <button onClick={() => onAdjust('increase_budget')}
          className="w-full flex items-center gap-4 p-4 rounded-2xl text-left transition-all hover:-translate-y-0.5"
          style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)' }}>
          <span className="text-2xl">💰</span>
          <div className="flex-1">
            <div className="font-black text-white text-sm">Increase Budget to {fmt(budgetCheck.min_required_budget)}</div>
            <div className="text-xs text-blue-300/50 mt-0.5">Add {fmt(budgetCheck.suggestions?.budget_needed)} more to unlock this trip</div>
          </div>
          <span className="text-green-400 font-black">→</span>
        </button>

        {/* Reduce days */}
        {s.days_reduction && (
          <button onClick={() => onAdjust('reduce_days', s.days_reduction.days)}
            className="w-full flex items-center gap-4 p-4 rounded-2xl text-left transition-all hover:-translate-y-0.5"
            style={{ background: 'rgba(99,179,237,0.08)', border: '1px solid rgba(99,179,237,0.2)' }}>
            <span className="text-2xl">📅</span>
            <div className="flex-1">
              <div className="font-black text-white text-sm">Reduce to {s.days_reduction.days} Days</div>
              <div className="text-xs text-blue-300/50 mt-0.5">Estimated cost drops to {fmt(s.days_reduction.estimated)}</div>
            </div>
            <span className="text-cyan-400 font-black">→</span>
          </button>
        )}

        {/* Cheaper transport */}
        {s.cheaper_transport && (
          <button onClick={() => onAdjust('change_transport', s.cheaper_transport.mode)}
            className="w-full flex items-center gap-4 p-4 rounded-2xl text-left transition-all hover:-translate-y-0.5"
            style={{ background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.2)' }}>
            <span className="text-2xl">{s.cheaper_transport.emoji}</span>
            <div className="flex-1">
              <div className="font-black text-white text-sm">Switch to {s.cheaper_transport.mode}</div>
              <div className="text-xs text-blue-300/50 mt-0.5">Saves {fmt(s.cheaper_transport.saves)} on transport</div>
            </div>
            <span className="text-purple-400 font-black">→</span>
          </button>
        )}

        {/* Change destination */}
        <button onClick={() => onAdjust('change_destination')}
          className="w-full flex items-center gap-4 p-4 rounded-2xl text-left transition-all hover:-translate-y-0.5"
          style={{ background: 'rgba(248,113,113,0.08)', border: '1px solid rgba(248,113,113,0.2)' }}>
          <span className="text-2xl">🗺️</span>
          <div className="flex-1">
            <div className="font-black text-white text-sm">Choose a Nearby Destination</div>
            <div className="text-xs text-blue-300/50 mt-0.5">A closer destination reduces travel & stay costs</div>
          </div>
          <span className="text-red-400 font-black">→</span>
        </button>
      </div>
    </Card>
  )
}

// ── Budget Preview (shown in step 4) ────────────────────────────────────
function BudgetPreview({ budgetCheck, form }) {
  const bd = budgetCheck.budget_breakdown || {}
  const bf = budgetCheck
  const tierChanged = bf.feasible_tier && bf.feasible_tier !== bf.original_travel_type
  const items = [
    { icon: '🏨', label: 'Accommodation', val: bd.accommodation },
    { icon: '🍽️', label: 'Food',          val: bd.food },
    { icon: '🚗', label: 'Transport',     val: bd.transport },
    { icon: '🎟️', label: 'Activities',   val: bd.activities },
    { icon: '🛍️', label: 'Miscellaneous',val: bd.misc },
  ]
  const finalCost = bf.budget_breakdown?.adjusted_estimate || bd.total_estimated
  const within = finalCost <= form.budget
  const saves = form.budget - finalCost

  return (
    <div className="space-y-5">
      {/* Tier change notice */}
      {tierChanged && (
        <div className="flex items-start gap-3 p-4 rounded-2xl"
          style={{ background: 'rgba(251,146,60,0.12)', border: '1px solid rgba(251,146,60,0.3)' }}>
          <span className="text-2xl">⚡</span>
          <div>
            <div className="font-black text-amber-300 text-sm">Travel style auto-adjusted</div>
            <div className="text-blue-200/70 text-xs mt-0.5">
              Your requested <strong className="text-white">{bf.original_travel_type}</strong> style
              exceeded budget. Optimized to <strong className="text-amber-300">{bf.feasible_tier}</strong> style
              to fit your ₹{Number(form.budget).toLocaleString('en-IN')} budget.
            </div>
          </div>
        </div>
      )}

      {/* Adjustments made */}
      {bf.adjustments?.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-black text-cyan-400/50 uppercase tracking-widest">✂️ Optimizations applied</p>
          {bf.adjustments.map((adj, i) => (
            <div key={i} className="flex items-center gap-3 p-3 rounded-xl"
              style={{ background: 'rgba(255,255,255,0.04)' }}>
              <span className="text-lg">{adj.icon}</span>
              <span className="text-blue-200/70 text-xs flex-1">{adj.text}</span>
              <span className="text-green-400 text-xs font-black">−{fmt(adj.saves)}</span>
            </div>
          ))}
        </div>
      )}

      {/* Budget vs estimated */}
      <div className="grid grid-cols-2 gap-3">
        <div className="text-center p-4 rounded-2xl" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(99,179,237,0.1)' }}>
          <p className="text-xs font-black text-blue-300/40 uppercase tracking-widest mb-1">Your Budget</p>
          <p className="text-2xl font-black text-white">{fmt(form.budget)}</p>
        </div>
        <div className="text-center p-4 rounded-2xl" style={{
          background: within ? 'rgba(16,185,129,0.1)' : 'rgba(251,146,60,0.1)',
          border: within ? '1px solid rgba(16,185,129,0.3)' : '1px solid rgba(251,146,60,0.3)',
        }}>
          <p className="text-xs font-black text-blue-300/40 uppercase tracking-widest mb-1">Estimated Cost</p>
          <p className="text-2xl font-black" style={{ color: within ? '#34d399' : '#fb923c' }}>{fmt(finalCost)}</p>
        </div>
      </div>

      {within && saves > 0 && (
        <div className="text-center text-sm font-bold text-green-400">
          🎉 You save {fmt(saves)} with this plan
        </div>
      )}

      {/* Breakdown bars */}
      <div className="space-y-3">
        {items.map((item, i) => {
          const pct = bd.total_estimated > 0 ? Math.round((item.val / bd.total_estimated) * 100) : 0
          return (
            <div key={i}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-blue-200/70">{item.icon} {item.label}</span>
                <span className="font-black text-white">{fmt(item.val)}</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                <div className="h-full rounded-full" style={{
                  width: `${pct}%`,
                  background: 'linear-gradient(90deg, #3b82f6, #06b6d4)',
                }} />
              </div>
            </div>
          )
        })}
      </div>

      {/* Upgrade plan */}
      {bf.upgrade_plan && bf.upgrade_plan.extra_budget_needed > 0 && (
        <div className="rounded-2xl overflow-hidden"
          style={{ border: '1px solid rgba(99,179,237,0.2)' }}>
          <div className="px-5 py-3 flex items-center gap-3"
            style={{ background: 'linear-gradient(135deg, rgba(37,99,235,0.2), rgba(8,145,178,0.15))' }}>
            <span className="text-xl">🚀</span>
            <div>
              <div className="font-black text-white text-sm">Want the full experience?</div>
              <div className="text-cyan-300 text-xs mt-0.5">
                Add {fmt(bf.upgrade_plan.extra_budget_needed)} more for premium {form.destination} experience
              </div>
            </div>
          </div>
          <div className="px-5 py-4 space-y-2" style={{ background: 'rgba(13,27,42,0.6)' }}>
            {bf.upgrade_plan.items?.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                <span className="text-blue-200/70 flex-1">{item.benefit}</span>
                <span className="text-cyan-300 font-black">+{fmt(item.cost)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Surprise Me Button ───────────────────────────────────────────────────────
function SurpriseButton({ origin, budget, days, travelType, onPick }) {
  const [loading, setLoading] = useState(false)
  const [suggestion, setSuggestion] = useState(null)

  const handleSurprise = async () => {
    setLoading(true)
    setSuggestion(null)
    try {
      const params = new URLSearchParams({
        origin: origin || 'Delhi',
        budget: budget || 15000,
        days: days || 3,
        travel_type: travelType || 'moderate',
      })
      const res = await fetch(`${API_BASE}/api/surprise-destination?${params}`)
      const data = await res.json()
      setSuggestion(data)
    } catch {
      setSuggestion(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mb-5">
      <button
        type="button"
        onClick={handleSurprise}
        disabled={loading}
        className="w-full flex items-center justify-center gap-3 py-3.5 rounded-2xl font-black text-sm transition-all hover:-translate-y-0.5 disabled:opacity-60"
        style={{
          background: 'linear-gradient(135deg, rgba(139,92,246,0.15), rgba(236,72,153,0.1))',
          border: '1px solid rgba(139,92,246,0.3)',
          color: '#a78bfa',
        }}
      >
        {loading ? (
          <><span className="w-4 h-4 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" /> Picking a destination…</>
        ) : (
          <><span className="text-lg">🎲</span> Surprise Me! Let AI pick a destination</>
        )}
      </button>

      {suggestion && (
        <div className="mt-3 p-4 rounded-2xl flex items-center justify-between"
          style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.2)' }}>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">{suggestion.emoji}</span>
              <div>
                <div className="font-outfit font-black text-white">{suggestion.destination}</div>
                <div className="text-purple-300/70 text-xs">{suggestion.vibe}</div>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleSurprise}
              className="text-xs px-3 py-1.5 rounded-xl font-bold text-purple-300/70 hover:text-purple-300 transition-colors"
              style={{ background: 'rgba(139,92,246,0.1)' }}
            >
              🔄 Try again
            </button>
            <button
              type="button"
              onClick={() => { onPick(suggestion.destination); setSuggestion(null) }}
              className="text-xs px-4 py-1.5 rounded-xl font-black text-white transition-all hover:scale-105"
              style={{ background: 'linear-gradient(135deg,#8b5cf6,#ec4899)' }}
            >
              Pick this! →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main Component ───────────────────────────────────────────────────────
export default function TripForm({ onSubmit, error }) {
  const { user } = useAuth()

  const [form, setForm] = useState({
    origin: '', destination: '', budget: '', days: 3,
    travel_type: 'moderate', num_people: 2,
    preferences: [], trip_type: 'couple', preferred_transport: null,
  })
  const [step, setStep] = useState(1)
  const [bgSlide, setBgSlide] = useState(0)

  // Background slideshow
  useEffect(() => {
    const t = setInterval(() => setBgSlide(p => (p + 1) % FORM_BG_SLIDES.length), 6000)
    return () => clearInterval(t)
  }, [])

  // Transport step state
  const [transportOpts, setTransportOpts]         = useState([])
  const [loadingTransport, setLoadingTransport]   = useState(false)

  // Hotel step state
  const [arrivalPoint, setArrivalPoint]           = useState(null)
  const [hotels, setHotels]                       = useState([])
  const [loadingHotels, setLoadingHotels]         = useState(false)
  const [selectedHotel, setSelectedHotel]         = useState(null)
  const [hotelFallbackUsed, setHotelFallbackUsed] = useState(false)
  const [hotelFallbackReason, setHotelFallbackReason] = useState("")
  const [hotelSearchCenter, setHotelSearchCenter] = useState("")

  // Budget check step state
  const [budgetCheck, setBudgetCheck]             = useState(null)
  const [loadingBudget, setLoadingBudget]         = useState(false)
  const [cannotFit, setCannotFit]                 = useState(false)

  const set = (field, val) => setForm(p => ({ ...p, [field]: val }))
  const togglePref = (label) =>
    set('preferences', form.preferences.includes(label)
      ? form.preferences.filter(p => p !== label)
      : [...form.preferences, label])

  const fetchTransport = useCallback(async () => {
    if (!form.origin || !form.destination || form.num_people < 1) return
    setLoadingTransport(true)
    try {
      const res = await axios.get(`${API_BASE}/api/transport-options`, {
        params: { origin: form.origin.trim(), destination: form.destination.trim(), num_people: form.num_people },
        timeout: 20000,  // increased from 10s — Google API fallbacks can take time
      })
      setTransportOpts(res.data.options || [])
    } catch (err) {
      console.error('[TripForm] transport fetch error:', err?.message)
      // Fallback: provide Car/Cab and Train as generic options so user isn't stuck
      setTransportOpts([
        {
          mode: 'Car / Cab',
          emoji: '🚕',
          duration: '~ 4 hrs',
          fare_min: 2000,
          fare_max: 4000,
          cost_per_person: 1500,
          cost_total: 3000,
          available: true,
          recommended: true,
          tip: 'Generic estimate — exact fares shown after selecting.',
          booking_link: 'https://www.makemytrip.com/cabs/',
          price_source: 'Estimated',
        },
        {
          mode: 'Train',
          emoji: '🚂',
          duration: '~ 5 hrs',
          fare_min: 300,
          fare_max: 800,
          cost_per_person: 500,
          cost_total: 1000,
          available: true,
          recommended: false,
          tip: 'Generic estimate — check IRCTC for exact trains and fares.',
          booking_link: 'https://www.irctc.co.in/',
          price_source: 'Estimated',
        },
      ])
    } finally {
      setLoadingTransport(false)
    }
  }, [form.origin, form.destination, form.num_people])

  useEffect(() => { if (step === 3) fetchTransport() }, [step])

  // Step 4: Fetch arrival point then hotels
  const fetchHotels = useCallback(async () => {
    if (!form.preferred_transport || !form.destination) return
    setLoadingHotels(true)
    setHotels([])
    setArrivalPoint(null)
    setSelectedHotel(null)
    setHotelFallbackUsed(false)
    setHotelFallbackReason("")
    setHotelSearchCenter("")
    try {
      // 1. Get arrival point
      const apRes = await axios.get(`${API_BASE}/api/arrival-point`, {
        params: { destination: form.destination.trim(), transport_mode: form.preferred_transport },
        timeout: 8000,
      })
      const ap = apRes.data.arrival_point
      setArrivalPoint(ap)

      // 2. Fetch hotels near arrival point (backend handles all fallbacks internally)
      if (ap && ap.latitude && ap.longitude) {
        const hRes = await axios.get(`${API_BASE}/api/hotels`, {
          params: {
            destination:  form.destination.trim(),
            arrival_lat:  ap.latitude,
            arrival_lon:  ap.longitude,
            travel_style: form.travel_type,
            num_people:   form.num_people,
            num_days:     form.days,
          },
          timeout: 15000,
        })
        const hotelData = hRes.data
        setHotels(hotelData.hotels || [])
        setHotelFallbackUsed(hotelData.fallback_used || false)
        setHotelFallbackReason(hotelData.fallback_reason || "")
        setHotelSearchCenter(hotelData.search_center_name || "")

        // If still 0 hotels, try a wider radius (10km)
        if (!hotelData.hotels || hotelData.hotels.length === 0) {
          console.log('[Hotels] No results at 6km — retrying with 15km radius...')
          const hRes2 = await axios.get(`${API_BASE}/api/hotels`, {
            params: {
              destination:  form.destination.trim(),
              arrival_lat:  ap.latitude,
              arrival_lon:  ap.longitude,
              travel_style: form.travel_type,
              num_people:   form.num_people,
              num_days:     form.days,
              radius_m:     15000,
            },
            timeout: 20000,
          })
          const hotelData2 = hRes2.data
          setHotels(hotelData2.hotels || [])
          setHotelFallbackUsed(hotelData2.fallback_used || false)
          setHotelFallbackReason(hotelData2.fallback_reason || "")
          setHotelSearchCenter(hotelData2.search_center_name || "")
        }
      }
    } catch (e) {
      console.error('Hotels fetch failed:', e)
      setHotels([])
    } finally {
      setLoadingHotels(false)
    }
  }, [form.preferred_transport, form.destination, form.travel_type, form.num_people, form.days])

  useEffect(() => { if (step === 4) fetchHotels() }, [step])

  const checkBudget = async () => {
    if (!form.preferred_transport) return
    setLoadingBudget(true)
    setBudgetCheck(null)
    setCannotFit(false)
    try {
      const payload = {
        origin:              form.origin.trim(),
        destination:         form.destination.trim(),
        budget:              parseFloat(form.budget),
        days:                parseInt(form.days),
        travel_type:         form.travel_type,
        num_people:          parseInt(form.num_people),
        preferences:         form.preferences,
        preferred_transport: form.preferred_transport,
      }
      const res = await axios.post(`${API_BASE}/api/check-budget`, payload, { timeout: 20000 })
      setBudgetCheck(res.data)
      if (!res.data.can_generate) setCannotFit(true)
    } catch (err) {
      console.error('[TripForm] check-budget error:', err?.response?.data || err.message)
      // Fallback: allow generation to proceed so user is not stuck
      setBudgetCheck({ can_generate: true, feasible_tier: form.travel_type, adjustments: [], budget_breakdown: {} })
    } finally {
      setLoadingBudget(false)
    }
  }

  useEffect(() => { if (step === 5) checkBudget() }, [step])

  const handleAdjust = (action, value) => {
    switch (action) {
      case 'increase_budget':
        set('budget', budgetCheck.min_required_budget?.toString() || form.budget)
        setBudgetCheck(null); setCannotFit(false); setStep(5)
        setTimeout(checkBudget, 100); break
      case 'reduce_days':
        set('days', value)
        setBudgetCheck(null); setCannotFit(false); setStep(5)
        setTimeout(checkBudget, 100); break
      case 'change_transport':
        set('preferred_transport', value)
        setBudgetCheck(null); setCannotFit(false); setStep(5)
        setTimeout(checkBudget, 100); break
      case 'change_destination':
        setStep(1); setBudgetCheck(null); setCannotFit(false); break
    }
  }

  const handleSubmit = (e) => {
    if (e && e.preventDefault) e.preventDefault()
    if (!budgetCheck) {
      console.warn('[TripForm] handleSubmit: budgetCheck is null')
      return
    }
    if (!budgetCheck.can_generate) {
      console.warn('[TripForm] handleSubmit: can_generate=false')
      return
    }
    onSubmit({
      origin:              form.origin.trim(),
      destination:         form.destination.trim(),
      budget:              parseFloat(form.budget),
      days:                parseInt(form.days),
      travel_type:         budgetCheck.feasible_tier || form.travel_type,
      num_people:          parseInt(form.num_people),
      preferences:         form.preferences,
      preferred_transport: form.preferred_transport,
      selected_hotel_name: selectedHotel?.name || null,
      selected_hotel_lat:  selectedHotel?.latitude || null,
      selected_hotel_lon:  selectedHotel?.longitude || null,
    })
  }

  const isStep1Valid = form.origin.trim().length >= 2 && form.destination.trim().length >= 2
  const isStep2Valid = parseFloat(form.budget) >= 500 && parseInt(form.days) >= 1

  /* shared button style helpers */
  const btnAmber = { background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 0 24px rgba(245,158,11,0.4)' }
  const btnDisabled = { background: 'rgba(255,255,255,0.07)', cursor: 'not-allowed' }
  const backBtn = 'px-6 py-4 rounded-2xl font-black text-sm text-white/70 transition-all hover:text-white hover:bg-white/8'

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* ── Animated background ── */}
      <div className="fixed inset-0 z-0">
        {FORM_BG_SLIDES.map((src, i) => (
          <div key={i} className="absolute inset-0 bg-cover bg-center transition-opacity duration-[2000ms]"
            style={{ backgroundImage: `url(${src})`, opacity: i === bgSlide ? 1 : 0 }} />
        ))}
        <div className="absolute inset-0" style={{ background: 'rgba(4,6,18,0.82)' }} />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg,rgba(120,40,0,0.18) 0%,transparent 60%,rgba(6,60,90,0.15) 100%)' }} />
      </div>

      {/* ── Content ── */}
      <div className="relative z-10 min-h-screen py-10 px-4">
        <div className="max-w-3xl mx-auto">

          {/* Header */}
          <div className="text-center mb-8">
            {user && (
              <div className="inline-flex items-center gap-2 text-amber-300 text-sm font-bold mb-3 px-4 py-1.5 rounded-full"
                style={{ background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.25)' }}>
                👋 Welcome back, {user.name}!
              </div>
            )}
            <h1 className="font-outfit font-black text-white mb-2" style={{ fontSize: 'clamp(2rem,5vw,3rem)' }}>
              Plan Your Dream Trip <span className="text-gold-gradient">✨</span>
            </h1>
            <p className="text-white/45 text-base">AI validates your budget before generating — every trip fits your wallet.</p>
          </div>

          <StepBar step={step} />
          <form onSubmit={(e) => e.preventDefault()} className="space-y-5">
          {/* ─────── STEP 1: Destination ───────────────────────── */}
          {step === 1 && (
            <Card className="fade-in-up">
              <SectionTitle step={1}>Where are you going?</SectionTitle>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
                <div>
                  <label className="block text-xs font-bold text-white/50 uppercase tracking-widest mb-2">🏠 Starting From</label>
                  <input className="w-full px-4 py-3.5 rounded-2xl text-white text-sm font-medium placeholder-white/25 outline-none transition-all focus:ring-2"
                    style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', '--tw-ring-color': 'rgba(245,158,11,0.5)' }}
                    placeholder="Mumbai, Delhi, Bangalore..."
                    value={form.origin} onChange={e => set('origin', e.target.value)} required />
                </div>
                <div>
                  <label className="block text-xs font-bold text-white/50 uppercase tracking-widest mb-2">📍 Destination</label>
                  <input className="w-full px-4 py-3.5 rounded-2xl text-white text-sm font-medium placeholder-white/25 outline-none transition-all focus:ring-2"
                    style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', '--tw-ring-color': 'rgba(245,158,11,0.5)' }}
                    placeholder="Goa, Paris, Dubai..."
                    value={form.destination} onChange={e => set('destination', e.target.value)} required />
                </div>
              </div>

              {/* Surprise Me */}
              <SurpriseButton
                origin={form.origin}
                budget={form.budget}
                days={form.days}
                travelType={form.travel_type}
                onPick={(dest) => set('destination', dest)}
              />

              <div>
                <p className="text-[10px] font-black text-white/35 uppercase tracking-widest mb-3">Popular Destinations</p>
                <div className="flex flex-wrap gap-2">
                  {POPULAR_DESTINATIONS.map(d => (
                    <button key={d.name} type="button"
                      onClick={() => set('destination', d.name)}
                      className="flex items-center gap-1.5 text-sm px-3 py-2 rounded-full font-semibold transition-all"
                      style={{
                        background: form.destination === d.name ? 'linear-gradient(135deg,#f59e0b,#ea580c)' : 'rgba(255,255,255,0.05)',
                        border: form.destination === d.name ? '1px solid transparent' : '1px solid rgba(255,255,255,0.1)',
                        color: form.destination === d.name ? '#fff' : 'rgba(255,255,255,0.55)',
                        boxShadow: form.destination === d.name ? '0 0 12px rgba(245,158,11,0.4)' : 'none',
                      }}>
                      {d.emoji} {d.name}
                    </button>
                  ))}
                </div>
              </div>
              <button type="button" disabled={!isStep1Valid} onClick={() => setStep(2)}
                className="mt-7 w-full py-4 rounded-2xl font-black text-base text-white transition-all hover:-translate-y-0.5 hover:scale-[1.01]"
                style={isStep1Valid ? btnAmber : btnDisabled}>
                Continue to Trip Details →
              </button>
            </Card>
          )}

          {/* ─────── STEP 2: Trip Details ──────────────────────── */}
          {step === 2 && (
            <div className="space-y-4 fade-in-up">
              <Card>
                <SectionTitle step={2}>Trip Details</SectionTitle>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
                  <div>
                    <label className="block text-xs font-bold text-white/50 uppercase tracking-widest mb-2">💰 Total Budget (₹)</label>
                    <input type="number" min="500"
                      className="w-full px-4 py-3.5 rounded-2xl text-white text-sm font-medium placeholder-white/25 outline-none"
                      style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
                      placeholder="e.g. 20000"
                      value={form.budget} onChange={e => set('budget', e.target.value)} required />
                    <p className="text-xs text-white/30 mt-1.5">Transport deducted from this</p>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-white/50 uppercase tracking-widest mb-2">
                      📅 Days: <span className="text-amber-400">{form.days}</span>
                    </label>
                    <input type="range" min="1" max="14" value={form.days}
                      onChange={e => set('days', e.target.value)}
                      className="w-full mt-3 h-2 rounded-full cursor-pointer accent-amber-500" />
                    <div className="flex justify-between text-xs text-white/30 mt-1"><span>1</span><span>7</span><span>14</span></div>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-white/50 uppercase tracking-widest mb-2">
                      👥 Travelers: <span className="text-amber-400">{form.num_people}</span>
                    </label>
                    <div className="flex items-center gap-3 mt-3">
                      <button type="button" onClick={() => set('num_people', Math.max(1, form.num_people - 1))}
                        className="w-10 h-10 text-white rounded-xl font-black text-xl flex items-center justify-center transition-all hover:scale-110"
                        style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>−</button>
                      <span className="text-2xl font-black text-white w-8 text-center">{form.num_people}</span>
                      <button type="button" onClick={() => set('num_people', Math.min(20, form.num_people + 1))}
                        className="w-10 h-10 text-white rounded-xl font-black text-xl flex items-center justify-center transition-all hover:scale-110"
                        style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>+</button>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs font-black text-white/50 uppercase tracking-widest mb-3">🎯 Travel Style</p>
                    <div className="space-y-2">
                      {TRAVEL_TYPES.map(t => (
                        <button key={t.id} type="button" onClick={() => set('travel_type', t.id)}
                          className="w-full flex items-center gap-3 p-3.5 rounded-2xl text-left transition-all"
                          style={{
                            background: form.travel_type === t.id ? 'rgba(245,158,11,0.12)' : 'rgba(255,255,255,0.04)',
                            border: form.travel_type === t.id ? '1px solid rgba(245,158,11,0.4)' : '1px solid rgba(255,255,255,0.08)',
                            boxShadow: form.travel_type === t.id ? '0 0 16px rgba(245,158,11,0.15)' : 'none',
                          }}>
                          <span className="text-2xl">{t.emoji}</span>
                          <div>
                            <div className="font-black text-sm text-white">{t.label}</div>
                            <div className="text-xs text-white/35 mt-0.5">{t.desc}</div>
                          </div>
                          {form.travel_type === t.id && <span className="ml-auto text-amber-400 font-black">✓</span>}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs font-black text-white/50 uppercase tracking-widest mb-3">🧳 Who's Travelling?</p>
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      {TRIP_TYPES.map(t => (
                        <button key={t.id} type="button" onClick={() => set('trip_type', t.id)}
                          className="p-3 rounded-2xl text-center transition-all"
                          style={{
                            background: form.trip_type === t.id ? 'linear-gradient(135deg,#f59e0b,#ea580c)' : 'rgba(255,255,255,0.04)',
                            border: form.trip_type === t.id ? '1px solid transparent' : '1px solid rgba(255,255,255,0.08)',
                          }}>
                          <div className="text-xl mb-0.5">{t.emoji}</div>
                          <div className="text-xs font-bold text-white">{t.label}</div>
                        </button>
                      ))}
                    </div>
                    <p className="text-xs font-black text-white/50 uppercase tracking-widest mb-3">❤️ Interests</p>
                    <div className="flex flex-wrap gap-1.5">
                      {PREFERENCES_LIST.map(p => (
                        <button key={p.id} type="button" onClick={() => togglePref(p.label)}
                          className="flex items-center gap-1 px-2.5 py-1.5 rounded-full text-xs font-semibold transition-all"
                          style={{
                            background: form.preferences.includes(p.label) ? 'linear-gradient(135deg,#f59e0b,#ea580c)' : 'rgba(255,255,255,0.05)',
                            border: form.preferences.includes(p.label) ? '1px solid transparent' : '1px solid rgba(255,255,255,0.1)',
                            color: form.preferences.includes(p.label) ? '#fff' : 'rgba(255,255,255,0.5)',
                          }}>
                          {p.emoji} {p.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
              <div className="flex gap-3">
                <button type="button" onClick={() => setStep(1)} className={backBtn}
                  style={{ border: '1px solid rgba(255,255,255,0.12)' }}>← Back</button>
                <button type="button" disabled={!isStep2Valid} onClick={() => setStep(3)}
                  className="flex-1 py-4 rounded-2xl font-black text-base text-white transition-all hover:-translate-y-0.5"
                  style={isStep2Valid ? btnAmber : btnDisabled}>
                  Fetch Transport Options →
                </button>
              </div>
            </div>
          )}

          {/* ─────── STEP 3: Transport Selection ──────────────── */}
          {step === 3 && (
            <div className="space-y-4 fade-in-up">
              <Card>
                <SectionTitle step={3}>How will you travel?</SectionTitle>
                <p className="text-white/45 text-sm mb-6">
                  Select your preferred transport from{' '}
                  <strong className="text-amber-300">{form.origin}</strong> to{' '}
                  <strong className="text-amber-300">{form.destination}</strong>.
                  Cost will be deducted from your budget before planning stays and activities.
                </p>

                {loadingTransport ? (
                  <div className="flex items-center gap-3 py-10 justify-center">
                    <span className="w-6 h-6 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
                    <span className="text-white/50 text-sm">Fetching transport options...</span>
                  </div>
                ) : transportOpts.length === 0 ? (
                  <div className="text-center py-10">
                    <div className="text-4xl mb-3">🔍</div>
                    <p className="text-white/40 text-sm mb-4">No specific routes found for this journey.</p>
                    <button type="button" onClick={() => { set('preferred_transport', 'Car / Cab'); setStep(4) }}
                      className="px-6 py-3 rounded-2xl font-black text-sm text-white transition-all"
                      style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
                      Continue with Car / Cab →
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {transportOpts.map((opt, i) => {
                      const isSelected = form.preferred_transport === opt.mode
                      const hasClasses = opt.classes && opt.classes.length > 1
                      return (
                        <div key={i}
                          onClick={() => set('preferred_transport', opt.mode)}
                          className="rounded-2xl cursor-pointer transition-all duration-200 relative overflow-hidden"
                          style={{
                            background: isSelected ? 'rgba(245,158,11,0.08)' : 'rgba(255,255,255,0.03)',
                            border: isSelected ? '1px solid rgba(245,158,11,0.45)' : '1px solid rgba(255,255,255,0.09)',
                            boxShadow: isSelected ? '0 0 20px rgba(245,158,11,0.12)' : 'none',
                          }}>

                          {/* Top accent line when selected */}
                          {isSelected && (
                            <div className="absolute top-0 left-0 right-0 h-0.5"
                              style={{ background: 'linear-gradient(90deg,#f59e0b,#ea580c)' }} />
                          )}

                          {/* ── Main row ── */}
                          <div className="flex items-start gap-4 p-5">
                            {/* Emoji */}
                            <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0"
                              style={{
                                background: isSelected ? 'rgba(245,158,11,0.15)' : 'rgba(255,255,255,0.05)',
                                border: isSelected ? '1px solid rgba(245,158,11,0.3)' : '1px solid rgba(255,255,255,0.08)',
                              }}>
                              {opt.emoji}
                            </div>

                            {/* Details */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="font-outfit font-black text-white text-lg">{opt.mode}</span>
                                {opt.recommended && (
                                  <span className="text-[10px] font-black px-2.5 py-0.5 rounded-full text-white"
                                    style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>★ Best Pick</span>
                                )}
                                {isSelected && (
                                  <span className="text-[10px] font-black px-2.5 py-0.5 rounded-full text-white"
                                    style={{ background: 'rgba(52,211,153,0.8)' }}>✓ Selected</span>
                                )}
                              </div>
                              <div className="text-white/40 text-xs mt-1 flex items-center gap-3">
                                <span>⏱ {opt.duration}</span>
                                {opt.fare_label && (
                                  <span className="text-amber-400/70 font-semibold">{opt.fare_label}</span>
                                )}
                              </div>
                              {opt.tip && (
                                <div className="text-white/30 text-xs mt-1.5 leading-relaxed">💡 {opt.tip}</div>
                              )}
                            </div>

                            {/* Fare — right side */}
                            <div className="text-right shrink-0">
                              {opt.fare_label ? (
                                <>
                                  <div className="font-outfit font-black text-amber-300 text-base leading-tight">{opt.fare_label}</div>
                                  <div className="text-white/30 text-xs mt-0.5">per person (one-way)</div>
                                </>
                              ) : (
                                <>
                                  <div className="font-outfit font-black text-amber-300 text-xl">{fmt(opt.cost_per_person)}</div>
                                  <div className="text-white/30 text-xs">per person</div>
                                </>
                              )}
                              {/* Price source badge */}
                              {opt.price_source && (
                                <div className="mt-1">
                                  <span className="text-[9px] font-black px-1.5 py-0.5 rounded-full"
                                    style={{
                                      background: opt.price_source === 'Live'
                                        ? 'rgba(52,211,153,0.2)' : opt.price_source === 'Cached'
                                        ? 'rgba(99,179,237,0.2)' : 'rgba(255,255,255,0.08)',
                                      color: opt.price_source === 'Live'
                                        ? '#34d399' : opt.price_source === 'Cached'
                                        ? '#63b3ed' : 'rgba(255,255,255,0.35)',
                                      border: `1px solid ${opt.price_source === 'Live'
                                        ? 'rgba(52,211,153,0.3)' : opt.price_source === 'Cached'
                                        ? 'rgba(99,179,237,0.3)' : 'rgba(255,255,255,0.1)'}`,
                                    }}>
                                    {opt.price_source === 'Live' ? '🟢 Live' : opt.price_source === 'Cached' ? '🔵 Cached' : '⚪ Estimated'}
                                  </span>
                                </div>
                              )}
                              <div className="text-white/45 text-sm font-bold mt-1">
                                {fmt(opt.cost_total)} <span className="text-white/25 font-normal text-xs">total</span>
                              </div>
                              <div className="flex items-center gap-1 mt-1.5 justify-end">
                                {opt.booking_link && (
                                  <a href={opt.booking_link} target="_blank" rel="noopener noreferrer"
                                    className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full text-white/60 hover:text-white transition-colors"
                                    style={{ background: 'rgba(255,255,255,0.07)' }}
                                    onClick={e => e.stopPropagation()}>
                                    Book ↗
                                  </a>
                                )}
                                {opt.booking_link_alt && (
                                  <a href={opt.booking_link_alt} target="_blank" rel="noopener noreferrer"
                                    className="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full text-white/40 hover:text-white/70 transition-colors"
                                    style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
                                    onClick={e => e.stopPropagation()}>
                                    Alt ↗
                                  </a>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* ── Airline breakdown for flights ── */}
                          {opt.mode === "Flight" && opt.airlines && opt.airlines.length > 0 && (
                            <div className="px-5 pb-4">
                              <div className="text-[10px] font-black text-white/25 uppercase tracking-widest mb-2 flex items-center gap-2">
                                <span>✈️ Available Airlines</span>
                                <span className="text-white/15">· estimated fares (one-way)</span>
                              </div>
                              <div className="space-y-2">
                                {opt.airlines.map((a, j) => (
                                  <div key={j}
                                    className="flex items-center justify-between px-4 py-2.5 rounded-xl"
                                    style={{
                                      background: j === 0 ? 'rgba(245,158,11,0.07)' : 'rgba(255,255,255,0.03)',
                                      border: j === 0 ? '1px solid rgba(245,158,11,0.2)' : '1px solid rgba(255,255,255,0.05)',
                                    }}>
                                    <div className="flex items-center gap-3">
                                      <span className="text-base">✈️</span>
                                      <div>
                                        <div className="text-white/80 text-sm font-bold">{a.airline}</div>
                                        <div className="text-white/30 text-[10px]">{a.note}</div>
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <div className="font-outfit font-black text-amber-300 text-sm">{a.fare_label}</div>
                                      <div className="text-white/25 text-[10px]">per person · one-way</div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                              <a href={opt.booking_link} target="_blank" rel="noopener noreferrer"
                                className="flex items-center justify-center gap-2 mt-3 py-2 rounded-xl text-xs font-bold text-white/50 hover:text-amber-300 transition-colors"
                                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}
                                onClick={e => e.stopPropagation()}>
                                🔗 Search live prices on Google Flights →
                              </a>
                            </div>
                          )}

                          {/* ── Class breakdown (Train / Bus sub-options) ── */}
                          {opt.mode !== "Flight" && hasClasses && (
                            <div className="px-5 pb-4">
                              <div className="text-[10px] font-black text-white/25 uppercase tracking-widest mb-2">
                                Available Classes
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                {opt.classes.map((cls, j) => (
                                  <div key={j}
                                    className="rounded-xl p-3"
                                    style={{
                                      background: cls.recommended ? 'rgba(245,158,11,0.07)' : 'rgba(255,255,255,0.03)',
                                      border: cls.recommended ? '1px solid rgba(245,158,11,0.2)' : '1px solid rgba(255,255,255,0.06)',
                                    }}>
                                    <div className="flex items-center gap-1.5 mb-1">
                                      <span className="text-white/60 text-xs font-semibold">{cls.class}</span>
                                      {cls.recommended && (
                                        <span className="text-[9px] text-amber-400 font-black">✦ Rec</span>
                                      )}
                                    </div>
                                    <div className="font-outfit font-black text-amber-300 text-sm">
                                      {fmt(cls.fare_min)}–{fmt(cls.fare_max)}
                                    </div>
                                    {cls.note && (
                                      <div className="text-white/25 text-[10px] mt-1 leading-tight">{cls.note}</div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </Card>

              {/* Budget remaining after transport */}
              {form.preferred_transport && (() => {
                const selOpt = transportOpts.find(o => o.mode === form.preferred_transport)
                const transportCost = selOpt?.cost_total || 0
                const remaining = parseFloat(form.budget) - transportCost
                const pct = form.budget > 0 ? Math.round((transportCost / form.budget) * 100) : 0
                return (
                  <Card>
                    <div className="flex items-start gap-4">
                      <div className="flex-1">
                        <p className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest mb-2">
                          Budget After Transport
                        </p>
                        <div className="flex items-baseline gap-2 flex-wrap">
                          <span className="text-white/50 text-sm">{fmt(form.budget)}</span>
                          <span className="text-white/30">−</span>
                          <span className="text-amber-300 font-bold text-sm">{fmt(transportCost)} transport</span>
                          <span className="text-white/30">=</span>
                          <span className="font-outfit font-black text-xl" style={{ color: remaining >= 0 ? '#34d399' : '#f87171' }}>
                            {fmt(Math.max(0, remaining))}
                          </span>
                          <span className="text-white/30 text-xs">remaining</span>
                        </div>
                        <p className="text-white/30 text-xs mt-2">
                          {pct}% of budget used for transport · remaining plans hotels, food & activities
                        </p>
                        {/* Mini bar */}
                        <div className="mt-3 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                          <div className="h-full rounded-full"
                            style={{ width: `${Math.min(pct, 100)}%`, background: 'linear-gradient(90deg,#f59e0b,#ea580c)' }} />
                        </div>
                      </div>
                      <div className="text-4xl">{selOpt?.emoji || '🚗'}</div>
                    </div>
                  </Card>
                )
              })()}

              <div className="flex gap-3">
                <button type="button" onClick={() => setStep(2)} className={backBtn}
                  style={{ border: '1px solid rgba(255,255,255,0.12)' }}>← Back</button>
                <button type="button" disabled={!form.preferred_transport} onClick={() => setStep(4)}
                  className="flex-1 py-4 rounded-2xl font-black text-base text-white transition-all hover:-translate-y-0.5"
                  style={form.preferred_transport ? btnAmber : btnDisabled}>
                  Select Hotel →
                </button>
              </div>
            </div>
          )}

          {/* ─────── STEP 4: Hotel Selection ───────────────────── */}
          {step === 4 && (
            <div className="space-y-4 fade-in-up">
              <Card>
                <SectionTitle step={4}>Choose Your Hotel</SectionTitle>

                {/* Arrival point info */}
                {arrivalPoint && (
                  <div className="flex items-center gap-3 p-4 rounded-2xl mb-5"
                    style={{ background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)' }}>
                    <span className="text-2xl flex-shrink-0">
                      {arrivalPoint.type === 'airport' ? '✈️' : arrivalPoint.type === 'railway' ? '🚂' : arrivalPoint.type === 'bus' ? '🚌' : arrivalPoint.type === 'port' ? '🚢' : '📍'}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest">Arrival Point</p>
                      <p className="font-outfit font-black text-white text-sm truncate">{arrivalPoint.name}</p>
                      <p className="text-white/35 text-xs mt-0.5 truncate">{arrivalPoint.address}</p>
                    </div>
                    {arrivalPoint.maps_url && (
                      <a href={arrivalPoint.maps_url} target="_blank" rel="noopener noreferrer"
                        className="text-amber-400 text-xs font-bold hover:text-amber-300 flex-shrink-0">Map ↗</a>
                    )}
                  </div>
                )}

                <p className="text-white/40 text-sm mb-5">
                  Hotels near your arrival point in <strong className="text-amber-300">{form.destination}</strong>.
                  Select one to include it in your trip plan.
                </p>

                {/* Fallback notice — shown only when city-center fallback was triggered */}
                {!loadingHotels && hotelFallbackUsed && (
                  <div className="flex items-start gap-3 p-4 rounded-2xl mb-5"
                    style={{ background: 'rgba(251,146,60,0.08)', border: '1px solid rgba(251,146,60,0.3)' }}>
                    <span className="text-2xl flex-shrink-0">⚠️</span>
                    <div>
                      <p className="font-black text-amber-300 text-sm">No verified hotels found near arrival point</p>
                      <p className="text-white/50 text-xs mt-1 leading-relaxed">{hotelFallbackReason}</p>
                    </div>
                  </div>
                )}

                {/* City-center fallback header */}
                {!loadingHotels && hotelFallbackUsed && hotels.length > 0 && (
                  <div className="flex items-center gap-2 mb-4">
                    <div className="h-px flex-1" style={{ background: 'rgba(255,255,255,0.08)' }} />
                    <span className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest px-3 py-1 rounded-full"
                      style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)' }}>
                      🏨 Popular hotels in {form.destination}
                    </span>
                    <div className="h-px flex-1" style={{ background: 'rgba(255,255,255,0.08)' }} />
                  </div>
                )}

                {loadingHotels ? (
                  <div className="flex items-center gap-3 py-10 justify-center">
                    <span className="w-6 h-6 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
                    <span className="text-white/50 text-sm">Finding hotels near arrival point...</span>
                  </div>
                ) : hotels.length === 0 ? (
                  <div className="text-center py-10">
                    <div className="text-4xl mb-3">⚠️</div>
                    <p className="text-amber-300 text-sm font-bold mb-1">
                      No verified hotels found near {arrivalPoint?.name || 'arrival point'}
                    </p>
                    <p className="text-white/35 text-xs mb-6 max-w-sm mx-auto leading-relaxed">
                      Our live search returned no results for this area. You can retry,
                      or continue and search hotels manually on MakeMyTrip / Booking.com.
                    </p>
                    <div className="flex flex-col gap-3 items-center">
                      <button type="button"
                        onClick={fetchHotels}
                        className="px-6 py-3 rounded-2xl font-black text-sm text-white transition-all hover:-translate-y-0.5"
                        style={{ background: 'linear-gradient(135deg,#3b82f6,#06b6d4)' }}>
                        🔄 Retry Hotel Search
                      </button>
                      <button type="button" onClick={() => setStep(5)}
                        className="px-6 py-3 rounded-2xl font-black text-sm text-white/70 transition-all hover:text-white"
                        style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)' }}>
                        Continue Without Hotel →
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {hotels.map((hotel, i) => {
                      const isSelected = selectedHotel?.place_id === hotel.place_id
                      const stars = Math.round(hotel.rating)
                      return (
                        <div key={i}
                          onClick={() => setSelectedHotel(hotel)}
                          className="rounded-2xl cursor-pointer transition-all duration-200 relative"
                          style={{
                            background: isSelected ? 'rgba(245,158,11,0.08)' : 'rgba(255,255,255,0.03)',
                            border: isSelected ? '1px solid rgba(245,158,11,0.45)' : '1px solid rgba(255,255,255,0.08)',
                            boxShadow: isSelected ? '0 0 20px rgba(245,158,11,0.12)' : 'none',
                          }}>
                          {isSelected && (
                            <div className="absolute top-0 left-0 right-0 h-0.5 rounded-t-2xl"
                              style={{ background: 'linear-gradient(90deg,#f59e0b,#ea580c)' }} />
                          )}
                          <div className="flex items-start gap-4 p-4">
                            {/* Icon */}
                            <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                              style={{ background: isSelected ? 'rgba(245,158,11,0.15)' : 'rgba(255,255,255,0.05)' }}>
                              🏨
                            </div>
                            {/* Details */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="font-outfit font-black text-white text-base leading-tight">{hotel.name}</span>
                                {isSelected && (
                                  <span className="text-[10px] font-black px-2 py-0.5 rounded-full text-white"
                                    style={{ background: 'rgba(52,211,153,0.8)' }}>✓ Selected</span>
                                )}
                              </div>
                              {/* Stars */}
                              <div className="flex items-center gap-1.5 mt-1">
                                <span className="text-amber-400 text-sm">{'★'.repeat(stars)}{'☆'.repeat(5 - stars)}</span>
                                <span className="text-white/50 text-xs">{hotel.rating.toFixed(1)}</span>
                                {hotel.user_ratings_total > 0 && (
                                  <span className="text-white/30 text-xs">({hotel.user_ratings_total.toLocaleString()} reviews)</span>
                                )}
                              </div>
                              <p className="text-white/35 text-xs mt-1 truncate">📍 {hotel.address}</p>
                              <p className="text-white/25 text-xs mt-0.5">
                                🚶 {hotel.distance_from_arrival_km} km {hotelFallbackUsed ? 'from city center' : 'from arrival point'}
                              </p>
                            </div>
                            {/* Price */}
                            <div className="text-right flex-shrink-0">
                              <div className="font-outfit font-black text-amber-300 text-sm leading-tight">{hotel.price_label}</div>
                              <div className="text-white/25 text-[10px] mt-0.5">{hotel.price_source}</div>
                              <div className="text-white/30 text-xs font-semibold mt-1">
                                ≈ {fmt(hotel.price_per_night_min * parseInt(form.days))}–{fmt(hotel.price_per_night_max * parseInt(form.days))} total
                              </div>
                              {hotel.maps_url && (
                                <a href={hotel.maps_url} target="_blank" rel="noopener noreferrer"
                                  className="inline-block mt-1.5 text-[10px] font-bold px-2 py-0.5 rounded-full text-white/50 hover:text-amber-300 transition-colors"
                                  style={{ background: 'rgba(255,255,255,0.06)' }}
                                  onClick={e => e.stopPropagation()}>
                                  View on Maps ↗
                                </a>
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </Card>

              {/* Selected hotel summary */}
              {selectedHotel && (
                <Card>
                  <p className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest mb-2">Selected Hotel</p>
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="font-outfit font-black text-white truncate">{selectedHotel.name}</p>
                      <p className="text-white/40 text-xs mt-0.5">
                        {parseInt(form.days)} nights · {selectedHotel.price_label}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="font-outfit font-black text-amber-300 text-lg">
                        {fmt(selectedHotel.price_per_night_min * parseInt(form.days))}
                      </p>
                      <p className="text-white/30 text-xs">estimated stay cost</p>
                    </div>
                  </div>
                </Card>
              )}

              <div className="flex gap-3">
                <button type="button" onClick={() => setStep(3)} className={backBtn}
                  style={{ border: '1px solid rgba(255,255,255,0.12)' }}>← Back</button>
                <button type="button" onClick={() => setStep(5)}
                  className="flex-1 py-4 rounded-2xl font-black text-base text-white transition-all hover:-translate-y-0.5"
                  style={btnAmber}>
                  {selectedHotel ? 'Check Budget Feasibility →' : 'Skip & Check Budget →'}
                </button>
              </div>
            </div>
          )}

          {/* ─────── STEP 5: Budget Check & Generate ──────────── */}
          {step === 5 && (
            <div className="space-y-4 fade-in-up">
              {loadingBudget ? (
                <Card>
                  <div className="flex flex-col items-center gap-4 py-10">
                    <div className="w-14 h-14 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    <div className="text-center">
                      <p className="text-white font-black text-lg">Checking Budget Feasibility</p>
                      <p className="text-blue-300/60 text-sm mt-1">Optimizing trip to fit ₹{Number(form.budget).toLocaleString('en-IN')}...</p>
                    </div>
                  </div>
                </Card>
              ) : cannotFit && budgetCheck ? (
                <>
                  <CannotFitScreen budgetCheck={budgetCheck} form={form} onAdjust={handleAdjust} />
                  <button type="button" onClick={() => setStep(3)}
                    className="w-full px-6 py-4 rounded-2xl font-black text-sm text-white border border-white/20 hover:bg-white/10 transition-all">
                    ← Change Transport
                  </button>
                </>
              ) : budgetCheck ? (
                <>
                  <Card>
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-12 h-12 bg-green-500/20 border border-green-500/30 rounded-2xl flex items-center justify-center text-2xl">✅</div>
                      <div>
                        <h2 className="text-xl font-black text-white">Budget Validated!</h2>
                        <p className="text-blue-300/60 text-sm">
                          Trip optimized to fit{' '}
                          <span className="text-cyan-300 font-bold">{fmt(form.budget)}</span>
                          {budgetCheck.feasible_tier !== form.travel_type && (
                            <span className="text-amber-400"> · style adjusted to {budgetCheck.feasible_tier}</span>
                          )}
                        </p>
                      </div>
                    </div>
                    <BudgetPreview budgetCheck={budgetCheck} form={form} />
                  </Card>

                  {/* Trip summary */}
                  <Card>
                    <p className="text-xs font-black text-blue-300/40 uppercase tracking-widest mb-4">📋 Your Trip</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { icon: '✈️', label: 'Route',     val: `${form.origin} → ${form.destination}` },
                        { icon: '📅', label: 'Duration',  val: `${form.days} Days` },
                        { icon: '🚗', label: 'Transport', val: form.preferred_transport },
                        { icon: '👥', label: 'Travelers', val: `${form.num_people} ${form.trip_type}` },
                      ].map((item, i) => (
                        <div key={i} className="rounded-2xl p-3 text-center"
                          style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(99,179,237,0.1)' }}>
                          <div className="text-xl mb-1">{item.icon}</div>
                          <div className="text-xs text-blue-300/40 font-medium">{item.label}</div>
                          <div className="text-sm font-black text-white truncate">{item.val}</div>
                        </div>
                      ))}
                    </div>
                    {/* Hotel row */}
                    {selectedHotel && (
                      <div className="mt-3 flex items-center gap-3 p-3 rounded-2xl"
                        style={{ background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)' }}>
                        <span className="text-xl">🏨</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-amber-400/60 font-bold uppercase tracking-widest">Hotel</p>
                          <p className="text-sm font-black text-white truncate">{selectedHotel.name}</p>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <p className="text-amber-300 text-sm font-black">{selectedHotel.price_label}</p>
                          <p className="text-white/30 text-xs">⭐ {selectedHotel.rating.toFixed(1)}</p>
                        </div>
                      </div>
                    )}
                    {!selectedHotel && (
                      <p className="text-white/25 text-xs text-center mt-3">No hotel selected — accommodation cost estimated from budget model</p>
                    )}
                  </Card>

                  {error && (
                    <Card>
                      <div className="flex items-start gap-3">
                        <span className="text-red-400 text-xl shrink-0">⚠️</span>
                        <div>
                          <p className="text-red-300 font-black text-sm">Could not generate itinerary</p>
                          <p className="text-red-300/70 text-sm mt-0.5">{error}</p>
                        </div>
                      </div>
                    </Card>
                  )}

                  <div className="flex gap-3">
                    <button type="button" onClick={() => setStep(3)}
                      className={backBtn} style={{ border: '1px solid rgba(255,255,255,0.12)' }}>
                      ← Change Transport
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault()
                        if (!budgetCheck || loadingBudget) return
                        if (!budgetCheck.can_generate) return
                        handleSubmit(e)
                      }}
                      disabled={loadingBudget || !budgetCheck?.can_generate}
                      className="flex-1 py-5 rounded-2xl font-black text-lg text-white transition-all hover:-translate-y-0.5 hover:scale-[1.01]"
                      style={{
                        background: (loadingBudget || !budgetCheck?.can_generate)
                          ? 'rgba(255,255,255,0.1)'
                          : 'linear-gradient(135deg,#f59e0b,#ea580c,#7c3aed)',
                        boxShadow: (loadingBudget || !budgetCheck?.can_generate)
                          ? 'none'
                          : '0 0 30px rgba(245,158,11,0.4)',
                        cursor: (loadingBudget || !budgetCheck?.can_generate) ? 'not-allowed' : 'pointer',
                      }}>
                      {loadingBudget ? '⏳ Validating budget...' : '✨ Generate My Itinerary'}
                    </button>
                  </div>
                  <p className="text-center text-xs text-white/25">🤖 Gemini AI + ML · 10–30 seconds</p>
                </>
              ) : null}
            </div>
          )}

        </form>
      </div>
    </div>
  </div>
  )
}
