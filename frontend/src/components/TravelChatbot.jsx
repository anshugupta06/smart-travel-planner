import { useState, useRef, useEffect } from 'react'
import { API_BASE } from '../config'

const QUICK_PROMPTS = [
  '🏨 Hotel prices here?',
  '🚆 Transport options?',
  '🍽️ Local food to try?',
  '🎟️ Attraction entry fees?',
  '💡 Budget saving tips?',
  '🌤️ Best time to visit?',
  '🛺 Local transport options?',
  '🛍️ Shopping spots?',
]

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5 px-5 py-4">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-2.5 h-2.5 rounded-full bg-amber-400/70"
          style={{ animation: `typingBounce 1.2s ease-in-out ${i * 0.2}s infinite` }}
        />
      ))}
    </div>
  )
}

// Render markdown-style bold (**text**) and bullet/numbered lines
function MessageContent({ text }) {
  const lines = text.split('\n').filter((l, i, arr) => !(l.trim() === '' && arr[i - 1]?.trim() === ''))
  return (
    <div className="space-y-1">
      {lines.map((line, i) => {
        const trimmed = line.trim()
        const isBullet = /^[-*•]\s/.test(trimmed)
        const isNumbered = /^\d+[.)]\s/.test(trimmed)
        const content = trimmed.replace(/^[-*•]\s/, '').replace(/^\d+[.)]\s/, '')

        // Bold rendering
        const renderBold = (str) =>
          str.split(/\*\*(.*?)\*\*/g).map((part, j) =>
            j % 2 === 1
              ? <strong key={j} className="text-amber-300 font-bold">{part}</strong>
              : <span key={j}>{part}</span>
          )

        if (isBullet || isNumbered) {
          return (
            <div key={i} className="flex items-start gap-2.5">
              <span className="text-amber-400 font-bold text-sm flex-shrink-0 mt-0.5">
                {isBullet ? '▸' : trimmed.match(/^(\d+[.)])/)?.[1]}
              </span>
              <span className="leading-relaxed">{renderBold(content)}</span>
            </div>
          )
        }

        if (trimmed === '') return <div key={i} className="h-1" />

        return (
          <div key={i} className="leading-relaxed">
            {renderBold(trimmed)}
          </div>
        )
      })}
    </div>
  )
}

