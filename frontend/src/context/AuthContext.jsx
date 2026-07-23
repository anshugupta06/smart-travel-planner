import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext(null)

// ── JWT decoder for Google credential ────────────────────────────────────────
function parseGoogleJWT(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(json)
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [user, setUser]               = useState(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode]       = useState('login')

  // Navigation callbacks injected by AppContent
  const [onLoginNav,  setOnLoginNav]  = useState(null)
  const [onLogoutNav, setOnLogoutNav] = useState(null)

  useEffect(() => {
    const saved = localStorage.getItem('stp_user')
    if (saved) {
      try { setUser(JSON.parse(saved)) } catch {}
    }
  }, [])

  // Register navigation callbacks from App
  const registerNav = useCallback((loginCb, logoutCb) => {
    setOnLoginNav(() => loginCb)
    setOnLogoutNav(() => logoutCb)
  }, [])

  const _saveAndNavigate = (u) => {
    setUser(u)
    localStorage.setItem('stp_user', JSON.stringify(u))
    setShowAuthModal(false)
    // Navigate to planner after login
    onLoginNav?.()
  }

  const login = (email, name) => {
    const u = {
      email,
      name: name || email.split('@')[0],
      avatar: (name || email)[0].toUpperCase(),
      provider: 'email',
    }
    _saveAndNavigate(u)
  }

  const signup = (email, name) => login(email, name)

  const loginWithGoogle = (credentialJWT) => {
    const payload = parseGoogleJWT(credentialJWT)
    if (!payload) return
    const u = {
      email:    payload.email,
      name:     payload.name,
      avatar:   payload.picture || payload.name?.[0]?.toUpperCase() || 'G',
      provider: 'google',
      googleId: payload.sub,
    }
    _saveAndNavigate(u)
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('stp_user')
    if (window.google?.accounts?.id) {
      window.google.accounts.id.disableAutoSelect()
    }
    // Navigate to landing after logout
    onLogoutNav?.()
  }

  const openLogin  = () => { setAuthMode('login');  setShowAuthModal(true) }
  const openSignup = () => { setAuthMode('signup'); setShowAuthModal(true) }
  const closeAuth  = () => setShowAuthModal(false)

  return (
    <AuthContext.Provider value={{
      user, login, signup, loginWithGoogle, logout,
      showAuthModal, authMode, setAuthMode,
      openLogin, openSignup, closeAuth,
      registerNav,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
