import { useState } from 'react'

const fmt = (n) => `₹${Number(n).toLocaleString('en-IN')}`

const DAY_THEMES = [
  { from: '#f59e0b', to: '#ea580c', accent: '#fbbf24', glow: 'rgba(245,158,11,0.25)' },
  { from: '#8b5cf6', to: '#ec4899', accent: '#c084fc', glow: 'rgba(139,92,246,0.25)' },
  { from: '#06b6d4', to: '#3b82f6', accent: '#67e8f9', glow: 'rgba(6,182,212,0.25)' },
  { from: '#10b981', to: '#06b6d4', accent: '#34d399', glow: 'rgba(16,185,129,0.25)' },
  { from: '#f43f5e', to: '#f97316', accent: '#fb7185', glow: 'rgba(244,63,94,0.25)' },
  { from: '#6366f1', to: '#8b5cf6', accent: '#a5b4fc', glow: 'rgba(99,102,241,0.25)' },
  { from: '#0891b2', to: '#0f766e', accent: '#5eead4', glow: 'rgba(8,145,178,0.25)' },
  { from: '#db2777', to: '#9333ea', accent: '#f9a8d4', glow: 'rgba(219,39,119,0.25)' },
]

const SLOT_CONFIG = [
  { key: 'morning',   label: 'Morning',   emoji: '🌅', color: '#fbbf24', bg: 'rgba(251,191,36,0.07)',  border: 'rgba(251,191,36,0.2)'  },
  { key: 'afternoon', label: 'Afternoon', emoji: '☀️', color: '#fb923c', bg: 'rgba(251,146,60,0.07)',  border: 'rgba(251,146,60,0.2)'  },
  { key: 'evening',   label: 'Evening',   emoji: '🌆', color: '#c084fc', bg: 'rgba(192,132,252,0.07)', border: 'rgba(192,132,252,0.2)' },
]

function getMapsUrl(places) {
  const c = places.filter(p => p.latitude && p.latitude !== 0)
  if (!c.length) return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(places.map(p => p.name).join(' '))}`
  if (c.length === 1) return `https://www.google.com/maps/search/?api=1&query=${c[0].latitude},${c[0].longitude}`
  const origin = `${c[0].latitude},${c[0].longitude}`
  const dest = `${c[c.length - 1].latitude},${c[c.length - 1].longitude}`
  const wp = c.slice(1, -1).map(p => `${p.latitude},${p.longitude}`).join('|')
  return `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${dest}&travelmode=driving${wp ? `&waypoints=${wp}` : ''}`
}

