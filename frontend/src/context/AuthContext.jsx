import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext(null)

// ── Storage key for registered accounts ──────────────────────────────────────
const ACCOUNTS_KEY = 'stp_accounts'   // persists in localStorage (survives browser close)
const SESSION_KEY  = 'stp_user'       // sessionStorage (clears on browser close)

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

// ── Simple password hash (not cryptographic — frontend only) ─────────────────
function hashPassword(password) {
  let hash = 0
  for (let i = 0; i < password.length; i++) {
    hash = ((hash << 5) - hash) + password.charCodeAt(i)
    hash |= 0
  }
  return hash.toString(36)
}

// ── Account store helpers ─────────────────────────────────────────────────────
function getAccounts() {
  try { return JSON.parse(localStorage.getItem(ACCOUNTS_KEY) || '{}') } catch { return {} }
}
function saveAccounts(accounts) {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts))
}

export function AuthProvider({ children }) {
  const [user, setUser]                   = useState(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode]           = useState('login')

  const [onLoginNav,  setOnLoginNav]  = useState(null)
  const [onLogoutNav, setOnLogoutNav] = useState(null)

  // Restore session on page refresh (within same tab session)
  useEffect(() => {
    const saved = sessionStorage.getItem(SESSION_KEY)
    if (saved) {
      try { setUser(JSON.parse(saved)) } catch {}
    }
  }, [])

  // Wrap callbacks in objects so React doesn't treat them as updater functions
  const registerNav = useCallback((loginCb, logoutCb) => {
    setOnLoginNav({ fn: loginCb })
    setOnLogoutNav({ fn: logoutCb })
  }, [])

  const _saveAndNavigate = (u) => {
    setUser(u)
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(u))
    setShowAuthModal(false)
    onLoginNav?.fn?.()
  }

  // ── SIGNUP — creates a new account, rejects duplicate email ──────────────────
  const signup = (email, name, password) => {
    const accounts = getAccounts()
    const key = email.toLowerCase().trim()

    if (accounts[key]) {
      return { error: 'An account with this email already exists. Please sign in.' }
    }

    const u = {
      email: key,
      name:  name || key.split('@')[0],
      avatar: (name || key)[0].toUpperCase(),
      provider: 'email',
    }

    // Save account to persistent store
    accounts[key] = { name: u.name, passwordHash: hashPassword(password) }
    saveAccounts(accounts)

    _saveAndNavigate(u)
    return { error: null }
  }

  // ── LOGIN — only allows registered accounts ───────────────────────────────────
  const login = (email, _name, password) => {
    // Guest bypass (no password check)
    if (email === 'guest@demo.com') {
      _saveAndNavigate({
        email: 'guest@demo.com',
        name: 'Guest Explorer',
        avatar: '👤',
        provider: 'guest',
      })
      return { error: null }
    }

    const accounts = getAccounts()
    const key = email.toLowerCase().trim()
    const account = accounts[key]

    if (!account) {
      return { error: 'No account found with this email. Please sign up first.' }
    }

    if (account.passwordHash !== hashPassword(password || '')) {
      return { error: 'Incorrect password. Please try again.' }
    }

    _saveAndNavigate({
      email: key,
      name:  account.name,
      avatar: account.name[0].toUpperCase(),
      provider: 'email',
    })
    return { error: null }
  }

  // ── Google login — always allowed (creates account on first use) ──────────────
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

    // Auto-register Google users in account store so they can be recognized
    const accounts = getAccounts()
    const key = payload.email.toLowerCase()
    if (!accounts[key]) {
      accounts[key] = { name: payload.name, provider: 'google', googleId: payload.sub }
      saveAccounts(accounts)
    }

    _saveAndNavigate(u)
  }

  const logout = () => {
    setUser(null)
    sessionStorage.removeItem(SESSION_KEY)
    if (window.google?.accounts?.id) {
      window.google.accounts.id.disableAutoSelect()
    }
    onLogoutNav?.fn?.()
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
