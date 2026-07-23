import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
const fmt = (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`

const TRAVEL_EMOJI = { budget: '🎒', moderate: '🌟', luxury: '💎' }

function HistoryCard({ trip, onReload, onView }) {
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async (e) => {
    e.stopPropagation()
    if (!confirm('Delete this trip?')) return
    setDeleting(true)
    try {
      await axios.delete(`${API_BASE}/api/history/${trip.id}`)
      onReload()
    } catch {
      setDeleting(false)
    }
  }

  const date = trip.created_at
    ? new Date(trip.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    : ''

  return (
    <div
      onClick={() => onView(trip.id)}
      className="group relative p-5 rounded-2xl cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-lg"
      style={{
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.08)',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Route */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-white/50 text-sm font-medium truncate max-w-[100px]">{trip.origin}</span>
        <span className="text-amber-400 font-black text-sm flex-shrink-0">→</span>
        <span className="text-white font-black text-sm truncate">{trip.destination}</span>
      </div>

      {/* Chips */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {[
          `📅 ${trip.days}d`,
          `👥 ${trip.num_people}`,
          `${TRAVEL_EMOJI[trip.travel_type] || '🌟'} ${trip.travel_type}`,
          fmt(trip.budget),
        ].map((chip, i) => (
          <span key={i} className="text-[10px] font-bold px-2 py-0.5 rounded-full text-white/60"
            style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' }}>
            {chip}
          </span>
        ))}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <span className="text-white/30 text-xs">{date}</span>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => { e.stopPropagation(); onView(trip.id) }}
            className="text-[10px] font-black px-3 py-1 rounded-full text-amber-300 opacity-0 group-hover:opacity-100 transition-all"
            style={{ background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.25)' }}
          >
            View →
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="text-[10px] font-black px-2 py-1 rounded-full text-red-400/70 opacity-0 group-hover:opacity-100 transition-all hover:text-red-400"
            style={{ background: 'rgba(239,68,68,0.08)' }}
          >
            {deleting ? '…' : '✕'}
          </button>
        </div>
      </div>

      {/* Hover accent */}
      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
        style={{ border: '1px solid rgba(245,158,11,0.3)' }} />
    </div>
  )
}

export default function TripHistory({ onViewTrip, onClose }) {
  const [trips, setTrips]     = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingId, setLoadingId] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await axios.get(`${API_BASE}/api/history?limit=20`)
      setTrips(res.data.trips || [])
    } catch {
      setTrips([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleView = async (id) => {
    setLoadingId(id)
    try {
      const res = await axios.get(`${API_BASE}/api/history/${id}`)
      if (res.data.response) {
        onViewTrip(res.data.response)
      }
    } catch {
      alert('Could not load this trip.')
    } finally {
      setLoadingId(null)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-16 overflow-y-auto"
      onClick={onClose}>
      {/* Backdrop */}
      <div className="absolute inset-0" style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)' }} />

      <div
        className="relative w-full max-w-2xl rounded-3xl overflow-hidden"
        style={{
          background: 'rgba(6,9,24,0.95)',
          border: '1px solid rgba(245,158,11,0.2)',
          backdropFilter: 'blur(24px)',
          boxShadow: '0 0 80px rgba(0,0,0,0.6)',
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-5 flex items-center justify-between"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.07)' }}>
          <div>
            <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-black uppercase tracking-widest mb-1">
              📋 My Trips
            </div>
            <h2 className="font-outfit font-black text-white text-2xl">Trip History</h2>
          </div>
          <button onClick={onClose}
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white/50 hover:text-white transition-colors"
            style={{ background: 'rgba(255,255,255,0.07)' }}>
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center gap-3 py-16">
              <span className="w-6 h-6 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-white/40">Loading trips…</span>
            </div>
          ) : trips.length === 0 ? (
            <div className="text-center py-16">
              <div className="text-5xl mb-4">✈️</div>
              <p className="text-white/40 font-medium">No trips planned yet.</p>
              <p className="text-white/25 text-sm mt-1">Your generated itineraries will appear here.</p>
            </div>
          ) : (
            <>
              <p className="text-white/30 text-sm mb-4">{trips.length} trip{trips.length !== 1 ? 's' : ''} found · Click any trip to reload its itinerary</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {trips.map(trip => (
                  <div key={trip.id} className="relative">
                    {loadingId === trip.id && (
                      <div className="absolute inset-0 z-10 flex items-center justify-center rounded-2xl"
                        style={{ background: 'rgba(6,9,24,0.7)' }}>
                        <span className="w-5 h-5 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
                      </div>
                    )}
                    <HistoryCard trip={trip} onReload={load} onView={handleView} />
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
