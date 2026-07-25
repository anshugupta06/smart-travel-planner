import { useState } from 'react'

const TYPE_LABELS = {
  tourist_attraction: 'Attraction', historical: 'Heritage', beach: 'Beach',
  park: 'Park', place_of_worship: 'Temple/Church', museum: 'Museum',
  natural_feature: 'Nature', shopping_mall: 'Shopping', viewpoint: 'Viewpoint',
}

const RANK_COLORS = [
  { from: '#f59e0b', to: '#ea580c' },
  { from: '#94a3b8', to: '#64748b' },
  { from: '#b45309', to: '#92400e' },
  { from: '#6366f1', to: '#8b5cf6' },
  { from: '#0891b2', to: '#0e7490' },
  { from: '#10b981', to: '#059669' },
  { from: '#f43f5e', to: '#e11d48' },
  { from: '#8b5cf6', to: '#7c3aed' },
]

const BEST_TIME_STYLES = {
  Morning:   { bg: 'rgba(251,191,36,0.15)',  text: '#fbbf24', border: 'rgba(251,191,36,0.25)'  },
  Afternoon: { bg: 'rgba(251,146,60,0.15)',  text: '#fb923c', border: 'rgba(251,146,60,0.25)'  },
  Evening:   { bg: 'rgba(167,139,250,0.15)', text: '#a78bfa', border: 'rgba(167,139,250,0.25)' },
  Sunrise:   { bg: 'rgba(251,113,133,0.15)', text: '#fb7185', border: 'rgba(251,113,133,0.25)' },
  Sunset:    { bg: 'rgba(244,114,182,0.15)', text: '#f472b6', border: 'rgba(244,114,182,0.25)' },
}