export default function TravelChatbot({ tripData }) {
  const { destination, origin, days, budget_provided, travel_type, num_people } = tripData || {}

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hey! I'm your travel assistant for **${destination || 'your trip'}**. Ask me anything — hotel prices, transport fares, local food, attractions, or packing tips! 🌍`,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [llmStatus, setLlmStatus] = useState(null) // null | 'ok' | 'error'
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  // Check LLM health on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/chat/health`)
      .then(r => r.json())
      .then(d => {
        const ok = d.groq_ready || d.gemini_ready
        setLlmStatus(ok ? 'ok' : 'degraded')
        console.log('[ChatBot] health:', d)
      })
      .catch(() => setLlmStatus('error'))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text) => {
    const userText = (text || input).trim()
    if (!userText || loading) return

    const newHistory = [...messages, { role: 'user', content: userText }]
    setMessages(newHistory)
    setInput('')
    setLoading(true)

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          destination,
          origin,
          days,
          budget: budget_provided,
          travel_type,
          num_people,
          history: messages.slice(-8).map(m => ({ role: m.role, content: m.content })),
        }),
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
      setLlmStatus('ok')
    } catch (err) {
      console.error('[ChatBot] fetch error:', err)
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ The backend server isn't responding. Make sure it's running:\n\`cd backend\`\n\`python -m uvicorn main:app --reload\`\n\nThen also verify your GROQ_API_KEY and GEMINI_API_KEY in the .env file are valid.`,
        },
      ])
      setLlmStatus('error')
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const statusDot = {
    ok: { color: '#34d399', shadow: '#34d399', label: 'AI Ready' },
    degraded: { color: '#f59e0b', shadow: '#f59e0b', label: 'Limited' },
    error: { color: '#f87171', shadow: '#f87171', label: 'Offline' },
    null: { color: '#6b7280', shadow: '#6b7280', label: 'Checking…' },
  }[llmStatus]

  return (
    <div
      className="flex flex-col h-full rounded-3xl overflow-hidden"
      style={{
        background: 'rgba(6,9,24,0.82)',
        border: '1px solid rgba(245,158,11,0.2)',
        backdropFilter: 'blur(28px)',
        boxShadow: '0 0 80px rgba(245,158,11,0.07), inset 0 1px 0 rgba(255,255,255,0.05)',
      }}
    >
      {/* ── Header ─────────────────────────────────────────────── */}
      <div
        className="px-6 py-5 flex items-center gap-4 flex-shrink-0"
        style={{
          background: 'linear-gradient(135deg, rgba(245,158,11,0.1), rgba(234,88,12,0.06))',
          borderBottom: '1px solid rgba(245,158,11,0.15)',
        }}
      >
        <div
          className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0"
          style={{
            background: 'linear-gradient(135deg,#f59e0b,#ea580c)',
            boxShadow: '0 0 20px rgba(245,158,11,0.4)',
          }}
        >
          🤖
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-outfit font-black text-white text-base leading-tight">
            Travel Assistant
          </div>
          <div className="text-amber-400/60 text-xs mt-0.5 truncate">
            Expert guide for {destination || 'your trip'}
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span
            className="w-2.5 h-2.5 rounded-full flex-shrink-0"
            style={{ background: statusDot.color, boxShadow: `0 0 8px ${statusDot.shadow}` }}
          />
          <span className="text-xs font-semibold" style={{ color: statusDot.color }}>
            {statusDot.label}
          </span>
        </div>
      </div>

      {/* ── Messages ───────────────────────────────────────────── */}
      <div
        className="flex-1 overflow-y-auto px-5 py-5 space-y-4"
        style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(245,158,11,0.2) transparent' }}
      >
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} gap-3`}>
            {msg.role === 'assistant' && (
              <div
                className="w-8 h-8 rounded-xl flex items-center justify-center text-base flex-shrink-0 mt-0.5"
                style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 2px 8px rgba(245,158,11,0.3)' }}
              >
                🤖
              </div>
            )}

            <div
              className={`px-5 py-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'rounded-tr-sm text-white font-medium'
                  : 'rounded-tl-sm text-white/85'
              }`}
              style={{
                maxWidth: '85%',
                ...(msg.role === 'user'
                  ? {
                      background: 'linear-gradient(135deg,#f59e0b,#ea580c)',
                      boxShadow: '0 4px 20px rgba(245,158,11,0.3)',
                    }
                  : {
                      background: 'rgba(255,255,255,0.06)',
                      border: '1px solid rgba(255,255,255,0.08)',
                    }),
              }}
            >
              {msg.role === 'assistant'
                ? <MessageContent text={msg.content} />
                : msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start gap-3">
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center text-base flex-shrink-0 mt-0.5"
              style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}
            >
              🤖
            </div>
            <div
              className="rounded-2xl rounded-tl-sm"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              <TypingDots />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── Quick prompts ──────────────────────────────────────── */}
      <div
        className="px-5 pt-3 pb-2 flex-shrink-0"
        style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
      >
        <p className="text-white/25 text-[10px] uppercase tracking-widest font-bold mb-2">Quick ask</p>
        <div
          className="flex gap-2 overflow-x-auto pb-1"
          style={{ scrollbarWidth: 'none' }}
        >
          {QUICK_PROMPTS.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              disabled={loading}
              className="flex-shrink-0 text-xs px-3.5 py-2 rounded-full font-semibold text-amber-300/80 hover:text-white hover:bg-amber-500/15 transition-all hover:-translate-y-0.5 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background: 'rgba(245,158,11,0.07)',
                border: '1px solid rgba(245,158,11,0.18)',
                whiteSpace: 'nowrap',
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* ── Input ─────────────────────────────────────────────── */}
      <div className="px-5 pb-5 pt-2 flex-shrink-0">
        <div
          className="flex items-end gap-3 p-3 rounded-2xl"
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: `1px solid ${llmStatus === 'error' ? 'rgba(248,113,113,0.3)' : 'rgba(245,158,11,0.22)'}`,
            transition: 'border-color 0.2s',
          }}
        >
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={e => {
              setInput(e.target.value)
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
            }}
            onKeyDown={handleKey}
            placeholder={`Ask about ${destination || 'your trip'}…`}
            disabled={loading}
            className="flex-1 bg-transparent text-white/90 text-sm placeholder-white/25 outline-none resize-none leading-relaxed px-2 py-1.5"
            style={{ fontFamily: 'inherit', minHeight: '38px' }}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all hover:scale-105 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed"
            style={{
              background: !input.trim() || loading
                ? 'rgba(245,158,11,0.15)'
                : 'linear-gradient(135deg,#f59e0b,#ea580c)',
              boxShadow: !input.trim() || loading ? 'none' : '0 0 16px rgba(245,158,11,0.45)',
            }}
          >
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <p className="text-center text-white/15 text-[10px] mt-2">
          Shift+Enter for new line · Enter to send
        </p>
      </div>

      <style>{`
        @keyframes typingBounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
          30% { transform: translateY(-7px); opacity: 1; }
        }
        .scrollbar-none::-webkit-scrollbar { display: none; }
      `}</style>
    </div>
  )
}
