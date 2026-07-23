import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../context/AuthContext'

// ── Replace with your Google OAuth Client ID ──────────────────────────────────
// Get it free at: console.cloud.google.com
//   1. Create project → APIs & Services → Credentials → Create OAuth Client ID
//   2. Application type: Web application
//   3. Authorized JS origins: http://localhost:5173
//   4. Copy the Client ID and paste below
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

export default function AuthModal() {
  const { authMode, setAuthMode, login, signup, loginWithGoogle, closeAuth } = useAuth()
  const [form, setForm]     = useState({ name: '', email: '', password: '', confirm: '' })
  const [error, setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const [gsiReady, setGsiReady] = useState(false)
  const googleBtnRef = useRef(null)

  const isLogin = authMode === 'login'

  // ── Initialise Google Identity Services ──────────────────────────────────────
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return

    const init = () => {
      if (!window.google?.accounts?.id) return
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: (response) => {
          if (response.credential) {
            loginWithGoogle(response.credential)
          }
        },
        auto_select: false,
        cancel_on_tap_outside: true,
      })
      setGsiReady(true)
    }

    // GSI script may already be loaded or still loading
    if (window.google?.accounts?.id) {
      init()
    } else {
      // Poll until the script loads (it's async defer)
      const timer = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(timer)
          init()
        }
      }, 100)
      return () => clearInterval(timer)
    }
  }, [loginWithGoogle])

  // Render the official Google button inside our container once GSI is ready
  useEffect(() => {
    if (!gsiReady || !googleBtnRef.current) return
    googleBtnRef.current.innerHTML = ''
    window.google.accounts.id.renderButton(googleBtnRef.current, {
      type:  'standard',
      theme: 'outline',
      size:  'large',
      text:  isLogin ? 'signin_with' : 'signup_with',
      shape: 'rectangular',
      logo_alignment: 'left',
      width: googleBtnRef.current.offsetWidth || 280,
    })
  }, [gsiReady, isLogin])

  // ── Form submit ──────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!form.email || !form.password) { setError('All fields are required'); return }
    if (!isLogin && form.password !== form.confirm) { setError('Passwords do not match'); return }
    if (!isLogin && !form.name) { setError('Name is required'); return }
    setLoading(true)
    await new Promise(r => setTimeout(r, 600))
    if (isLogin) login(form.email, form.name)
    else signup(form.email, form.name, form.password)
    setLoading(false)
  }

  const handle = (field, val) => setForm(p => ({ ...p, [field]: val }))

  const features = [
    { icon: '🗺️', text: 'AI-powered itineraries in seconds' },
    { icon: '📍', text: 'Real places, not fake suggestions' },
    { icon: '💰', text: 'Smart budget estimation' },
    { icon: '🌤️', text: 'Live weather integration' },
    { icon: '✈️', text: 'Routes for any city worldwide' },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={closeAuth}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      <div
        className="relative w-full max-w-4xl bg-white rounded-3xl overflow-hidden shadow-2xl flex"
        style={{ minHeight: '580px' }}
        onClick={e => e.stopPropagation()}
      >
        {/* ── Left panel — branding ── */}
        <div className="hidden md:flex flex-col justify-between w-5/12 gradient-hero text-white p-10">
          <div>
            <div className="flex items-center gap-3 mb-10">
              <span className="text-4xl float-anim">✈️</span>
              <div>
                <div className="font-black text-xl tracking-tight">Smart Travel</div>
                <div className="text-blue-200 text-xs font-medium">AI Planner</div>
              </div>
            </div>
            <h2 className="text-3xl font-black leading-tight mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Your Dream Trip,<br />Planned in Seconds
            </h2>
            <p className="text-blue-200 text-sm leading-relaxed">
              Join thousands of travelers using AI to create perfect, personalized itineraries.
            </p>
          </div>
          <div className="space-y-3">
            {features.map((f, i) => (
              <div key={i} className="flex items-center gap-3 glass rounded-xl px-4 py-3">
                <span className="text-xl">{f.icon}</span>
                <span className="text-sm font-medium text-white/90">{f.text}</span>
              </div>
            ))}
          </div>
          <div className="text-blue-200/60 text-xs">© 2025 Smart Travel Planner</div>
        </div>

        {/* ── Right panel — form ── */}
        <div className="flex-1 flex flex-col p-8 md:p-12 justify-center">
          <button
            onClick={closeAuth}
            className="absolute top-5 right-5 w-9 h-9 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-500 transition-colors text-lg"
          >✕</button>

          <div className="mb-8">
            <h3 className="text-3xl font-black text-gray-900 mb-1">
              {isLogin ? 'Welcome back! 👋' : 'Create account ✨'}
            </h3>
            <p className="text-gray-400 text-sm">
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <button
                onClick={() => { setAuthMode(isLogin ? 'signup' : 'login'); setError('') }}
                className="text-blue-600 font-semibold hover:underline"
              >
                {isLogin ? 'Sign up free' : 'Sign in'}
              </button>
            </p>
          </div>

          {/* ── Google Sign-In ─── */}
          <div className="mb-5">
            {GOOGLE_CLIENT_ID ? (
              <div>
                {/* Official Google button rendered by GSI */}
                <div ref={googleBtnRef} className="w-full flex justify-center" />
                {!gsiReady && (
                  <div className="w-full flex items-center justify-center gap-2 py-3 border-2 border-gray-200 rounded-xl text-sm font-semibold text-gray-500">
                    <span className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                    Loading Google Sign-In…
                  </div>
                )}
              </div>
            ) : (
              /* Fallback when no Client ID is configured — shows a styled button
                 that opens Google's accounts page (best we can do without a key) */
              <button
                type="button"
                onClick={() => {
                  // Without a Client ID we can't do real OAuth.
                  // Show a clear message instead of silently logging in as a fake user.
                  setError('Google Sign-In requires a Client ID. See .env.example for setup instructions, or use email/password below.')
                }}
                className="w-full flex items-center justify-center gap-3 py-3 border-2 border-gray-200 rounded-xl hover:border-gray-300 hover:bg-gray-50 transition-all text-sm font-semibold text-gray-700"
              >
                <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </button>
            )}
          </div>

          <div className="flex items-center gap-3 mb-5">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-gray-400 text-xs font-medium">or use email</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>

          {/* ── Email / Password form ── */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Full Name</label>
                <input className="auth-input" placeholder="John Doe" value={form.name} onChange={e => handle('name', e.target.value)} />
              </div>
            )}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Email Address</label>
              <input type="email" className="auth-input" placeholder="you@gmail.com" value={form.email} onChange={e => handle('email', e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Password</label>
              <input type="password" className="auth-input" placeholder="••••••••" value={form.password} onChange={e => handle('password', e.target.value)} />
            </div>
            {!isLogin && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Confirm Password</label>
                <input type="password" className="auth-input" placeholder="••••••••" value={form.confirm} onChange={e => handle('confirm', e.target.value)} />
              </div>
            )}

            {isLogin && (
              <div className="text-right">
                <button type="button" className="text-sm text-blue-600 hover:underline font-medium">Forgot password?</button>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl px-4 py-3 flex items-start gap-2">
                <span className="mt-0.5 flex-shrink-0">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <button type="submit" disabled={loading} className="w-full btn-primary text-base py-4 mt-2">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {isLogin ? 'Signing in...' : 'Creating account...'}
                </span>
              ) : (
                isLogin ? '🚀 Sign In' : '✨ Create Account'
              )}
            </button>
          </form>

          {/* Guest access */}
          <button
            type="button"
            onClick={() => login('guest@demo.com', 'Guest Explorer')}
            className="mt-4 w-full flex items-center justify-center gap-2 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all text-sm font-medium text-gray-500"
          >
            <span>👤</span> Continue as Guest
          </button>

          <p className="text-center text-xs text-gray-400 mt-5">
            By continuing, you agree to our{' '}
            <span className="text-blue-500 cursor-pointer hover:underline">Terms</span> &{' '}
            <span className="text-blue-500 cursor-pointer hover:underline">Privacy Policy</span>
          </p>
        </div>
      </div>
    </div>
  )
}
