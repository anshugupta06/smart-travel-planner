import { useState, useEffect } from 'react'

// Static approximate exchange rates from INR (updated periodically)
// No API key needed — these are good enough for travel budgeting
const RATES = {
  USD: 0.012, EUR: 0.011, GBP: 0.0094, AED: 0.044, SGD: 0.016,
  THB: 0.42,  JPY: 1.84,  AUD: 0.018,  CAD: 0.016, CHF: 0.011,
  MYR: 0.056, IDR: 195,   NPR: 1.6,    LKR: 3.7,   BDT: 1.32,
  PKR: 3.35,  KWD: 0.0037,SAR: 0.045,  QAR: 0.044, OMR: 0.0046,
}

const FLAG = {
  USD: '🇺🇸', EUR: '🇪🇺', GBP: '🇬🇧', AED: '🇦🇪', SGD: '🇸🇬',
  THB: '🇹🇭', JPY: '🇯🇵', AUD: '🇦🇺', CAD: '🇨🇦', CHF: '🇨🇭',
  MYR: '🇲🇾', IDR: '🇮🇩', NPR: '🇳🇵', LKR: '🇱🇰', BDT: '🇧🇩',
  PKR: '🇵🇰', KWD: '🇰🇼', SAR: '🇸🇦', QAR: '🇶🇦', OMR: '🇴🇲',
}

// Map destination keywords to most relevant currencies
function guessCurrency(destination) {
  const d = destination.toLowerCase()
  if (/dubai|uae|abu dhabi/.test(d)) return 'AED'
  if (/singapore/.test(d))           return 'SGD'
  if (/bangkok|thailand|phuket/.test(d)) return 'THB'
  if (/japan|tokyo|osaka/.test(d))   return 'JPY'
  if (/bali|indonesia/.test(d))      return 'IDR'
  if (/malaysia|kuala lumpur/.test(d)) return 'MYR'
  if (/uk|london|england/.test(d))   return 'GBP'
  if (/paris|france|europe|italy|spain|germany/.test(d)) return 'EUR'
  if (/australia|sydney|melbourne/.test(d)) return 'AUD'
  if (/nepal|kathmandu/.test(d))     return 'NPR'
  if (/sri lanka|colombo/.test(d))   return 'LKR'
  if (/usa|new york|los angeles|america/.test(d)) return 'USD'
  if (/canada|toronto/.test(d))      return 'CAD'
  if (/saudi|riyadh/.test(d))        return 'SAR'
  if (/qatar|doha/.test(d))          return 'QAR'
  if (/oman|muscat/.test(d))         return 'OMR'
  if (/kuwait/.test(d))              return 'KWD'
  return null  // domestic India trip — no widget needed
}

const SHOW_CURRENCIES = ['USD', 'EUR', 'GBP', 'AED', 'SGD', 'THB', 'JPY', 'AUD']

function fmt(n, currency) {
  if (n >= 1000) return `${currency} ${(n / 1000).toFixed(1)}k`
  return `${currency} ${n.toFixed(n < 10 ? 2 : 0)}`
}

export default function CurrencyWidget({ budgetINR, destination }) {
  const [expanded, setExpanded] = useState(false)
  const suggestedCurrency = guessCurrency(destination)

  // For domestic India trips, don't show the widget
  if (!suggestedCurrency && !expanded) return null

  const displayCurrencies = suggestedCurrency
    ? [suggestedCurrency, ...SHOW_CURRENCIES.filter(c => c !== suggestedCurrency)].slice(0, expanded ? 12 : 4)
    : SHOW_CURRENCIES.slice(0, expanded ? 12 : 4)

  return (
    <div className="p-6 rounded-3xl"
      style={{ background: 'rgba(6,9,24,0.6)', border: '1px solid rgba(56,189,248,0.15)', backdropFilter: 'blur(20px)' }}>

      <div className="flex items-center justify-between mb-4">
        <div className="inline-flex items-center gap-2 text-sky-400 text-xs font-black uppercase tracking-widest px-4 py-2 rounded-full"
          style={{ background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.2)' }}>
          💱 Currency Converter
        </div>
        <div className="text-white/30 text-xs">Base: ₹{Number(budgetINR).toLocaleString('en-IN')}</div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {displayCurrencies.map(currency => {
          const rate      = RATES[currency]
          const converted = budgetINR * rate
          const isMain    = currency === suggestedCurrency
          return (
            <div key={currency}
              className="p-3.5 rounded-2xl text-center transition-all"
              style={{
                background: isMain ? 'rgba(56,189,248,0.1)' : 'rgba(255,255,255,0.04)',
                border: isMain ? '1px solid rgba(56,189,248,0.3)' : '1px solid rgba(255,255,255,0.07)',
              }}>
              <div className="text-xl mb-1">{FLAG[currency]}</div>
              <div className="font-outfit font-black text-white text-base leading-none">{fmt(converted, currency)}</div>
              <div className="text-white/35 text-[10px] mt-1 font-medium">{currency}</div>
              {isMain && <div className="text-sky-400 text-[9px] font-black mt-1">✦ Local currency</div>}
            </div>
          )
        })}
      </div>

      <button
        onClick={() => setExpanded(e => !e)}
        className="mt-4 w-full text-xs text-white/30 hover:text-white/60 transition-colors font-medium"
      >
        {expanded ? '↑ Show less' : `↓ Show all ${Object.keys(RATES).length} currencies`}
      </button>

      <p className="text-white/20 text-[10px] text-center mt-2">
        Approximate rates · For reference only · Check bank for exact rates
      </p>
    </div>
  )
}
