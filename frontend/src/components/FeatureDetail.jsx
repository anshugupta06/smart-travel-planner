import { useEffect, useState } from 'react'

const FEATURE_DETAILS = {
  'Gemini AI Powered': {
    gradient: 'from-violet-600 via-purple-700 to-indigo-800',
    bg: 'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=1600&q=80',
    accentColor: '#a78bfa',
    glowColor: 'rgba(139,92,246,0.4)',
    tagline: 'Next-gen AI that thinks like a travel expert',
    overview: 'Powered by Google Gemini — one of the most advanced large language models in the world — Smart Travel Planner generates deeply personalized, context-aware travel narratives. Not templates. Not generic text. Real storytelling.',
    points: [
      { icon: '✍️', title: 'Rich Day Narratives', desc: 'Each day of your itinerary reads like it was written by a local travel writer — describing the mood, the best time to visit, what to order for lunch, and insider tips.' },
      { icon: '🧠', title: 'Context-Aware Planning', desc: 'Gemini understands your group size, travel style, budget and interests together — and optimizes for all of them simultaneously, not one at a time.' },
      { icon: '🌐', title: 'Multilingual Ready', desc: 'Get your itinerary with local phrases, cultural notes and etiquette tips tailored to the destination\'s language and customs.' },
      { icon: '🔄', title: 'Dynamic Regeneration', desc: 'Not happy with a day? The AI can rethink and rewrite individual days while keeping the rest of your trip intact.' },
    ],
    stat1: { value: '1M+', label: 'Token Context Window' },
    stat2: { value: '< 20s', label: 'AI Generation Time' },
    stat3: { value: '30+', label: 'Supported Languages' },
  },
  'Smart Route Planning': {
    gradient: 'from-blue-600 via-cyan-700 to-teal-800',
    bg: 'https://images.unsplash.com/photo-1524661135-423995f22d0b?w=1600&q=80',
    accentColor: '#22d3ee',
    glowColor: 'rgba(6,182,212,0.4)',
    tagline: 'ML-optimized routes that save hours every day',
    overview: 'Our route planner uses a Machine Learning implementation of the nearest-neighbor algorithm to cluster attractions geographically. Your days are built so you never backtrack, wasting time in transit when you could be exploring.',
    points: [
      { icon: '📍', title: 'Cluster-Based Grouping', desc: 'Attractions are grouped by proximity — so your morning, afternoon and evening stops flow naturally from one neighborhood to the next.' },
      { icon: '🗺️', title: 'Google Maps Integration', desc: 'Every place comes with a direct Google Maps link so navigation is instant — no copy-pasting addresses.' },
      { icon: '⏱️', title: 'Time-of-Day Optimization', desc: 'Popular spots are scheduled at off-peak times based on real data — beat the crowds at sunrise viewpoints, visit busy markets in the evening.' },
      { icon: '🔀', title: 'Flexible Re-routing', desc: 'Rainy day? Weather-aware rerouting swaps outdoor attractions for indoor alternatives automatically.' },
    ],
    stat1: { value: '40%', label: 'Less Travel Time' },
    stat2: { value: '10+', label: 'Places Per Day Optimized' },
    stat3: { value: 'Real-time', label: 'Google Maps Data' },
  },
  'Budget Prediction': {
    gradient: 'from-emerald-600 via-green-700 to-teal-800',
    bg: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80',
    accentColor: '#34d399',
    glowColor: 'rgba(52,211,153,0.4)',
    tagline: 'Know exactly what your trip will cost before you go',
    overview: 'Our regression-based ML cost model was trained on real travel spending data across 30+ cities. It breaks down your trip budget into hotels, food, transport and activities — per person, per day — with surprising accuracy.',
    points: [
      { icon: '🏨', title: 'Hotel Cost Modeling', desc: 'Budget, mid-range and luxury accommodation costs are estimated per city, per night, scaled for your group size and travel style.' },
      { icon: '🍜', title: 'Food & Dining Estimates', desc: 'From street food to fine dining — the model accounts for your destination\'s food price index and suggests a daily food budget per person.' },
      { icon: '🚕', title: 'Transport Breakdown', desc: 'Local transport, intercity travel, taxis and ride-sharing costs are factored in based on distance and city-specific pricing.' },
      { icon: '🎟️', title: 'Activity & Entry Fees', desc: 'Entry fees for monuments, parks, tours and experiences are pulled from our curated database of 1000+ attractions.' },
    ],
    stat1: { value: '±12%', label: 'Average Cost Accuracy' },
    stat2: { value: '4', label: 'Budget Categories Tracked' },
    stat3: { value: '30+', label: 'Cities Modeled' },
  },
  'Live Weather': {
    gradient: 'from-amber-500 via-orange-600 to-yellow-700',
    bg: 'https://images.unsplash.com/photo-1504608524841-42584120d693?w=1600&q=80',
    accentColor: '#fbbf24',
    glowColor: 'rgba(245,158,11,0.4)',
    tagline: 'Your itinerary adapts to the sky above you',
    overview: 'Weather changes everything about a travel day. Our OpenWeatherMap integration pulls live and forecasted conditions for your destination and dynamically adjusts what you do each day — so bad weather never ruins a plan.',
    points: [
      { icon: '🌧️', title: 'Rain-Day Alternatives', desc: 'When rain is forecast, outdoor beaches and hikes are replaced with museums, galleries, cafés and indoor experiences automatically.' },
      { icon: '☀️', title: 'Golden Hour Scheduling', desc: 'Sunrise and sunset times are used to schedule photography spots, viewpoints and rooftop dining at exactly the right moment.' },
      { icon: '🌡️', title: 'Heat & Cold Warnings', desc: 'Extreme temperatures trigger pacing adjustments — midday rest during peak heat, early-morning outdoor activities in hot climates.' },
      { icon: '📅', title: '7-Day Forecast Integration', desc: 'For multi-day trips, the planner spreads weather-sensitive activities to the best forecast days in your window.' },
    ],
    stat1: { value: 'Live', label: 'Weather Data' },
    stat2: { value: '7-day', label: 'Forecast Horizon' },
    stat3: { value: '1000+', label: 'Cities Covered' },
  },
  'Real Places Only': {
    gradient: 'from-rose-600 via-pink-700 to-fuchsia-800',
    bg: 'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1600&q=80',
    accentColor: '#f472b6',
    glowColor: 'rgba(244,114,182,0.4)',
    tagline: 'Zero hallucinations. Only verified real attractions.',
    overview: 'AI hallucination is a real problem — models can invent places that don\'t exist. We solve this by grounding every attraction in real data: Google Places API for live results combined with a hand-curated database of 1000+ verified attractions across 30+ cities.',
    points: [
      { icon: '🔍', title: 'Google Places API', desc: 'Every attraction is fetched live from Google Places — verified, geolocated and real. If Google doesn\'t know it, we don\'t suggest it.' },
      { icon: '📚', title: 'Curated World Database', desc: 'Our team has hand-verified 1000+ top attractions with correct addresses, opening hours, entry fees and best-visit times.' },
      { icon: '⭐', title: 'Rating-Based Ranking', desc: 'Places are ranked using a blend of Google ratings, review count, and our AI relevance score — so you always get the best, not just the popular.' },
      { icon: '🛡️', title: 'Zero Fake Locations', desc: 'Every place in your itinerary can be opened directly in Google Maps. No invented names, no wrong addresses, no disappointments on arrival.' },
    ],
    stat1: { value: '1000+', label: 'Verified Attractions' },
    stat2: { value: '0', label: 'Hallucinated Places' },
    stat3: { value: '30+', label: 'Cities in Database' },
  },
  'Any Destination': {
    gradient: 'from-teal-600 via-cyan-700 to-blue-800',
    bg: 'https://images.unsplash.com/photo-1488085061387-422e29b40080?w=1600&q=80',
    accentColor: '#2dd4bf',
    glowColor: 'rgba(45,212,191,0.4)',
    tagline: 'From Shimla to Sydney. Your world, planned.',
    overview: 'Smart Travel Planner works for any city on Earth. Whether it\'s a tiny hill station in the Himalayas or a sprawling metropolis like Tokyo — our AI + Places API combination can generate a rich, real itinerary for it.',
    points: [
      { icon: '🌏', title: 'Global Google Places Coverage', desc: 'The Google Places API covers every city with verified tourist data — so you\'re never limited to a fixed list of destinations.' },
      { icon: '🏔️', title: 'Tier-1 to Tier-3 Cities', desc: 'We don\'t just cover the famous cities. Niche destinations like Coorg, Hampi, Rishikesh or Ooty get just as detailed itineraries as Paris or Tokyo.' },
      { icon: '🗓️', title: '1 to 14 Day Trips', desc: 'Plan a quick weekend getaway or an extended two-week expedition. The AI scales content, pacing and budget for any trip length.' },
      { icon: '👨‍👩‍👧‍👦', title: 'Any Group Type', desc: 'Solo traveler, couple, family with kids, group of friends — the AI adapts recommendations, accommodation and activity types for your group.' },
    ],
    stat1: { value: '∞', label: 'Destinations Possible' },
    stat2: { value: '1–14', label: 'Trip Days Supported' },
    stat3: { value: 'Any', label: 'Group Size' },
  },
}

