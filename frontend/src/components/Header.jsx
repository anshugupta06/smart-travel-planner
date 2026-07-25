import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Header({ onNewTrip, showNewTrip, onHome, onHistory, onDashboard }) {
  const { user, logout, openLogin, openSignup } = useAuth()
  const [dropOpen, setDropOpen] = useState(false)
  const dropRef = useRef(null)

  // Close dropdown when clicking anywhere outside it
  useEffect(() => {
    if (!dropOpen) return
    const handle = (e) => {
      if (dropRef.current && !dropRef.current.contains(e.target)) {
        setDropOpen(false)
      }
    }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [dropOpen])

  return (
    <header className="sticky top-0 z-40 text-white"
      style={{
        background: 'rgba(6,9,24,0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.07)',
        boxShadow: '0 4px 30px rgba(0,0,0,0.4)',
      }}>
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-4 flex items-center justify-between">

        {/* Logo */}
        <button onClick={onHome} className="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <span className="text-3xl" style={{ animation: 'float 4s ease-in-out infinite' }}>✈️</span>
          <div>
            <div className="font-outfit font-black text-white text-lg leading-none tracking-tight">Smart Travel Planner</div>
            <div className="text-amber-400 text-[10px] font-bold tracking-widest uppercase mt-0.5">AI-Powered Itineraries</div>
          </div>
        </button>

        {/* Nav */}
        <nav className="hidden lg:flex items-center gap-1">
          {['Features', 'Destinations', 'How It Works'].map(item => (
            <button key={item} onClick={onHome}
              className="text-white/55 hover:text-amber-300 text-sm font-semibold px-4 py-2 rounded-xl transition-all hover:bg-white/5">
              {item}
            </button>
          ))}
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {showNewTrip && (
            <button onClick={onNewTrip}
              className="hidden sm:flex items-center gap-2 text-white text-sm font-bold px-4 py-2.5 rounded-xl transition-all"
              style={{ background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.3)' }}>
              ✈️ New Trip
            </button>
          )}

          {user ? (
            <div className="relative" ref={dropRef}>
              <button onClick={() => setDropOpen(!dropOpen)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-xl transition-all"
                style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.12)' }}>
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white overflow-hidden flex-shrink-0"
                  style={{ background: 'linear-gradient(135deg, #f59e0b, #ea580c)' }}>
                  {user.avatar?.startsWith('http') ? (
                    <img src={user.avatar} alt={user.name} className="w-full h-full object-cover rounded-full" referrerPolicy="no-referrer" />
                  ) : (
                    user.avatar || user.name?.[0]?.toUpperCase() || '?'
                  )}
                </div>
                <span className="text-white text-sm font-semibold hidden sm:block max-w-[120px] truncate">{user.name}</span>
                <span className="text-white/40 text-xs">{dropOpen ? '▲' : '▼'}</span>
              </button>

              {dropOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 rounded-2xl shadow-2xl py-2 z-50 overflow-hidden"
                  style={{ background: 'rgba(10,15,32,0.97)', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(20px)' }}>
                  <div className="px-4 py-3 mb-1" style={{ borderBottom: '1px solid rgba(255,255,255,0.07)' }}>
                    <div className="font-bold text-white text-sm truncate">{user.name}</div>
                    <div className="text-white/35 text-xs truncate mt-0.5">{user.email}</div>
                  </div>
                  {[
                    { icon: '✈️', label: 'Plan New Trip', action: onNewTrip },
                    { icon: '📋', label: 'My Trips',      action: onHistory },
                    { icon: '📊', label: 'Analytics',     action: onDashboard },
                  ].map(item => (
                    <button key={item.label} onClick={() => { setDropOpen(false); item.action?.() }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-white/65 font-medium transition-all hover:text-amber-300 hover:bg-white/5">
                      <span>{item.icon}</span> {item.label}
                    </button>
                  ))}
                  <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }} className="mt-1 pt-1">
                    <button onClick={() => { setDropOpen(false); logout() }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400/80 font-semibold transition-all hover:text-red-400 hover:bg-red-500/10">
                      <span>👋</span> Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button onClick={openLogin}
                className="text-white/60 hover:text-white text-sm font-semibold px-3 py-2 transition-colors">
                Sign In
              </button>
              <button onClick={openSignup}
                className="text-sm font-black px-5 py-2.5 rounded-xl text-white transition-all hover:scale-105"
                style={{ background: 'linear-gradient(135deg, #f59e0b, #ea580c)', boxShadow: '0 0 16px rgba(245,158,11,0.35)' }}>
                Get Started →
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
