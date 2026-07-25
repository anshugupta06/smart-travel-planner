import WeatherCard from './WeatherCard'
import BudgetCard from './BudgetCard'
import DayPlanCard from './DayPlanCard'
import TopPlacesCard from './TopPlacesCard'
import TravelChatbot from './TravelChatbot'
import PackingList from './PackingList'
import TripComparison from './TripComparison'
import TripRating from './TripRating'
import CurrencyWidget from './CurrencyWidget'
import BestTimeCalendar from './BestTimeCalendar'
import { OfflineSaveBanner } from './OfflineMode'
import ShareTrip from './ShareTrip'
import { useState } from 'react'
const fmt = (n) => `₹${Number(n).toLocaleString('en-IN')}`
const TRAVEL_EMOJI = { budget: '🎒', moderate: '🌟', luxury: '💎' }

const DEST_HERO = {
  'goa':'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1600',
  'jaipur':'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=1600',
  'paris':'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1600',
  'dubai':'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1600',
  'bali':'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1600',
  'istanbul':'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=1600',
  'tokyo':'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1600',
  'manali':'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=1600',
  'delhi':'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1600',
  'mumbai':'https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?w=1600',
  'agra':'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=1600',
  'varanasi':'https://images.unsplash.com/photo-1561361058-c24cecae35ca?w=1600',
  'kerala':'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1600',
  'shimla':'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=1600',
  'rishikesh':'https://images.unsplash.com/photo-1623158228064-0500f3d3b35b?w=1600',
  'london':'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1600',
  'new york':'https://images.unsplash.com/photo-1534430480872-3498386e7856?w=1600',
  'singapore':'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=1600',
  'bangkok':'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=1600',
  'sydney':'https://images.unsplash.com/photo-1523428096881-5bd79d043006?w=1600',
  'rome':'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1600',
  'amsterdam':'https://images.unsplash.com/photo-1468581264429-2548ef9eb732?w=1600',
}

function getHeroImage(destination = '') {
  const key = destination.toLowerCase().trim()
  if (DEST_HERO[key]) return DEST_HERO[key]
  for (const [k, v] of Object.entries(DEST_HERO)) {
    if (key.startsWith(k) || k.startsWith(key)) return v
  }
  return 'https://images.unsplash.com/photo-1488085061387-422e29b40080?w=1600'
}