function getMapUrl(place) {
  if (place.latitude && place.latitude !== 0)
    return `https://www.google.com/maps/search/?api=1&query=${place.latitude},${place.longitude}`
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name)}`
}

function StarRating({ rating }) {
  if (!rating) return null
  const full = Math.floor(rating)
  const half = rating % 1 >= 0.5
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-0.5">
        {Array.from({ length: 5 }, (_, i) => (
          <span key={i} style={{ color: i < full ? '#fbbf24' : (i === full && half ? '#fbbf24' : 'rgba(255,255,255,0.15)'), fontSize: '14px' }}>★</span>
        ))}
      </div>
      <span className="text-white/60 text-xs font-bold">{rating.toFixed(1)}</span>
    </div>
  )
}

export default function TopPlacesCard({ places, destination }) {
  const [activePlace, setActivePlace] = useState(0)
  const [showRestaurants, setShowRestaurants] = useState(false)
  const selected = places[activePlace]

  // Map URL centered on selected place or destination
  const mapQuery = selected?.latitude && selected.latitude !== 0
    ? `${selected.latitude},${selected.longitude}`
    : encodeURIComponent(`${selected?.name}, ${destination}`)
  const mapEmbedUrl = `https://maps.google.com/maps?q=${mapQuery}&t=&z=14&ie=UTF8&iwloc=&output=embed`

  // Restaurant map embed
  const restaurantQuery = encodeURIComponent(`best restaurants in ${destination}`)
  const restaurantMapUrl = `https://maps.google.com/maps?q=${restaurantQuery}&t=&z=14&ie=UTF8&iwloc=&output=embed`

  // Full map for all places
  const allMapUrl = `https://www.google.com/maps/search/${encodeURIComponent(destination + ' tourist attractions')}`
  const allRestaurantsUrl = `https://www.google.com/maps/search/${encodeURIComponent('restaurants in ' + destination)}`

  return (
    <div>
      {/* Section header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6 sm:mb-8">
        <div>
          <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-3"
            style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
            📍 AI Ranked
          </div>
          <h2 className="font-outfit font-black text-white text-3xl md:text-5xl">
            Must-Visit Places in <span className="text-gold-gradient">{destination}</span>
          </h2>
          <p className="text-white/35 mt-2 text-sm">Click a place to locate it on the map · Ranked by AI</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Restaurant toggle */}
          <button
            onClick={() => setShowRestaurants(r => !r)}
            className="flex items-center gap-2 text-xs sm:text-sm font-bold px-3 sm:px-4 py-2 sm:py-2.5 rounded-xl text-white transition-all hover:-translate-y-0.5"
            style={{
              background: showRestaurants ? 'rgba(251,146,60,0.2)' : 'rgba(255,255,255,0.07)',
              border: showRestaurants ? '1px solid rgba(251,146,60,0.4)' : '1px solid rgba(255,255,255,0.1)',
            }}>
            🍽️ <span className="hidden sm:inline">{showRestaurants ? 'Hide' : 'Nearby'} </span>Food
          </button>
          <a href={showRestaurants ? allRestaurantsUrl : allMapUrl} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 text-xs sm:text-sm font-bold px-3 sm:px-5 py-2 sm:py-2.5 rounded-xl text-white transition-all hover:-translate-y-0.5"
            style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' }}>
            🗺️ <span className="hidden sm:inline">Open All in </span>Maps
          </a>
        </div>
      </div>

      {/* ── MAIN TWO-COLUMN LAYOUT ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* LEFT — Places list */}
        <div className="flex flex-col gap-3 overflow-y-auto" style={{ maxHeight: '680px' }}>
          {places.slice(0, 9).map((place, i) => {
            const typeKey = (place.types || []).find(t => TYPE_LABELS[t]) || (place.types || [])[0]
            const typeLabel = TYPE_LABELS[typeKey] || typeKey || 'Attraction'
            const bestTimeStyle = BEST_TIME_STYLES[place.best_time]
            const rankColor = RANK_COLORS[i % RANK_COLORS.length]
            const isActive = activePlace === i

            return (
              <button key={i} onClick={() => setActivePlace(i)}
                className="text-left w-full rounded-2xl transition-all duration-300 hover:-translate-y-0.5 group"
                style={{
                  background: isActive ? 'rgba(245,158,11,0.08)' : 'rgba(255,255,255,0.03)',
                  border: isActive ? '1px solid rgba(245,158,11,0.35)' : '1px solid rgba(255,255,255,0.07)',
                  boxShadow: isActive ? '0 4px 24px rgba(245,158,11,0.12)' : 'none',
                }}>
                <div className="flex items-start gap-4 p-4">
                  {/* Rank badge */}
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center text-white font-black text-sm flex-shrink-0"
                    style={{ background: `linear-gradient(135deg,${rankColor.from},${rankColor.to})` }}>
                    {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i + 1}`}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-outfit font-black text-white text-base leading-tight group-hover:text-amber-300 transition-colors">
                        {place.name}
                      </h3>
                      {place.price_level === 0 && (
                        <span className="text-[10px] font-black px-2 py-0.5 rounded-full flex-shrink-0"
                          style={{ background: 'rgba(52,211,153,0.2)', color: '#34d399' }}>FREE</span>
                      )}
                    </div>
                    <StarRating rating={place.rating} />
                    {place.description && (
                      <p className="text-white/40 text-xs leading-relaxed mt-1 line-clamp-2">{place.description}</p>
                    )}
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {typeLabel && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold"
                          style={{ background: 'rgba(34,211,238,0.12)', color: '#22d3ee', border: '1px solid rgba(34,211,238,0.2)' }}>
                          {typeLabel}
                        </span>
                      )}
                      {place.best_time && bestTimeStyle && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold"
                          style={{ background: bestTimeStyle.bg, color: bestTimeStyle.text, border: `1px solid ${bestTimeStyle.border}` }}>
                          ⏰ {place.best_time}
                        </span>
                      )}
                    </div>
                    {place.address && (
                      <p className="text-white/25 text-[10px] mt-1.5 truncate">{place.address}</p>
                    )}
                  </div>

                  {/* Map pin indicator */}
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 transition-all ${isActive ? 'opacity-100' : 'opacity-30 group-hover:opacity-60'}`}
                    style={{ background: isActive ? 'rgba(245,158,11,0.2)' : 'rgba(255,255,255,0.05)' }}>
                    <span className="text-sm">{isActive ? '📍' : '↗'}</span>
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {/* RIGHT — Sticky map + selected place detail */}
        <div className="flex flex-col gap-4 lg:sticky lg:top-24" style={{ height: 'fit-content' }}>
          {/* Selected place highlight */}
          {selected && (
            <div className="rounded-2xl p-5 flex items-center gap-4"
              style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)' }}>
              <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-black flex-shrink-0"
                style={{ background: `linear-gradient(135deg,${RANK_COLORS[activePlace % RANK_COLORS.length].from},${RANK_COLORS[activePlace % RANK_COLORS.length].to})` }}>
                #{activePlace + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-outfit font-black text-white text-lg leading-tight">{selected.name}</div>
                <StarRating rating={selected.rating} />
              </div>
              <a href={getMapUrl(selected)} target="_blank" rel="noopener noreferrer"
                className="text-xs font-black px-4 py-2 rounded-xl text-white flex-shrink-0 transition-all hover:-translate-y-0.5"
                style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
                Open in Maps ↗
              </a>
            </div>
          )}

          {/* Map embed */}
          <div className="rounded-3xl overflow-hidden relative"
            style={{ height: 'clamp(280px, 40vw, 500px)', border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 8px 40px rgba(0,0,0,0.5)' }}>
            <iframe
              key={showRestaurants ? 'restaurants' : activePlace}
              title={showRestaurants ? 'Restaurants Map' : 'Place Map'}
              width="100%"
              height="100%"
              style={{ border: 0 }}
              loading="lazy"
              allowFullScreen
              src={showRestaurants ? restaurantMapUrl : mapEmbedUrl}
            />
            {/* Map overlay label */}
            <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between"
              style={{ pointerEvents: 'none' }}>
              <div className="px-4 py-2 rounded-xl text-xs text-white font-semibold flex items-center gap-2"
                style={{ background: 'rgba(6,9,24,0.88)', backdropFilter: 'blur(12px)', border: '1px solid rgba(255,255,255,0.1)' }}>
                <span className="w-2 h-2 rounded-full animate-pulse"
                  style={{ background: showRestaurants ? '#fb923c' : '#f59e0b' }} />
                {showRestaurants ? `Restaurants in ${destination}` : (selected?.name || destination)}
              </div>
              {showRestaurants && (
                <a href={allRestaurantsUrl} target="_blank" rel="noopener noreferrer"
                  className="px-3 py-2 rounded-xl text-xs text-white font-bold"
                  style={{ background: 'rgba(251,146,60,0.85)', pointerEvents: 'all' }}>
                  Open in Maps ↗
                </a>
              )}
            </div>
          </div>

          {/* Navigation hint */}
          <p className="text-center text-white/25 text-xs">
            {showRestaurants
              ? '🍽️ Showing restaurants near ' + destination
              : '← Select a place from the list to locate it on the map'}
          </p>
        </div>
      </div>
    </div>
  )
}
