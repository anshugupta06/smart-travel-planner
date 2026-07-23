import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

export default function TripRating({ tripId, destination }) {
  const [rating,    setRating]    = useState(0)
  const [hover,     setHover]     = useState(0)
  const [review,    setReview]    = useState('')
  const [submitted, setSubmitted] = useState(false)  // permanently true after first save
  const [loading,   setLoading]   = useState(false)
  const [dirty,     setDirty]     = useState(false)  // true when user changed rating/review after save

  // Load existing rating on mount
  useEffect(() => {
    if (!tripId) return
    axios.get(`${API_BASE}/api/ratings/${tripId}`)
      .then(res => {
        if (res.data.rating) {
          setRating(res.data.rating)
          setReview(res.data.review || '')
          setSubmitted(true)
        }
      })
      .catch(() => {})
  }, [tripId])

  const handleStarClick = (star) => {
    setRating(star)
    setDirty(true)   // user changed rating — allow re-submit
  }

  const handleReviewChange = (val) => {
    setReview(val)
    setDirty(true)
  }

  const handleSave = async () => {
    if (!rating || !tripId) return
    setLoading(true)
    try {
      await axios.post(`${API_BASE}/api/ratings`, { trip_id: tripId, rating, review })
      setSubmitted(true)
      setDirty(false)
    } catch {
      alert('Could not save rating. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const labels = ['', 'Poor', 'Fair', 'Good', 'Great', 'Excellent!']
  const activeRating = hover || rating
  const canSubmit = rating > 0 && !loading && (!submitted || dirty)

  return (
    <div className="p-6 rounded-3xl"
      style={{ background: 'rgba(6,9,24,0.6)', border: '1px solid rgba(245,158,11,0.12)', backdropFilter: 'blur(20px)' }}>

      <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-black uppercase tracking-widest px-4 py-2 rounded-full mb-4"
        style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
        ⭐ Rate This Trip
      </div>

      <p className="text-white/50 text-sm mb-5">
        {submitted && !dirty
          ? `✅ You rated ${destination} — thanks for the feedback!`
          : `How was your AI-planned trip to ${destination}?`}
      </p>

      {/* Star selector */}
      <div className="flex items-center gap-2 mb-2">
        {[1, 2, 3, 4, 5].map(star => (
          <button
            key={star}
            type="button"
            onClick={() => handleStarClick(star)}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            className="text-4xl transition-all hover:scale-110 active:scale-95"
            style={{
              color: star <= activeRating ? '#f59e0b' : 'rgba(255,255,255,0.15)',
              filter: star <= activeRating ? 'drop-shadow(0 0 8px rgba(245,158,11,0.5))' : 'none',
            }}
          >
            ★
          </button>
        ))}
        {activeRating > 0 && (
          <span className="ml-2 font-outfit font-black text-amber-300 text-sm">{labels[activeRating]}</span>
        )}
      </div>

      {/* Review textarea */}
      <textarea
        value={review}
        onChange={e => handleReviewChange(e.target.value)}
        placeholder="Share your thoughts about the itinerary (optional)…"
        rows={3}
        className="w-full mt-3 px-4 py-3 rounded-2xl text-white/80 text-sm placeholder-white/20 outline-none resize-none"
        style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.09)', fontFamily: 'inherit' }}
      />

      <div className="flex items-center justify-between mt-3">
        {/* Status message */}
        <div>
          {submitted && !dirty && (
            <span className="text-emerald-400 text-sm font-bold flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-emerald-400 flex items-center justify-center text-[11px] text-white font-black flex-shrink-0">✓</span>
              Rating submitted
            </span>
          )}
          {!tripId && (
            <span className="text-white/25 text-xs">Generate a trip first to rate it</span>
          )}
        </div>

        {/* Submit button */}
        <button
          onClick={handleSave}
          disabled={!canSubmit}
          className="px-6 py-2.5 rounded-xl font-black text-sm text-white transition-all hover:-translate-y-0.5 disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            background: canSubmit
              ? 'linear-gradient(135deg,#f59e0b,#ea580c)'
              : submitted && !dirty
                ? 'rgba(52,211,153,0.2)'
                : 'rgba(255,255,255,0.07)',
            boxShadow: canSubmit ? '0 0 16px rgba(245,158,11,0.3)' : 'none',
            color: submitted && !dirty && !canSubmit ? '#34d399' : 'white',
          }}
        >
          {loading
            ? '⏳ Saving…'
            : submitted && !dirty
              ? '✓ Submitted'
              : '⭐ Submit Rating'}
        </button>
      </div>
    </div>
  )
}