function TransportBadge({ message, origin, destination }) {
  const modeMatch = message?.match(/·\s(.+?)\srecommended/)
  const mode = modeMatch?.[1] || 'Check routes'
  const mapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&travelmode=driving`
  const emoji = mode.includes('Flight') ? '✈️' : mode.includes('Train') ? '🚂' : mode.includes('Bus') ? '🚌' : '🚗'
  return (
    <div className="flex items-center gap-4 p-5 rounded-2xl"
      style={{ background: 'rgba(6,9,24,0.6)', border: '1px solid rgba(245,158,11,0.2)', backdropFilter: 'blur(16px)' }}>
      <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
        style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 0 20px rgba(245,158,11,0.3)' }}>
        {emoji}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest">Getting There</p>
        <div className="font-outfit font-black text-white truncate">{origin} → {destination}</div>
        <div className="text-amber-300/70 text-xs mt-0.5">{mode}</div>
      </div>
      <a href={mapsUrl} target="_blank" rel="noopener noreferrer"
        className="text-xs font-black px-4 py-2.5 rounded-xl text-white transition-all hover:-translate-y-0.5 flex-shrink-0"
        style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
        🗺️ Route
      </a>
    </div>
  )
}

export default function ItineraryResult({ data, onNewTrip }) {
  const { destination, origin, days, travel_type, num_people, budget_provided,
    weather, day_plans, budget_estimate, travel_tips, top_places,
    itinerary_summary, message, transport_options = [] } = data

  const [heroLoaded, setHeroLoaded] = useState(false)
  const [showPacking, setShowPacking]     = useState(false)
  const [showCompare, setShowCompare]     = useState(false)
  const [sideOpen,   setSideOpen]         = useState(false)
  const heroImg = getHeroImage(destination)

  const handlePDF = () => {
    // Inject a clean print stylesheet, trigger print (Save as PDF in browser dialog)
    const existing = document.getElementById('stp-print-style')
    if (existing) existing.remove()
    const s = document.createElement('style')
    s.id = 'stp-print-style'
    s.innerHTML = `
      @media print {
        body { background: white !important; color: #111 !important; }
        header, .no-print, aside, button { display: none !important; }
        .fixed { position: static !important; }
        * { box-shadow: none !important; backdrop-filter: none !important; }
        h1, h2, h3 { color: #111 !important; }
        p, div, span { color: #333 !important; background: transparent !important; border-color: #ddd !important; }
        .rounded-3xl, .rounded-2xl { border-radius: 8px !important; border: 1px solid #eee !important; }
        @page { margin: 1.5cm; }
      }
    `
    document.head.appendChild(s)
    window.print()
    setTimeout(() => s.remove(), 2000)
  }

  return (
    <div className="min-h-screen relative" style={{ background: '#060918' }}>
      {/* Packing list modal */}
      {showPacking && <PackingList tripData={data} onClose={() => setShowPacking(false)} />}
      {/* Budget comparison modal */}
      {showCompare && <TripComparison tripData={data} onClose={() => setShowCompare(false)} />}

      {/* ── SIDE PANEL OVERLAY ─────────────────────────────── */}
      {/* Backdrop */}
      {sideOpen && (
        <div
          className="fixed inset-0 z-40"
          style={{ background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(4px)' }}
          onClick={() => setSideOpen(false)}
        />
      )}
      {/* Slide-in panel — full width on mobile, 600px on desktop */}
      <div
        className="fixed top-0 left-0 z-50 h-full overflow-y-auto transition-transform duration-300 ease-out no-print"
        style={{
          width: 'min(600px, 100vw)',
          transform: sideOpen ? 'translateX(0)' : 'translateX(-100%)',
          background: 'rgba(6,9,24,0.97)',
          borderRight: '1px solid rgba(255,255,255,0.08)',
          boxShadow: '8px 0 40px rgba(0,0,0,0.6)',
        }}
      >
        {/* Panel header */}
        <div className="flex items-center justify-between px-5 py-4 sticky top-0 z-10"
          style={{ background: 'rgba(6,9,24,0.97)', borderBottom: '1px solid rgba(255,255,255,0.07)' }}>
          <div>
            <div className="font-outfit font-black text-white text-base">{destination}</div>
            <div className="text-white/35 text-xs mt-0.5">Trip Tools</div>
          </div>
          <button onClick={() => setSideOpen(false)}
            className="w-8 h-8 rounded-xl flex items-center justify-center text-white/50 hover:text-white transition-colors"
            style={{ background: 'rgba(255,255,255,0.07)' }}>✕</button>
        </div>

        {/* Panel content */}
        <div className="px-5 py-5 space-y-5">

          {/* Mobile-only quick actions (hidden on sm+ where top bar shows them) */}
          <div className="grid grid-cols-2 gap-2 sm:hidden">
            {[
              { icon: '📄', label: 'PDF', action: handlePDF },
              { icon: '🖨️', label: 'Print', action: () => window.print() },
              { icon: '🎒', label: 'Pack List', action: () => { setSideOpen(false); setShowPacking(true) } },
              { icon: '⚖️', label: 'Compare', action: () => { setSideOpen(false); setShowCompare(true) } },
            ].map(item => (
              <button key={item.label} onClick={item.action}
                className="flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-semibold text-white/70 hover:text-white transition-all hover:bg-white/10"
                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <span>{item.icon}</span> {item.label}
              </button>
            ))}
          </div>

          {/* Divider */}
          <div style={{ height: '1px', background: 'rgba(255,255,255,0.06)' }} />

          {/* Travel Tips */}
          {travel_tips?.length > 0 && (
            <div>
              <div className="text-amber-400 text-xs font-black uppercase tracking-widest mb-3">💡 Travel Tips</div>
              <div className="space-y-2">
                {travel_tips.map((tip, i) => (
                  <div key={i} className="flex items-start gap-2.5 p-3 rounded-xl"
                    style={{ background: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.1)' }}>
                    <span className="w-5 h-5 rounded-lg flex items-center justify-center text-[10px] font-black text-white flex-shrink-0"
                      style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>{i+1}</span>
                    <p className="text-white/55 text-xs leading-relaxed">{tip}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Divider */}
          <div style={{ height: '1px', background: 'rgba(255,255,255,0.06)' }} />

          {/* Currency */}
          <CurrencyWidget budgetINR={budget_provided} destination={destination} />

          {/* Divider */}
          <div style={{ height: '1px', background: 'rgba(255,255,255,0.06)' }} />

          {/* Best Time */}
          <BestTimeCalendar destination={destination} />

          {/* Divider */}
          <div style={{ height: '1px', background: 'rgba(255,255,255,0.06)' }} />

          {/* Share + Offline */}
          <ShareTrip tripId={data?.id || null} destination={destination} />
          <OfflineSaveBanner tripData={data} />

          {/* Divider */}
          <div style={{ height: '1px', background: 'rgba(255,255,255,0.06)' }} />

          {/* Rating */}
          <TripRating tripId={data?.id || null} destination={destination} />

        </div>
      </div>

      {/* ════════════════════════════════════════════════════
          FULL-PAGE FIXED BACKGROUND — blurred destination photo
          covers the entire page behind all content
      ════════════════════════════════════════════════════ */}
      <div className="fixed inset-0 z-0" style={{ pointerEvents: 'none' }}>
        <img
          src={heroImg} alt=""
          className="w-full h-full object-cover"
          style={{
            opacity: heroLoaded ? 0.18 : 0,
            transform: 'scale(1.05)',
            transition: 'opacity 1.5s ease',
            filter: 'blur(2px)',
          }}
          onLoad={() => setHeroLoaded(true)}
        />
        {/* Dark base so it stays readable */}
        <div className="absolute inset-0" style={{ background: 'rgba(6,9,24,0.78)' }} />
        {/* Ambient color tints */}
        <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg,rgba(180,80,0,0.08) 0%,transparent 50%,rgba(100,50,200,0.06) 100%)' }} />
        {/* Top fade for header area */}
        <div className="absolute top-0 left-0 right-0 h-32" style={{ background: 'linear-gradient(to bottom,rgba(6,9,24,0.6),transparent)' }} />
      </div>

      {/* ── CINEMATIC HERO ─────────────────────────────────── */}
      <div className="relative z-10 overflow-hidden" style={{ minHeight: '500px' }}>
        {/* Sharp hero image (not blurred) */}
        <div className="absolute inset-0">
          <img src={heroImg} alt={destination}
            className="w-full h-full object-cover"
            style={{ opacity: heroLoaded ? 1 : 0, transform: heroLoaded ? 'scale(1.04)' : 'scale(1)', transition: 'transform 10s ease-out, opacity 1s ease' }}
            onLoad={() => setHeroLoaded(true)} />
          {/* Progressive overlay: clear top → opaque bottom */}
          <div className="absolute inset-0" style={{ background: 'linear-gradient(to bottom, rgba(6,9,24,0.2) 0%, rgba(6,9,24,0.45) 35%, rgba(6,9,24,0.88) 75%, rgba(6,9,24,1) 100%)' }} />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(to right, rgba(6,9,24,0.3) 0%, transparent 50%)' }} />
        </div>

        {/* Floating orbs */}
        <div className="absolute top-8 right-24 w-72 h-72 rounded-full blur-3xl opacity-25 pointer-events-none"
          style={{ background: 'radial-gradient(circle,#f59e0b,transparent)' }} />
        <div className="absolute bottom-24 left-8 w-56 h-56 rounded-full blur-3xl opacity-15 pointer-events-none"
          style={{ background: 'radial-gradient(circle,#a78bfa,transparent)' }} />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 pt-10 sm:pt-14 pb-16 sm:pb-20">
          {/* Actions row */}
          <div className="flex items-center justify-between gap-2 mb-12 no-print">
            {/* Hamburger — opens side panel */}
            <button
              onClick={() => setSideOpen(true)}
              className="flex flex-col justify-center items-center gap-1.5 w-11 h-11 rounded-xl transition-all hover:bg-white/10 flex-shrink-0"
              style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.12)' }}
              title="Trip Tools"
            >
              <span className="block w-5 h-0.5 rounded-full bg-white/70" />
              <span className="block w-5 h-0.5 rounded-full bg-white/70" />
              <span className="block w-5 h-0.5 rounded-full bg-white/70" />
            </button>

            {/* Right side actions — PDF/Print/Pack/Compare hidden on mobile */}
            <div className="flex items-center gap-2">
              {[['📄 PDF', handlePDF], ['🖨️ Print', () => window.print()]].map(([label, fn]) => (
                <button key={label} onClick={fn}
                  className="hidden sm:block text-white/60 hover:text-white text-sm font-bold px-4 py-2 rounded-xl transition-all"
                  style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(8px)' }}>
                  {label}
                </button>
              ))}
              <button onClick={() => setShowPacking(true)}
                className="hidden sm:block text-white/60 hover:text-white text-sm font-bold px-4 py-2 rounded-xl transition-all"
                style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(8px)' }}>
                🎒 Pack
              </button>
              <button onClick={() => setShowCompare(true)}
                className="hidden sm:block text-white/60 hover:text-white text-sm font-bold px-4 py-2 rounded-xl transition-all"
                style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(8px)' }}>
                ⚖️ Compare
              </button>
              <button onClick={onNewTrip}
                className="text-sm px-4 py-2 rounded-xl font-black text-white transition-all hover:scale-105"
                style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 0 16px rgba(245,158,11,0.4)' }}>
                + New Trip
              </button>
            </div>
          </div>

          {/* Route breadcrumb */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6 text-sm font-semibold"
            style={{ background: 'rgba(255,255,255,0.08)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.12)' }}>
            <span className="text-white/45">{origin}</span>
            <span className="text-amber-400 font-black">→</span>
            <span className="text-amber-300 font-bold">{destination}</span>
          </div>

          {/* Destination name */}
          <h1 className="font-outfit font-black text-white leading-none mb-4"
            style={{ fontSize: 'clamp(2.5rem,10vw,8rem)', textShadow: '0 8px 60px rgba(0,0,0,0.6)' }}>
            {destination}
          </h1>

          {itinerary_summary && (
            <p className="text-white/55 max-w-2xl leading-relaxed text-sm sm:text-lg mb-6 sm:mb-8">{itinerary_summary}</p>
          )}

          {/* Info chips */}
          <div className="flex flex-wrap gap-1.5 sm:gap-2 mb-6 sm:mb-10">
            {[
              `📅 ${days} Days`,
              `👥 ${num_people} Traveler${num_people > 1 ? 's' : ''}`,
              `${TRAVEL_EMOJI[travel_type] || '🌟'} ${travel_type?.charAt(0).toUpperCase() + travel_type?.slice(1)}`,
              `💰 ${fmt(budget_provided)}`,
              weather ? `${weather.icon} ${weather.temperature}°C` : null,
            ].filter(Boolean).map((chip, i) => (
              <span key={i} className="text-white/75 text-xs sm:text-sm font-semibold px-3 sm:px-4 py-1.5 sm:py-2 rounded-full"
                style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.14)' }}>
                {chip}
              </span>
            ))}
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { icon: '📍', val: `${top_places?.length || 0}`, label: 'Attractions', color: '#22d3ee' },
              { icon: '📅', val: `${days}`, label: 'Days Planned', color: '#a78bfa' },
              { icon: '💰', val: fmt(budget_estimate?.per_person || 0), label: 'Per Person', color: '#f59e0b' },
              { icon: weather?.icon || '🌤️', val: `${weather?.temperature || '--'}°C`, label: weather?.description || 'Weather', color: '#34d399' },
            ].map((s, i) => (
              <div key={i} className="flex items-center gap-3 p-4 rounded-2xl"
                style={{ background: 'rgba(6,9,24,0.55)', border: `1px solid ${s.color}25`, backdropFilter: 'blur(16px)' }}>
                <div className="text-2xl">{s.icon}</div>
                <div>
                  <div className="font-outfit font-black text-white text-lg leading-none">{s.val}</div>
                  <div className="text-xs font-medium mt-0.5" style={{ color: s.color + '99' }}>{s.label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── ALL CONTENT (over the blurred full-page bg) ─────── */}
      <div className="relative z-10">
        {/* Two-column layout: itinerary left, chatbot right */}
        <div className="max-w-[1600px] mx-auto px-3 sm:px-4 pb-24">
          <div className="flex gap-6 items-start">

            {/* ══ LEFT COLUMN — itinerary content ══════════════════ */}
            <main className="flex-1 min-w-0 space-y-10">

              {/* ── TRANSPORT + WEATHER ─────────────────────────── */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <TransportBadge message={message} origin={origin} destination={destination} />
                {weather && <WeatherCard weather={weather} destination={destination} />}
              </div>

              {/* ── PLACES TO VISIT + MAP ───────────────────────── */}
              {top_places?.length > 0 && (
                <section className="p-8 rounded-3xl"
                  style={{ background: 'rgba(6,9,24,0.6)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(20px)' }}>
                  <TopPlacesCard places={top_places} destination={destination} />
                </section>
              )}

              {/* ── DAY-WISE ITINERARY ───────────────────────────── */}
              <section>
                <div className="flex items-end justify-between mb-8">
                  <div>
                    <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-3"
                      style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
                      🗓️ Day by Day
                    </div>
                    <h2 className="font-outfit font-black text-white text-4xl md:text-5xl">
                      Your <span className="text-gold-gradient">{days}-Day</span> Itinerary
                    </h2>
                    <p className="text-white/30 text-sm mt-2">Best places for your {fmt(budget_provided)} budget · Optimized by AI</p>
                  </div>
                  <span className="text-white/20 text-sm hidden md:block">Click any day to expand</span>
                </div>
                <div className="space-y-5">
                  {day_plans?.map((day, i) => <DayPlanCard key={i} day={day} />)}
                </div>
              </section>

              {/* ── BUDGET ──────────────────────────────────────── */}
              {budget_estimate && (
                <BudgetCard budget={budget_estimate} numPeople={num_people} budgetProvided={budget_provided} transportOptions={transport_options} />
              )}

              {/* ── TRAVEL TIPS ─────────────────────────────────── */}
              {/* Moved to side panel (☰ menu) */}

              {/* ── CURRENCY + BEST TIME + OFFLINE + SHARE ──────── */}
              {/* These have moved to the side panel (☰ menu) */}

              {/* ── TRIP RATING ──────────────────────────────────── */}
              {/* Moved to side panel */}

              {/* ── FOOTER CTA ──────────────────────────────────── */}
              <div className="no-print">
                <div className="relative rounded-3xl overflow-hidden p-14 text-center"
                  style={{ background: 'rgba(6,9,24,0.65)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(20px)' }}>
                  <div className="absolute inset-0 pointer-events-none overflow-hidden">
                    <div className="absolute top-0 left-1/4 w-72 h-72 rounded-full blur-3xl opacity-12"
                      style={{ background: 'radial-gradient(circle,#f59e0b,transparent)' }} />
                    <div className="absolute bottom-0 right-1/4 w-72 h-72 rounded-full blur-3xl opacity-8"
                      style={{ background: 'radial-gradient(circle,#a78bfa,transparent)' }} />
                  </div>
                  <div className="relative z-10">
                    <div className="text-6xl mb-5" style={{ animation: 'float 4s ease-in-out infinite' }}>✈️</div>
                    <h3 className="font-outfit font-black text-white text-4xl mb-3">Ready for Another Adventure?</h3>
                    <p className="text-white/35 text-base mb-8 max-w-md mx-auto">Your next dream trip is just 30 seconds away. Plan anywhere in the world.</p>
                    <button onClick={onNewTrip}
                      className="font-outfit font-black text-lg px-16 py-5 rounded-2xl text-white transition-all hover:-translate-y-1 hover:scale-105"
                      style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 0 50px rgba(245,158,11,0.45)' }}>
                      ✈️ Plan Another Trip
                    </button>
                    <p className="text-xs text-white/20 mt-5">Generated by Smart Travel Planner · Gemini AI + ML</p>
                  </div>
                </div>
              </div>

            </main>

            {/* ══ RIGHT COLUMN — sticky chatbot panel ══════════════ */}
            <aside
              className="no-print hidden xl:flex flex-col flex-shrink-0"
              style={{ width: '460px', position: 'sticky', top: '24px', height: 'calc(100vh - 48px)', maxHeight: '920px' }}
            >
              {/* Panel label */}
              <div className="flex items-center gap-2 mb-3 px-1">
                <div className="h-px flex-1" style={{ background: 'rgba(245,158,11,0.15)' }} />
                <span className="text-amber-400/50 text-xs font-bold uppercase tracking-widest">Ask AI</span>
                <div className="h-px flex-1" style={{ background: 'rgba(245,158,11,0.15)' }} />
              </div>
              <TravelChatbot tripData={data} />
            </aside>

          </div>
        </div>

        {/* ── Mobile floating chatbot button + drawer (< xl) ── */}
        <MobileChatbot tripData={data} />
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────
   Mobile chatbot: floating button + slide-up drawer for screens < xl
───────────────────────────────────────────────────────────────────────── */
function MobileChatbot({ tripData }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="xl:hidden no-print">
      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40"
          style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
          onClick={() => setOpen(false)}
        />
      )}

      {/* Drawer */}
      <div
        className="fixed bottom-0 left-0 right-0 z-50 rounded-t-3xl overflow-hidden transition-transform duration-300 ease-out"
        style={{
          height: '80vh',
          transform: open ? 'translateY(0)' : 'translateY(100%)',
          background: 'rgba(6,9,24,0.97)',
          border: '1px solid rgba(245,158,11,0.2)',
          borderBottom: 'none',
          boxShadow: '0 -20px 60px rgba(0,0,0,0.5)',
        }}
      >
        {/* Drag handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full" style={{ background: 'rgba(255,255,255,0.15)' }} />
        </div>
        <div className="h-[calc(100%-20px)]">
          <TravelChatbot tripData={tripData} />
        </div>
      </div>

      {/* Floating button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-2xl flex items-center justify-center text-2xl transition-all hover:scale-110 active:scale-95"
          style={{
            background: 'linear-gradient(135deg,#f59e0b,#ea580c)',
            boxShadow: '0 0 30px rgba(245,158,11,0.5), 0 8px 24px rgba(0,0,0,0.4)',
          }}
        >
          🤖
        </button>
      )}
    </div>
  )
}