export default function FeatureDetail({ feature, onClose }) {
  const [visible, setVisible] = useState(false)
  const [activePoint, setActivePoint] = useState(null)
  const data = FEATURE_DETAILS[feature?.title]

  // Mount animation
  useEffect(() => {
    if (feature) {
      document.body.style.overflow = 'hidden'
      requestAnimationFrame(() => setVisible(true))
    }
    return () => { document.body.style.overflow = '' }
  }, [feature])

  const handleClose = () => {
    setVisible(false)
    setTimeout(() => {
      document.body.style.overflow = ''
      onClose()
    }, 400)
  }

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') handleClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  if (!feature || !data) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'scale(1)' : 'scale(1.04)',
        transition: 'opacity 0.4s cubic-bezier(0.16,1,0.3,1), transform 0.4s cubic-bezier(0.16,1,0.3,1)',
      }}
    >
      {/* Background photo */}
      <div className="absolute inset-0">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${data.bg})`,
            transform: visible ? 'scale(1)' : 'scale(1.08)',
            transition: 'transform 0.7s cubic-bezier(0.16,1,0.3,1)',
          }}
        />
        <div className="absolute inset-0" style={{ background: 'rgba(4,6,18,0.82)' }} />
        <div className="absolute inset-0" style={{
          background: `linear-gradient(135deg, ${data.glowColor.replace('0.4', '0.25')} 0%, transparent 50%, rgba(4,6,18,0.6) 100%)`
        }} />
      </div>

      {/* Scrollable content */}
      <div className="relative z-10 w-full overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-12 md:py-16">

          {/* Close button */}
          <button
            onClick={handleClose}
            className="fixed top-6 right-6 w-12 h-12 rounded-2xl flex items-center justify-center text-white/70 hover:text-white transition-all hover:scale-110 z-20"
            style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', backdropFilter: 'blur(8px)' }}
          >
            ✕
          </button>

          {/* Header */}
          <div
            className="mb-12"
            style={{
              opacity: visible ? 1 : 0,
              transform: visible ? 'translateY(0)' : 'translateY(24px)',
              transition: 'opacity 0.5s ease 0.15s, transform 0.5s ease 0.15s',
            }}
          >
            <div
              className="w-20 h-20 rounded-3xl flex items-center justify-center text-4xl mb-6 shadow-2xl"
              style={{ background: `linear-gradient(135deg, ${data.accentColor}, ${data.accentColor}88)`, boxShadow: `0 0 40px ${data.glowColor}` }}
            >
              {feature.icon}
            </div>
            <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-4"
              style={{ background: `${data.accentColor}20`, border: `1px solid ${data.accentColor}40`, color: data.accentColor }}>
              Smart Travel Planner · Feature
            </div>
            <h1 className="font-outfit font-black text-white text-4xl md:text-6xl leading-tight mb-4">{feature.title}</h1>
            <p className="text-white/50 text-xl font-medium" style={{ color: data.accentColor + 'cc' }}>{data.tagline}</p>
          </div>

          {/* Overview */}
          <div
            className="rounded-3xl p-8 mb-10"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: `1px solid ${data.accentColor}25`,
              backdropFilter: 'blur(16px)',
              opacity: visible ? 1 : 0,
              transform: visible ? 'translateY(0)' : 'translateY(24px)',
              transition: 'opacity 0.5s ease 0.25s, transform 0.5s ease 0.25s',
            }}
          >
            <p className="text-white/75 text-lg leading-relaxed">{data.overview}</p>
          </div>

          {/* Stats row */}
          <div
            className="grid grid-cols-3 gap-4 mb-12"
            style={{
              opacity: visible ? 1 : 0,
              transform: visible ? 'translateY(0)' : 'translateY(24px)',
              transition: 'opacity 0.5s ease 0.35s, transform 0.5s ease 0.35s',
            }}
          >
            {[data.stat1, data.stat2, data.stat3].map((s, i) => (
              <div key={i} className="rounded-2xl p-6 text-center"
                style={{ background: 'rgba(255,255,255,0.04)', border: `1px solid ${data.accentColor}20`, backdropFilter: 'blur(12px)' }}>
                <div className="font-outfit font-black text-3xl mb-1" style={{ color: data.accentColor }}>{s.value}</div>
                <div className="text-white/45 text-xs font-medium uppercase tracking-wider">{s.label}</div>
              </div>
            ))}
          </div>

          {/* Feature points */}
          <div
            style={{
              opacity: visible ? 1 : 0,
              transform: visible ? 'translateY(0)' : 'translateY(24px)',
              transition: 'opacity 0.5s ease 0.45s, transform 0.5s ease 0.45s',
            }}
          >
            <h2 className="font-outfit font-bold text-white text-2xl mb-6">What makes it powerful</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.points.map((p, i) => (
                <div
                  key={i}
                  onClick={() => setActivePoint(activePoint === i ? null : i)}
                  className="rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:-translate-y-1"
                  style={{
                    background: activePoint === i ? `${data.accentColor}15` : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${activePoint === i ? data.accentColor + '50' : 'rgba(255,255,255,0.07)'}`,
                    backdropFilter: 'blur(12px)',
                    boxShadow: activePoint === i ? `0 0 24px ${data.glowColor}` : 'none',
                    animationDelay: `${0.55 + i * 0.1}s`,
                  }}
                >
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                      style={{ background: `${data.accentColor}18` }}>
                      {p.icon}
                    </div>
                    <div>
                      <h3 className="font-outfit font-bold text-white text-base mb-1">{p.title}</h3>
                      <p className="text-white/50 text-sm leading-relaxed"
                        style={{ maxHeight: activePoint === i ? '200px' : '48px', overflow: 'hidden', transition: 'max-height 0.4s ease' }}>
                        {p.desc}
                      </p>
                      <div className="mt-2 text-xs font-semibold" style={{ color: data.accentColor }}>
                        {activePoint === i ? '▲ Show less' : '▼ Read more'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div
            className="mt-12 text-center pb-8"
            style={{
              opacity: visible ? 1 : 0,
              transition: 'opacity 0.5s ease 0.7s',
            }}
          >
            <p className="text-white/40 text-sm mb-5">Ready to experience this in action?</p>
            <button
              onClick={handleClose}
              className="font-outfit font-black text-lg px-12 py-5 rounded-2xl text-white transition-all hover:-translate-y-1 hover:scale-105"
              style={{ background: `linear-gradient(135deg, ${data.accentColor}, ${data.accentColor}88)`, boxShadow: `0 0 40px ${data.glowColor}` }}
            >
              ✨ Start Planning Free
            </button>
          </div>

        </div>
      </div>
    </div>
  )
}