function getPlaceMapUrl(place) {
  if (place.latitude && place.latitude !== 0)
    return `https://www.google.com/maps/search/?api=1&query=${place.latitude},${place.longitude}`
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name)}`
}

export default function DayPlanCard({ day }) {
  const [open, setOpen] = useState(day.day <= 2)
  const theme = DAY_THEMES[(day.day - 1) % DAY_THEMES.length]
  const mapsUrl = getMapsUrl(day.places || [])
  const label = day.date_label?.replace(/^Day \d+\s*[–\-]\s*/, '') || `Explore Day ${day.day}`

  return (
    <div className="rounded-3xl overflow-hidden transition-all duration-500"
      style={{
        background: 'rgba(6,9,24,0.7)',
        border: open ? `1px solid ${theme.accent}35` : '1px solid rgba(255,255,255,0.07)',
        backdropFilter: 'blur(16px)',
        boxShadow: open ? `0 16px 60px ${theme.glow}, 0 4px 20px rgba(0,0,0,0.4)` : '0 4px 20px rgba(0,0,0,0.3)',
      }}>

      {/* ── Header ──────────────────────────────────── */}
      <button className="w-full text-left" onClick={() => setOpen(!open)}>
        <div className="flex items-stretch min-h-[100px] relative overflow-hidden">
          {/* Gradient background */}
          <div className="absolute inset-0" style={{ background: `linear-gradient(135deg, ${theme.from}22, ${theme.to}11)` }} />
          {/* Glow orb */}
          <div className="absolute -right-16 -top-16 w-48 h-48 rounded-full blur-3xl pointer-events-none"
            style={{ background: `radial-gradient(circle, ${theme.accent}40, transparent)` }} />
          <div className="absolute top-0 left-0 right-0 h-0.5"
            style={{ background: `linear-gradient(90deg, ${theme.from}, ${theme.to}, transparent)` }} />

          {/* Day number */}
          <div className="flex flex-col items-center justify-center px-4 sm:px-7 py-6 flex-shrink-0 relative z-10"
            style={{ minWidth: '70px', borderRight: `1px solid ${theme.accent}20` }}>
            <span className="text-[10px] font-black uppercase tracking-[0.2em]" style={{ color: theme.accent + 'aa' }}>DAY</span>
            <span className="font-outfit font-black leading-none" style={{ fontSize: 'clamp(2rem,8vw,3rem)', color: theme.accent }}>
              {day.day}
            </span>
          </div>

          {/* Title */}
          <div className="flex-1 py-4 sm:py-6 px-4 sm:px-6 flex flex-col justify-center relative z-10">
            <h3 className="font-outfit font-black text-white text-lg sm:text-2xl leading-tight">{label}</h3>
            {day.narrative && (
              <p className="text-white/45 text-xs sm:text-sm mt-1.5 line-clamp-1 max-w-lg">{day.narrative}</p>
            )}
            <div className="flex flex-wrap items-center gap-2 mt-3">
              {day.places?.length > 0 && (
                <span className="text-xs font-bold px-3 py-1 rounded-full"
                  style={{ background: `${theme.accent}18`, color: theme.accent, border: `1px solid ${theme.accent}25` }}>
                  📍 {day.places.length} places
                </span>
              )}
              {day.estimated_cost > 0 && (
                <span className="text-xs font-bold px-3 py-1 rounded-full"
                  style={{ background: 'rgba(255,255,255,0.06)', color: 'rgba(255,255,255,0.55)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  💰 {fmt(day.estimated_cost)}
                </span>
              )}
            </div>
          </div>

          {/* Chevron */}
          <div className="flex items-center pr-7 relative z-10">
            <div className="w-10 h-10 rounded-2xl flex items-center justify-center text-white transition-all duration-300"
              style={{
                background: `${theme.accent}18`,
                border: `1px solid ${theme.accent}25`,
                transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
              }}>
              ▾
            </div>
          </div>
        </div>
      </button>

      {/* ── Body ────────────────────────────────────── */}
      {open && (
        <div className="overflow-hidden">
          <div className="p-4 sm:p-7 space-y-5 sm:space-y-7">

            {/* Narrative quote */}
            {day.narrative && (
              <div className="flex gap-4 p-6 rounded-3xl relative overflow-hidden"
                style={{ background: `${theme.from}0d`, border: `1px solid ${theme.accent}20` }}>
                <div className="text-6xl opacity-15 font-black leading-none flex-shrink-0 mt-1" style={{ color: theme.accent }}>"</div>
                <p className="text-white/60 italic leading-relaxed text-base flex-1 pt-2">{day.narrative}</p>
              </div>
            )}

            {/* Places + route */}
            {day.places?.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-outfit font-black text-white text-sm uppercase tracking-widest flex items-center gap-2">
                    <span style={{ color: theme.accent }}>📍</span> Today's Stops
                  </h4>
                  <a href={mapsUrl} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm font-black px-5 py-2.5 rounded-2xl text-white transition-all hover:-translate-y-0.5"
                    style={{ background: `linear-gradient(135deg,${theme.from},${theme.to})`, boxShadow: `0 4px 16px ${theme.glow}` }}>
                    🗺️ Full Route
                  </a>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {day.places.map((p, i) => (
                    <a key={i} href={getPlaceMapUrl(p)} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-3 p-4 rounded-2xl transition-all group hover:-translate-y-0.5"
                      style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${theme.accent}15` }}>
                      <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white text-xs font-black flex-shrink-0"
                        style={{ background: `linear-gradient(135deg,${theme.from},${theme.to})` }}>
                        {i + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-white text-base truncate group-hover:transition-colors"
                          style={{ '--hover-color': theme.accent }}>
                          {p.name}
                        </div>
                        {p.rating > 0 && <div className="text-xs text-white/35 mt-0.5">⭐ {p.rating?.toFixed(1)}</div>}
                      </div>
                      {p.price_level === 0 && (
                        <span className="text-xs font-bold px-2 py-0.5 rounded-full flex-shrink-0"
                          style={{ background: 'rgba(52,211,153,0.15)', color: '#34d399' }}>Free</span>
                      )}
                      <span className="text-white/30 group-hover:text-white/70 transition-colors">↗</span>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Time slots */}
            <div className="space-y-4">
              {SLOT_CONFIG.map(slot => {
                const content = day[slot.key]
                if (!content) return null
                return (
                  <div key={slot.key} className="rounded-2xl overflow-hidden"
                    style={{ background: slot.bg, border: `1px solid ${slot.border}` }}>
                    <div className="flex items-center gap-3 px-6 py-4"
                      style={{ borderBottom: `1px solid ${slot.border}` }}>
                      <span className="text-2xl">{slot.emoji}</span>
                      <span className="font-outfit font-black text-lg" style={{ color: slot.color }}>{slot.label}</span>
                    </div>
                    <div className="px-6 py-5">
                      <p className="text-white/65 text-base leading-relaxed">{content}</p>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Full route CTA */}
            <a href={mapsUrl} target="_blank" rel="noopener noreferrer"
              className="flex items-center justify-center gap-3 w-full py-5 rounded-2xl font-outfit font-black text-white text-lg transition-all hover:-translate-y-1"
              style={{ background: `linear-gradient(135deg,${theme.from},${theme.to})`, boxShadow: `0 8px 32px ${theme.glow}` }}>
              📍 View Full Day Route on Google Maps
            </a>

            {/* Footer */}
            <div className="flex items-center justify-between pt-4"
              style={{ borderTop: `1px solid ${theme.accent}12` }}>
              <div className="flex items-center gap-2">
                <span className="text-amber-400">💰</span>
                <span className="text-white/40 text-sm">Estimated spend:</span>
                <span className="font-outfit font-black text-white">{fmt(day.estimated_cost)}</span>
              </div>
              <span className="text-white/20 text-xs">Day {day.day} of your journey</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
