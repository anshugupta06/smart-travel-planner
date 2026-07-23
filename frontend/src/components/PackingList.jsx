import { useState, useEffect } from 'react'
import { API_BASE } from '../config'

const CATEGORY_ICONS = {
  'Clothing':      '👕',
  'Toiletries':    '🪥',
  'Documents':     '📄',
  'Electronics':   '🔌',
  'Health':        '💊',
  'Activities':    '🎒',
  'Essentials':    '⭐',
}

function parsePackingList(text) {
  // Parse LLM response into categorised sections
  const categories = {}
  let currentCat = 'Essentials'

  for (const line of text.split('\n')) {
    const trimmed = line.trim()
    if (!trimmed) continue

    // Detect category headings like "**Clothing:**" or "## Documents"
    const headingMatch = trimmed.match(/^[#*_]{0,3}\s*([A-Z][a-zA-Z &]+)[:#*_]{0,3}$/)
    if (headingMatch && trimmed.length < 40) {
      currentCat = headingMatch[1].trim()
      continue
    }

    // Detect bullet items
    const itemMatch = trimmed.match(/^[-•*✓]\s+(.+)/)
    if (itemMatch) {
      const item = itemMatch[1].replace(/\*\*/g, '').trim()
      if (item.length > 1) {
        if (!categories[currentCat]) categories[currentCat] = []
        categories[currentCat].push(item)
      }
    }
  }

  // Fallback: split by newline if no bullets found
  if (Object.keys(categories).length === 0) {
    const items = text.split('\n').filter(l => l.trim().length > 2).map(l => l.replace(/^[-•*]\s*/, '').trim())
    categories['Essentials'] = items
  }

  return categories
}

export default function PackingList({ tripData, onClose }) {
  const [categories, setCategories] = useState(null)
  const [loading, setLoading]       = useState(true)
  const [checked, setChecked]       = useState({})
  const [error, setError]           = useState('')

  const { destination, days, travel_type, weather } = tripData || {}

  useEffect(() => {
    const generate = async () => {
      setLoading(true)
      try {
        const weatherHint = weather ? `Weather: ${weather.temperature}°C, ${weather.description}` : ''
        const prompt = `Generate a smart packing list for a ${days}-day ${travel_type} trip to ${destination}. ${weatherHint}

Format the response as categorised bullet points with these sections:
- Clothing
- Toiletries
- Documents
- Electronics
- Health & Medicine
- Activities & Gear
- Essentials

Keep each item short (2-5 words). Include 4-7 items per category. Be specific to the destination and weather.`

        const res = await fetch(`${API_BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: prompt,
            destination,
            days,
            travel_type,
          }),
        })
        const data = await res.json()
        setCategories(parsePackingList(data.reply))
      } catch {
        setError('Could not generate packing list. Please try again.')
      } finally {
        setLoading(false)
      }
    }
    generate()
  }, [])

  const toggle = (cat, item) => {
    const key = `${cat}::${item}`
    setChecked(p => ({ ...p, [key]: !p[key] }))
  }

  const total    = Object.values(categories || {}).flat().length
  const done     = Object.values(checked).filter(Boolean).length
  const progress = total > 0 ? Math.round((done / total) * 100) : 0

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-12 overflow-y-auto"
      onClick={onClose}>
      <div className="absolute inset-0" style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)' }} />

      <div
        className="relative w-full max-w-2xl rounded-3xl overflow-hidden mb-8"
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
            <div className="text-amber-400 text-xs font-black uppercase tracking-widest mb-1">🎒 Packing List</div>
            <h2 className="font-outfit font-black text-white text-2xl">What to Pack</h2>
            <p className="text-white/35 text-sm mt-0.5">{destination} · {days} days · {travel_type}</p>
          </div>
          <button onClick={onClose}
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white/50 hover:text-white"
            style={{ background: 'rgba(255,255,255,0.07)' }}>✕</button>
        </div>

        {/* Progress bar */}
        {!loading && !error && categories && (
          <div className="px-6 py-4" style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <div className="flex justify-between text-xs text-white/40 mb-1.5 font-medium">
              <span>Packing progress</span>
              <span>{done}/{total} items · {progress}%</span>
            </div>
            <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.07)' }}>
              <div className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${progress}%`,
                  background: progress === 100
                    ? 'linear-gradient(90deg,#34d399,#10b981)'
                    : 'linear-gradient(90deg,#f59e0b,#ea580c)',
                }} />
            </div>
            {progress === 100 && (
              <p className="text-emerald-400 text-xs font-bold mt-2 text-center">✅ All packed! Have a great trip! ✈️</p>
            )}
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 gap-4">
              <span className="w-8 h-8 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
              <p className="text-white/40 text-sm">AI is generating your packing list…</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-400/80">{error}</p>
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(categories).map(([cat, items]) => (
                <div key={cat}>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">{CATEGORY_ICONS[cat] || '📦'}</span>
                    <h3 className="font-outfit font-black text-white text-base">{cat}</h3>
                    <span className="text-white/25 text-xs ml-auto">
                      {items.filter(i => checked[`${cat}::${i}`]).length}/{items.length}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {items.map(item => {
                      const key = `${cat}::${item}`
                      const done = checked[key]
                      return (
                        <button
                          key={item}
                          onClick={() => toggle(cat, item)}
                          className="flex items-center gap-3 p-3 rounded-xl text-left transition-all hover:-translate-y-0.5"
                          style={{
                            background: done ? 'rgba(52,211,153,0.08)' : 'rgba(255,255,255,0.04)',
                            border: done ? '1px solid rgba(52,211,153,0.25)' : '1px solid rgba(255,255,255,0.07)',
                          }}
                        >
                          <div className="w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 transition-all"
                            style={{
                              background: done ? '#34d399' : 'rgba(255,255,255,0.1)',
                              border: done ? 'none' : '1px solid rgba(255,255,255,0.2)',
                            }}>
                            {done && <span className="text-white text-xs font-black">✓</span>}
                          </div>
                          <span className={`text-sm font-medium transition-all ${done ? 'line-through text-white/30' : 'text-white/70'}`}>
                            {item}
                          </span>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {!loading && !error && (
          <div className="px-6 pb-5">
            <button
              onClick={() => setChecked({})}
              className="w-full py-3 rounded-xl text-sm font-semibold text-white/40 hover:text-white/70 transition-colors"
              style={{ border: '1px solid rgba(255,255,255,0.08)' }}
            >
              Reset All
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
