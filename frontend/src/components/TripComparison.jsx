import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
const fmt = (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`

const TIER_CONFIG = {
  budget:   { emoji: '🎒', label: 'Budget',   color: '#34d399', bg: 'rgba(52,211,153,0.07)',  border: 'rgba(52,211,153,0.25)'  },
  moderate: { emoji: '🌟', label: 'Moderate', color: '#f59e0b', bg: 'rgba(245,158,11,0.07)', border: 'rgba(245,158,11,0.3)'  },
  luxury:   { emoji: '💎', label: 'Luxury',   color: '#a78bfa', bg: 'rgba(167,139,250,0.07)', border: 'rgba(167,139,250,0.3)' },
}

const LINE_ITEMS = [
  { key: 'accommodation', label: 'Stay',       emoji: '🏨' },
  { key: 'food',          label: 'Food',        emoji: '🍽️' },
  { key: 'transport',     label: 'Transport',   emoji: '✈️' },
  { key: 'activities',    label: 'Activities',  emoji: '🎟️' },
  { key: 'misc',          label: 'Misc',        emoji: '🛍️' },
]

export default function TripComparison({ tripData, onClose, onSelectTier }) {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState('')

  const { destination, origin, days, num_people, budget_provided, preferred_transport } = tripData || {}

  useEffect(() => {
    const fetch = async () => {
      setLoading(true)
      try {
        const res = await axios.post(`${API_BASE}/api/compare-budgets`, {
          origin,
          destination,
          days,
          num_people,
          budget: budget_provided,
          travel_type: 'moderate',
          preferences: [],
          preferred_transport: preferred_transport || null,
        })
        setData(res.data)
      } catch {
        setError('Could not load comparison. Please try again.')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-12 overflow-y-auto"
      onClick={onClose}>
      <div className="absolute inset-0" style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)' }} />

      <div
        className="relative w-full max-w-3xl rounded-3xl overflow-hidden mb-8"
        style={{
          background: 'rgba(6,9,24,0.96)',
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
            <div className="text-amber-400 text-xs font-black uppercase tracking-widest mb-1">⚖️ Compare</div>
            <h2 className="font-outfit font-black text-white text-2xl">Budget Comparison</h2>
            <p className="text-white/35 text-sm mt-0.5">{origin} → {destination} · {days} days · {num_people} traveller{num_people > 1 ? 's' : ''}</p>
          </div>
          <button onClick={onClose}
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white/50 hover:text-white"
            style={{ background: 'rgba(255,255,255,0.07)' }}>✕</button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center gap-3 py-16">
              <span className="w-7 h-7 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-white/40">Calculating all tiers…</span>
            </div>
          ) : error ? (
            <p className="text-center text-red-400/80 py-12">{error}</p>
          ) : (
            <>
              {/* Your budget banner */}
              <div className="flex items-center justify-between px-4 py-3 rounded-2xl mb-6"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <span className="text-white/50 text-sm font-medium">Your Budget</span>
                <span className="font-outfit font-black text-white text-lg">{fmt(data.your_budget)}</span>
              </div>

              {/* Tier columns */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                {['budget', 'moderate', 'luxury'].map(tier => {
                  const t = data.tiers[tier]
                  const cfg = TIER_CONFIG[tier]
                  const fits = t.fits_budget
                  const isCurrentTier = tripData?.travel_type === tier

                  return (
                    <div key={tier}
                      className="rounded-2xl p-4 flex flex-col"
                      style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}>
                      {/* Tier header */}
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xl">{cfg.emoji}</span>
                        <div>
                          <div className="font-outfit font-black text-white text-sm">{cfg.label}</div>
                          {isCurrentTier && (
                            <div className="text-[9px] font-black px-1.5 py-0.5 rounded-full text-white mt-0.5"
                              style={{ background: cfg.color + '40', color: cfg.color }}>
                              Current
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Total */}
                      <div className="font-outfit font-black text-2xl mb-1" style={{ color: cfg.color }}>
                        {fmt(t.total_estimated)}
                      </div>
                      <div className="text-white/35 text-xs mb-3">
                        {fmt(t.per_person)}/person
                      </div>

                      {/* Fits badge */}
                      <div className={`text-[10px] font-black px-2 py-1 rounded-full text-center mb-4 ${fits ? 'text-emerald-400' : 'text-red-400'}`}
                        style={{ background: fits ? 'rgba(52,211,153,0.12)' : 'rgba(239,68,68,0.12)' }}>
                        {fits ? '✅ Fits budget' : '❌ Over budget'}
                      </div>

                      {/* Line items */}
                      <div className="space-y-1.5 flex-1">
                        {LINE_ITEMS.map(item => (
                          <div key={item.key} className="flex justify-between items-center">
                            <span className="text-white/40 text-[11px]">{item.emoji} {item.label}</span>
                            <span className="text-white/70 text-[11px] font-bold">{fmt(t[item.key])}</span>
                          </div>
                        ))}
                      </div>

                      {/* Select button */}
                      {onSelectTier && (
                        <button
                          onClick={() => { onSelectTier(tier); onClose() }}
                          className="mt-4 w-full py-2 rounded-xl text-xs font-black transition-all hover:scale-105"
                          style={{
                            background: isCurrentTier
                              ? 'rgba(255,255,255,0.05)'
                              : `linear-gradient(135deg,${cfg.color},${cfg.color}99)`,
                            color: isCurrentTier ? cfg.color : '#fff',
                            border: isCurrentTier ? `1px solid ${cfg.border}` : 'none',
                          }}
                        >
                          {isCurrentTier ? 'Current Plan' : `Plan ${cfg.label} →`}
                        </button>
                      )}
                    </div>
                  )
                })}
              </div>

              {/* Tips from cheapest fitting tier */}
              {(() => {
                const fittingTier = ['budget', 'moderate', 'luxury'].find(t => data.tiers[t].fits_budget)
                const tips = fittingTier ? data.tiers[fittingTier].budget_tips : []
                if (!tips.length) return null
                return (
                  <div className="p-4 rounded-2xl"
                    style={{ background: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.12)' }}>
                    <p className="text-amber-400 text-xs font-black uppercase tracking-widest mb-2">💡 Money-Saving Tips</p>
                    <div className="space-y-1">
                      {tips.map((tip, i) => (
                        <div key={i} className="flex items-start gap-2">
                          <span className="text-amber-400 text-xs mt-0.5 flex-shrink-0">▸</span>
                          <span className="text-white/50 text-xs">{tip}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })()}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
