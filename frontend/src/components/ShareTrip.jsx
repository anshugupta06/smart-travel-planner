import { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../config'

export default function ShareTrip({ tripId, destination }) {
  const [shareUrl, setShareUrl]   = useState('')
  const [loading,  setLoading]    = useState(false)
  const [copied,   setCopied]     = useState(false)
  const [error,    setError]      = useState('')

  const handleShare = async () => {
    if (shareUrl) { copyUrl(); return }
    if (!tripId) {
      setError('Trip must be saved first. Generate an itinerary to enable sharing.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await axios.post(`${API_BASE}/api/history/${tripId}/share`)
      const url = `${window.location.origin}?share=${res.data.share_id}`
      setShareUrl(url)
      copyToClipboard(url)
    } catch {
      setError('Could not generate share link.')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (url) => {
    navigator.clipboard?.writeText(url || shareUrl).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2500)
    }).catch(() => {})
  }

  const copyUrl = () => copyToClipboard(shareUrl)

  return (
    <div className="p-4 rounded-2xl no-print"
      style={{ background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)' }}>
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-indigo-400 text-lg flex-shrink-0">🔗</span>
          <div className="min-w-0">
            <div className="text-white/70 text-sm font-semibold">Share this itinerary</div>
            {shareUrl ? (
              <div className="text-indigo-300/70 text-xs truncate max-w-xs mt-0.5">{shareUrl}</div>
            ) : (
              <div className="text-white/30 text-xs mt-0.5">Anyone with the link can view the plan</div>
            )}
            {error && <div className="text-red-400/80 text-xs mt-0.5">{error}</div>}
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {shareUrl && (
            <button
              onClick={copyUrl}
              className="text-xs px-3 py-2 rounded-xl font-bold transition-all"
              style={{
                background: copied ? 'rgba(52,211,153,0.15)' : 'rgba(99,102,241,0.15)',
                border: `1px solid ${copied ? 'rgba(52,211,153,0.3)' : 'rgba(99,102,241,0.3)'}`,
                color: copied ? '#34d399' : '#818cf8',
              }}
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
          )}
          <button
            onClick={handleShare}
            disabled={loading}
            className="text-xs px-4 py-2 rounded-xl font-black text-white transition-all hover:-translate-y-0.5 disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', boxShadow: '0 0 12px rgba(99,102,241,0.3)' }}
          >
            {loading ? '…' : shareUrl ? '🔄 New Link' : '🔗 Share'}
          </button>
        </div>
      </div>
    </div>
  )
}
