import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'
const fmt  = (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`

const STYLE_CONFIG = {
  budget:   { emoji: '🎒', label: 'Budget',   color: '#34d399', bg: 'rgba(52,211,153,0.12)'  },
  moderate: { emoji: '🌟', label: 'Moderate', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)' },
  luxury:   { emoji: '💎', label: 'Luxury',   color: '#a78bfa', bg: 'rgba(167,139,250,0.12)' },
}

function StatCard({ icon, value, label, color = '#f59e0b', sub }) {
  return (
    <div className="p-5 rounded-2xl flex items-center gap-4"
      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
      <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0"
        style={{ background: color + '18', border: `1px solid ${color}30` }}>
        {icon}
      </div>
      <div>
        <div className="font-outfit font-black text-2xl text-white leading-none">{value}</div>
        <div className="text-white/40 text-xs font-medium mt-0.5">{label}</div>
        {sub && <div className="text-xs mt-0.5" style={{ color }}>{sub}</div>}
      </div>
    </div>
  )
}

function BarChart({ items, colorFn }) {
  if (!items?.length) return <p className="text-white/30 text-sm text-center py-6">No data yet</p>
  const max = Math.max(...items.map(i => i.count))
  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="text-white/60 text-sm font-medium w-28 truncate flex-shrink-0">{item.name}</div>
          <div className="flex-1 h-6 rounded-full overflow-hidden"
            style={{ background: 'rgba(255,255,255,0.05)' }}>
            <div
              className="h-full rounded-full flex items-center px-3 transition-all duration-700"
              style={{
                width: `${Math.max(8, (item.count / max) * 100)}%`,
                background: colorFn ? colorFn(i) : 'linear-gradient(90deg,#f59e0b,#ea580c)',
              }}
            >
              <span className="text-white text-[10px] font-black">{item.count}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function Dashboard({ onClose }) {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get(`${API_BASE}/api/analytics`)
      .then(res => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [])

  const styleTotal = data
    ? Object.values(data.travel_styles || {}).reduce((a, b) => a + b, 0)
    : 0

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
            <div className="text-amber-400 text-xs font-black uppercase tracking-widest mb-1">📊 Analytics</div>
            <h2 className="font-outfit font-black text-white text-2xl">Trip Dashboard</h2>
            <p className="text-white/35 text-sm mt-0.5">Insights from all planned trips</p>
          </div>
          <button onClick={onClose}
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white/50 hover:text-white"
            style={{ background: 'rgba(255,255,255,0.07)' }}>✕</button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center gap-3 py-16">
              <span className="w-7 h-7 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-white/40">Loading analytics…</span>
            </div>
          ) : !data || data.total_trips === 0 ? (
            <div className="text-center py-16">
              <div className="text-5xl mb-4">📊</div>
              <p className="text-white/40 font-medium">No trips planned yet.</p>
              <p className="text-white/25 text-sm mt-1">Plan your first trip to see analytics here.</p>
            </div>
          ) : (
            <div className="space-y-6">

              {/* Stat cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <StatCard icon="✈️" value={data.total_trips} label="Trips Planned"  color="#f59e0b" />
                <StatCard icon="📅" value={`${data.avg_days}d`} label="Avg Duration" color="#34d399" />
                <StatCard icon="💰" value={fmt(data.avg_budget)} label="Avg Budget"  color="#a78bfa" />
                <StatCard icon="🗺️" value={data.destinations?.length || 0} label="Destinations" color="#38bdf8" />
              </div>

              {/* Top destinations + origins */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="p-5 rounded-2xl"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                  <p className="text-amber-400 text-xs font-black uppercase tracking-widest mb-4">🏆 Top Destinations</p>
                  <BarChart
                    items={data.destinations}
                    colorFn={(i) => `hsl(${38 + i * 18}, 95%, ${60 - i * 3}%)`}
                  />
                </div>
                <div className="p-5 rounded-2xl"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                  <p className="text-amber-400 text-xs font-black uppercase tracking-widest mb-4">🏠 Top Origins</p>
                  <BarChart
                    items={data.top_origins}
                    colorFn={(i) => `hsl(${200 + i * 20}, 85%, ${55 - i * 3}%)`}
                  />
                </div>
              </div>

              {/* Travel style breakdown */}
              <div className="p-5 rounded-2xl"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                <p className="text-amber-400 text-xs font-black uppercase tracking-widest mb-4">🎭 Travel Styles</p>
                <div className="grid grid-cols-3 gap-3">
                  {['budget', 'moderate', 'luxury'].map(style => {
                    const count  = data.travel_styles?.[style] || 0
                    const pct    = styleTotal > 0 ? Math.round((count / styleTotal) * 100) : 0
                    const cfg    = STYLE_CONFIG[style]
                    return (
                      <div key={style} className="p-4 rounded-2xl text-center"
                        style={{ background: cfg.bg, border: `1px solid ${cfg.color}25` }}>
                        <div className="text-2xl mb-1">{cfg.emoji}</div>
                        <div className="font-outfit font-black text-2xl" style={{ color: cfg.color }}>{count}</div>
                        <div className="text-white/40 text-xs mt-0.5">{cfg.label}</div>
                        <div className="text-xs font-bold mt-1" style={{ color: cfg.color + 'aa' }}>{pct}%</div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Total budget planned */}
              <div className="p-4 rounded-2xl flex items-center justify-between"
                style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)' }}>
                <span className="text-white/50 text-sm font-medium">💰 Total budget across all trips</span>
                <span className="font-outfit font-black text-amber-300 text-xl">{fmt(data.total_budget)}</span>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
