// Best Time to Visit — static data, no API needed
// peak = best weather, shoulder = okay, monsoon/winter = avoid or cold

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

const SEASON_STYLE = {
  peak:     { bg: 'rgba(52,211,153,0.2)',  border: 'rgba(52,211,153,0.4)',  text: '#34d399', label: 'Peak'     },
  shoulder: { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)',  text: '#f59e0b', label: 'Good'     },
  avoid:    { bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.25)',  text: '#f87171', label: 'Avoid'    },
  cool:     { bg: 'rgba(56,189,248,0.1)',  border: 'rgba(56,189,248,0.25)', text: '#38bdf8', label: 'Cool'     },
  hot:      { bg: 'rgba(251,146,60,0.15)', border: 'rgba(251,146,60,0.3)',  text: '#fb923c', label: 'Hot'      },
}

// Each destination: 12 entries (one per month) with season + note
// Format: [season, short_note]
const DESTINATION_DATA = {
  // ── Indian hill stations ──────────────────────────────────────────────
  shimla:     [['cool','Snow'],['cool','Snow'],['shoulder','Cold'],['shoulder','Pleasant'],['peak','Best'],['peak','Best'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['shoulder','Cold'],['cool','Snow']],
  manali:     [['cool','Snow'],['cool','Snow'],['shoulder','Cold'],['shoulder','Thaw'],['peak','Best'],['peak','Best'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['cool','Cold'],['cool','Snow']],
  mussoorie:  [['cool','Cold'],['cool','Cold'],['shoulder','Cool'],['peak','Best'],['peak','Best'],['shoulder','Pre-monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['shoulder','Cool'],['cool','Cold']],
  darjeeling: [['cool','Cold'],['shoulder','Warming'],['peak','Best'],['peak','Best'],['peak','Best'],['avoid','Monsoon'],['avoid','Heavy rain'],['avoid','Heavy rain'],['shoulder','Wet'],['peak','Best'],['shoulder','Pleasant'],['cool','Cold']],
  ooty:       [['shoulder','Cool'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['avoid','Rain'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['shoulder','Cool']],
  kodaikanal: [['shoulder','Cool'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['avoid','Rain'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['shoulder','Cool']],
  leh:        [['cool','Frozen'],['cool','Frozen'],['cool','Cold'],['shoulder','Thaw'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Cool'],['shoulder','Cold'],['cool','Closed'],['cool','Closed']],
  srinagar:   [['cool','Snow'],['cool','Snow'],['shoulder','Thaw'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['shoulder','Cold'],['cool','Snow']],
  // ── Beach & coastal ───────────────────────────────────────────────────
  goa:        [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['shoulder','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  'kanyakumari':[['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['shoulder','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['shoulder','Wet'],['peak','Best'],['peak','Best']],
  puri:       [['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Pre-monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  // ── Desert & Rajasthan ────────────────────────────────────────────────
  jaipur:     [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  jaisalmer:  [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  jodhpur:    [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  udaipur:    [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Post-rain'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  pushkar:    [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  // ── Heritage & spiritual ──────────────────────────────────────────────
  agra:       [['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['hot','Very hot'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Rain'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  varanasi:   [['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['hot','Very hot'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Rain'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  amritsar:   [['shoulder','Cold'],['shoulder','Cool'],['peak','Best'],['peak','Best'],['peak','Best'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['shoulder','Cold']],
  rishikesh:  [['shoulder','Cold'],['shoulder','Cool'],['peak','Best'],['peak','Best'],['peak','Best'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['shoulder','Cool'],['shoulder','Cold']],
  haridwar:   [['shoulder','Cold'],['shoulder','Cool'],['peak','Best'],['peak','Best'],['peak','Best'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['shoulder','Cool'],['shoulder','Cold']],
  // ── South India ───────────────────────────────────────────────────────
  munnar:     [['shoulder','Cool'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['shoulder','Pre-rain'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['shoulder','Cool']],
  coorg:      [['shoulder','Cool'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['shoulder','Pre-rain'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['shoulder','Cool']],
  mysore:     [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['shoulder','Warm'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  // ── International ─────────────────────────────────────────────────────
  dubai:      [['peak','Perfect'],['peak','Perfect'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['hot','Very hot'],['hot','Very hot'],['hot','Very hot'],['hot','Hot'],['shoulder','Warm'],['peak','Best'],['peak','Best']],
  bali:       [['peak','Dry'],['peak','Dry'],['shoulder','Good'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['avoid','Rain'],['avoid','Rain']],
  bangkok:    [['peak','Best'],['peak','Best'],['peak','Best'],['hot','Hot'],['avoid','Pre-monsoon'],['avoid','Rain'],['avoid','Rain'],['avoid','Rain'],['avoid','Rain'],['shoulder','Wet'],['peak','Best'],['peak','Best']],
  singapore:  [['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['shoulder','Wet'],['avoid','Wet'],['avoid','Wet']],
  paris:      [['cool','Cold'],['cool','Cold'],['shoulder','Cool'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Cool'],['shoulder','Cool'],['cool','Cold']],
  london:     [['cool','Cold'],['cool','Cold'],['shoulder','Cool'],['shoulder','Mild'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Mild'],['shoulder','Cool'],['cool','Rainy'],['cool','Cold']],
  tokyo:      [['cool','Cold'],['cool','Cold'],['peak','Cherry blossom'],['peak','Best'],['shoulder','Good'],['avoid','Rain'],['hot','Hot'],['hot','Hot'],['peak','Best'],['peak','Best'],['shoulder','Cool'],['cool','Cold']],
  'new york': [['cool','Cold'],['cool','Cold'],['shoulder','Cool'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Cool'],['shoulder','Cool'],['cool','Cold']],
  istanbul:   [['cool','Cold'],['cool','Cold'],['shoulder','Cool'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Mild'],['shoulder','Cool'],['cool','Cold']],
  // ── Indian metros ─────────────────────────────────────────────────────
  delhi:      [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Rain'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  mumbai:     [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Humid'],['avoid','Heavy rain'],['avoid','Heavy rain'],['avoid','Heavy rain'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  kolkata:    [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
  bangalore:  [['shoulder','Cool'],['shoulder','Warm'],['peak','Best'],['peak','Best'],['shoulder','Rain starts'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['shoulder','Cool']],
  chennai:    [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['shoulder','Rain'],['shoulder','Rain'],['shoulder','Rain'],['avoid','NE monsoon'],['avoid','NE monsoon'],['shoulder','Wet'],['peak','Best']],
  hyderabad:  [['peak','Best'],['peak','Best'],['peak','Best'],['shoulder','Warm'],['hot','Hot'],['avoid','Monsoon'],['avoid','Monsoon'],['avoid','Monsoon'],['shoulder','Wet'],['peak','Best'],['peak','Best'],['peak','Best']],
}

function getSeasonData(destination) {
  const key = destination.toLowerCase().trim()
  if (DESTINATION_DATA[key]) return DESTINATION_DATA[key]
  // Partial match
  for (const [k, v] of Object.entries(DESTINATION_DATA)) {
    if (key.includes(k) || k.includes(key)) return v
  }
  return null
}

export default function BestTimeCalendar({ destination }) {
  const data = getSeasonData(destination)
  if (!data) return null

  const peakCount     = data.filter(([s]) => s === 'peak').length
  const bestMonths    = MONTHS.filter((_, i) => data[i][0] === 'peak').join(', ')

  return (
    <div className="p-6 rounded-3xl"
      style={{ background: 'rgba(6,9,24,0.6)', border: '1px solid rgba(167,139,250,0.15)', backdropFilter: 'blur(20px)' }}>

      {/* Header */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <div className="inline-flex items-center gap-2 text-purple-400 text-xs font-black uppercase tracking-widest px-4 py-2 rounded-full mb-3"
            style={{ background: 'rgba(167,139,250,0.1)', border: '1px solid rgba(167,139,250,0.2)' }}>
            📅 Best Time to Visit
          </div>
          <h3 className="font-outfit font-black text-white text-2xl">{destination}</h3>
          {bestMonths && <p className="text-emerald-400/80 text-sm mt-1 font-medium">✦ Best months: {bestMonths}</p>}
        </div>
        <div className="text-right flex-shrink-0">
          <div className="font-outfit font-black text-3xl text-purple-300">{peakCount}</div>
          <div className="text-white/30 text-xs">peak months</div>
        </div>
      </div>

      {/* Month grid */}
      <div className="grid grid-cols-6 sm:grid-cols-12 gap-1.5 mb-5">
        {MONTHS.map((month, i) => {
          const [season, note] = data[i]
          const style = SEASON_STYLE[season] || SEASON_STYLE.shoulder
          return (
            <div key={month} className="flex flex-col items-center group">
              <div className="w-full rounded-xl py-4 flex flex-col items-center gap-1 transition-all hover:scale-105 cursor-default relative"
                style={{ background: style.bg, border: `1px solid ${style.border}` }}>
                <span className="text-[10px] font-black" style={{ color: style.text }}>{month}</span>
                {/* Tooltip on hover */}
                <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block z-10 whitespace-nowrap">
                  <div className="text-[10px] font-bold px-2 py-1 rounded-lg text-white"
                    style={{ background: 'rgba(6,9,24,0.95)', border: `1px solid ${style.border}` }}>
                    {note}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3">
        {Object.entries(SEASON_STYLE).map(([key, s]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm" style={{ background: s.bg, border: `1px solid ${s.border}` }} />
            <span className="text-white/40 text-xs font-medium">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
