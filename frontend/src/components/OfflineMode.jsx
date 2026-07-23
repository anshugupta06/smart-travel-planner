import { useState, useEffect } from 'react'

const STORAGE_KEY = 'stp_saved_trip'

// Save the current itinerary to localStorage
export function saveForOffline(tripData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      data:      tripData,
      savedAt:   new Date().toISOString(),
      destination: tripData.destination,
    }))
    return true
  } catch {
    return false
  }
}

// Load saved itinerary from localStorage
export function loadOfflineTrip() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

// Banner shown on the itinerary result page — allows saving for offline
export function OfflineSaveBanner({ tripData }) {
  const [saved,   setSaved]   = useState(false)
  const [toast,   setToast]   = useState('')
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  useEffect(() => {
    const handleOnline  = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    window.addEventListener('online',  handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online',  handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Check if this trip is already saved
  useEffect(() => {
    const saved = loadOfflineTrip()
    if (saved?.destination === tripData?.destination) setSaved(true)
  }, [tripData])

  const handleSave = () => {
    const ok = saveForOffline(tripData)
    if (ok) {
      setSaved(true)
      setToast('✅ Saved! View offline anytime from the header menu.')
      setTimeout(() => setToast(''), 3500)
    }
  }

  return (
    <div className="flex items-center justify-between p-4 rounded-2xl no-print"
      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full"
            style={{ background: isOnline ? '#34d399' : '#f87171', boxShadow: `0 0 6px ${isOnline ? '#34d399' : '#f87171'}` }} />
          <span className="text-xs font-semibold" style={{ color: isOnline ? '#34d399' : '#f87171' }}>
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>
        {toast ? (
          <span className="text-emerald-400 text-xs font-medium">{toast}</span>
        ) : (
          <span className="text-white/35 text-xs">
            {saved ? `📱 ${tripData?.destination} itinerary saved for offline access` : 'Save this itinerary to view without internet'}
          </span>
        )}
      </div>
      <button
        onClick={handleSave}
        disabled={saved}
        className="text-xs font-black px-4 py-2 rounded-xl transition-all hover:-translate-y-0.5 disabled:opacity-50"
        style={{
          background: saved ? 'rgba(52,211,153,0.15)' : 'rgba(255,255,255,0.08)',
          border:     saved ? '1px solid rgba(52,211,153,0.3)' : '1px solid rgba(255,255,255,0.12)',
          color:      saved ? '#34d399' : 'rgba(255,255,255,0.7)',
        }}
      >
        {saved ? '✓ Saved Offline' : '📱 Save Offline'}
      </button>
    </div>
  )
}

// Full offline view shown when user opens the app without internet and has a saved trip
export default function OfflineTripView({ onGoOnline }) {
  const saved = loadOfflineTrip()

  if (!saved) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8"
        style={{ background: '#060918' }}>
        <div className="text-center max-w-md">
          <div className="text-6xl mb-6">📡</div>
          <h2 className="font-outfit font-black text-white text-3xl mb-3">You're Offline</h2>
          <p className="text-white/40 leading-relaxed mb-6">
            No saved itinerary found. Connect to the internet and save a trip to access it offline.
          </p>
          <button onClick={onGoOnline}
            className="px-8 py-3 rounded-2xl font-black text-white"
            style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
            Try to Reconnect
          </button>
        </div>
      </div>
    )
  }

  const savedDate = new Date(saved.savedAt).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  })

  return (
    <div className="min-h-screen flex items-center justify-center p-8"
      style={{ background: '#060918' }}>
      <div className="text-center max-w-sm">
        <div className="text-5xl mb-4">📱</div>
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-black text-red-400 mb-4"
          style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}>
          📡 Offline Mode
        </div>
        <h2 className="font-outfit font-black text-white text-2xl mb-2">Saved Itinerary</h2>
        <p className="text-amber-300 font-bold text-lg mb-1">{saved.destination}</p>
        <p className="text-white/30 text-sm mb-6">Saved on {savedDate}</p>
        <button onClick={onGoOnline}
          className="w-full py-3.5 rounded-2xl font-black text-white mb-3"
          style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 0 20px rgba(245,158,11,0.3)' }}>
          📋 View Saved Itinerary
        </button>
        <p className="text-white/20 text-xs">Tap above to load your saved trip in offline mode</p>
      </div>
    </div>
  )
}
