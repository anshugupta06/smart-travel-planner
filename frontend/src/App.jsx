import { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import AuthModal from './components/AuthModal'
import LandingPage from './components/LandingPage'
import Header from './components/Header'
import TripForm from './components/TripForm'
import ItineraryResult from './components/ItineraryResult'
import LoadingScreen from './components/LoadingScreen'
import TripHistory from './components/TripHistory'
import Dashboard from './components/Dashboard'
import { loadOfflineTrip } from './components/OfflineMode'
import axios from 'axios'
import { API_BASE } from './config'

function AppContent() {
  const { user, showAuthModal, openSignup, registerNav } = useAuth()
  const [tripData, setTripData]       = useState(null)
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)
  const [view, setView]               = useState('landing')
  const [showHistory,   setShowHistory]   = useState(false)
  const [showDashboard, setShowDashboard] = useState(false)

  // Register nav callbacks so AuthContext can drive navigation after login/logout
  useEffect(() => {
    registerNav(
      () => setView('planner'),   // after login → go to trip planner
      () => { setTripData(null); setError(null); setView('landing') }  // after logout → go to landing
    )
  }, [registerNav])

  // Handle shared trip links — ?share=abc123
  useEffect(() => {
    const params  = new URLSearchParams(window.location.search)
    const shareId = params.get('share')
    if (!shareId) return
    axios.get(`${API_BASE}/api/shared/${shareId}`)
      .then(res => {
        if (res.data.response) {
          setTripData(res.data.response)
          setView('result')
          window.history.replaceState({}, '', window.location.pathname)
        }
      })
      .catch(() => console.warn('[App] Shared trip not found:', shareId))
  }, [])

  // Offline mode — load saved trip from localStorage if offline
  useEffect(() => {
    if (navigator.onLine) return
    const saved = loadOfflineTrip()
    if (saved?.data) {
      setTripData(saved.data)
      setView('result')
    }
  }, [])

  const handlePlanTrip = async (formData) => {
    setLoading(true)
    setError(null)
    setView('planner')  // stay on planner while loading — prevent flash to landing
    try {
      const response = await axios.post(`${API_BASE}/api/plan-trip`, formData, { timeout: 90000 })
      setTripData(response.data)
      setView('result')
    } catch (err) {
      const detail = err.response?.data?.detail
      let msg = 'Failed to generate itinerary. Please try again.'
      if (typeof detail === 'string') {
        msg = detail
      } else if (Array.isArray(detail)) {
        // Pydantic validation errors
        msg = detail.map(d => `${d.loc?.join('.')}: ${d.msg}`).join(', ')
      } else if (err.message) {
        msg = err.message
      }
      console.error('[App] plan-trip error:', err.response?.status, msg)
      setError(msg)
      setView('planner')   // explicitly stay on planner to show the error
    } finally {
      setLoading(false)
    }
  }

  const handleNewTrip = () => {
    setTripData(null)
    setView('planner')
    setError(null)
  }

  const handleHome = () => {
    setTripData(null)
    setView('landing')
    setError(null)
  }

  const handleStartPlanning = () => {
    if (!user) { openSignup(); return }
    setView('planner')
  }

  return (
    <div className="min-h-screen">
      {showAuthModal && <AuthModal />}
      {loading && <LoadingScreen />}

      {/* Trip History modal */}
      {showHistory && (
        <TripHistory
          onClose={() => setShowHistory(false)}
          onViewTrip={(data) => {
            setTripData(data)
            setView('result')
            setShowHistory(false)
          }}
        />
      )}
      {/* Analytics Dashboard modal */}
      {showDashboard && <Dashboard onClose={() => setShowDashboard(false)} />}

      {/* Landing page — no header */}
      {!loading && view === 'landing' && (
        <LandingPage onStartPlanning={handleStartPlanning} />
      )}

      {/* Planner / Result pages — with header */}
      {!loading && view !== 'landing' && (
        <>
          <Header
            onNewTrip={handleNewTrip}
            showNewTrip={view === 'result'}
            onHome={handleHome}
            onHistory={() => setShowHistory(true)}
            onDashboard={() => setShowDashboard(true)}
          />
          {view === 'planner' && (
            <TripForm onSubmit={handlePlanTrip} error={error} />
          )}
          {view === 'result' && tripData && (
            <ItineraryResult data={tripData} onNewTrip={handleNewTrip} />
          )}
          {/* If result but no data yet — stay on planner */}
          {view === 'result' && !tripData && (
            <TripForm onSubmit={handlePlanTrip} error={error || 'No itinerary data. Please try again.'} />
          )}
        </>
      )}
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}
