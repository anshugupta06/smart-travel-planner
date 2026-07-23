import { useState, useEffect } from 'react'

const STEPS = [
  { icon: '📍', text: 'Fetching real attractions from Google Places…', color: 'from-blue-500 to-cyan-500' },
  { icon: '🤖', text: 'AI ranking by tourist popularity…',             color: 'from-violet-500 to-purple-600' },
  { icon: '🗺️', text: 'Optimizing route with ML algorithm…',          color: 'from-emerald-500 to-teal-600' },
  { icon: '💰', text: 'Predicting budget and costs…',                  color: 'from-amber-500 to-orange-600' },
  { icon: '✍️', text: 'Generating itinerary with Gemini AI…',         color: 'from-rose-500 to-pink-600' },
  { icon: '🌤️', text: 'Checking live weather forecasts…',            color: 'from-sky-500 to-blue-600' },
]

export default function LoadingScreen() {
  const [active, setActive] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setActive(a => (a + 1) % STEPS.length), 2200)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0891b2 100%)' }}>

      {/* Background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[0,1,2].map(i => (
          <div key={i} className="absolute rounded-full blur-3xl opacity-20"
            style={{
              width: `${300 + i*100}px`, height: `${300 + i*100}px`,
              background: ['#3b82f6','#8b5cf6','#06b6d4'][i],
              top: `${[10,40,70][i]}%`, left: `${[60,10,50][i]}%`,
              animation: `float ${4+i}s ease-in-out infinite`,
              animationDelay: `${i*1.3}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 text-center max-w-lg w-full px-6">
        {/* Plane */}
        <div className="text-8xl mb-6 inline-block" style={{ animation: 'float 2.5s ease-in-out infinite' }}>✈️</div>

        <h2 className="text-3xl font-black text-white mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
          Planning Your Trip
        </h2>
        <p className="text-blue-200 mb-10 text-base">AI is crafting your perfect itinerary…</p>

        {/* Steps */}
        <div className="space-y-3">
          {STEPS.map((step, i) => {
            const isDone   = i < active
            const isCurrent = i === active
            return (
              <div key={i}
                className={`flex items-center gap-4 rounded-2xl px-5 py-3.5 transition-all duration-500 ${
                  isCurrent ? 'bg-white/15 scale-[1.02] shadow-xl' :
                  isDone    ? 'bg-white/5 opacity-60' : 'bg-white/5 opacity-30'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl flex-shrink-0 ${
                  isDone ? 'bg-green-400/30' : isCurrent ? `bg-gradient-to-br ${step.color}` : 'bg-white/10'
                }`}>
                  {isDone ? '✓' : step.icon}
                </div>
                <span className={`text-sm font-semibold flex-1 text-left ${isCurrent ? 'text-white' : 'text-white/70'}`}>
                  {step.text}
                </span>
                {isCurrent && (
                  <div className="w-5 h-5 border-2 border-white/50 border-t-white rounded-full animate-spin flex-shrink-0" />
                )}
                {isDone && <span className="text-green-400 text-sm flex-shrink-0">✓</span>}
              </div>
            )
          })}
        </div>

        {/* Progress dots */}
        <div className="flex items-center justify-center gap-2 mt-8">
          {STEPS.map((_, i) => (
            <div key={i} className={`rounded-full transition-all duration-300 ${
              i === active ? 'w-6 h-2.5 bg-white' : i < active ? 'w-2.5 h-2.5 bg-white/60' : 'w-2.5 h-2.5 bg-white/20'
            }`} />
          ))}
        </div>
        <p className="text-blue-200/50 text-xs mt-5">This takes 15–30 seconds</p>
      </div>
    </div>
  )
}
