const fmt  = (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`
const fmtK = (n) => n >= 1000 ? `₹${(n / 1000).toFixed(1)}k` : fmt(n)

// Line items shown in the breakdown
const LINE_ITEMS = [
  { key: 'intercity_transport', label: 'Intercity Transport', emoji: '✈️', from: '#f59e0b', to: '#ea580c' },
  { key: 'accommodation',       label: 'Accommodation',       emoji: '🏨', from: '#3b82f6', to: '#06b6d4' },
  { key: 'food',                label: 'Food & Dining',        emoji: '🍽️', from: '#10b981', to: '#34d399' },
  { key: 'local_transport',     label: 'Local Transport',      emoji: '🚕', from: '#0891b2', to: '#6366f1' },
  { key: 'activities',          label: 'Activities & Entry',   emoji: '🎟️', from: '#8b5cf6', to: '#ec4899' },
  { key: 'misc',                label: 'Miscellaneous',        emoji: '🛍️', from: '#f43f5e', to: '#f97316' },
]

const DAILY_ITEMS = [
  { key: 'breakfast',       label: 'Breakfast',        emoji: '☕' },
  { key: 'lunch',           label: 'Lunch',             emoji: '🍛' },
  { key: 'dinner',          label: 'Dinner',            emoji: '🍽️' },
  { key: 'local_transport', label: 'Local Transport',   emoji: '🚕' },
  { key: 'entry_tickets',   label: 'Entry Tickets',     emoji: '🎟️' },
  { key: 'shopping',        label: 'Shopping',          emoji: '🛍️' },
  { key: 'misc',            label: 'Miscellaneous',     emoji: '🧾' },
]

function TransportOptions({ options }) {
  if (!options?.length) return null
  return (
    <div className="mb-8">
      <p className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest mb-4">🚗 Transport Options</p>
      <div className="space-y-2">
        {options.map((opt, i) => (
          <div key={i} className="flex items-center gap-3 p-3.5 rounded-2xl transition-all"
            style={{
              background: opt.recommended ? 'rgba(245,158,11,0.07)' : 'rgba(255,255,255,0.03)',
              border: opt.recommended ? '1px solid rgba(245,158,11,0.3)' : '1px solid rgba(255,255,255,0.07)',
            }}>
            {opt.recommended && (
              <div className="absolute -top-1.5 -right-1.5 text-[9px] font-black px-2 py-0.5 rounded-full text-white"
                style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>★ Best</div>
            )}
            <span className="text-xl">{opt.emoji}</span>
            <div className="flex-1 min-w-0">
              <div className="font-black text-white text-sm">{opt.mode}</div>
              <div className="text-white/35 text-xs">⏱ {opt.duration}</div>
            </div>
            <div className="text-right shrink-0">
              <div className="font-black text-amber-300 text-sm">
                {opt.fare_label || fmt(opt.cost_per_person)}
              </div>
              <div className="text-white/30 text-xs">per person</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function BudgetFitBanner({ fit }) {
  if (!fit) return null
  const { fits_budget, recommendation, adjustments_made, utilization_pct,
          savings, upgrade_plan, adjusted_estimate, original_estimate, budget_provided } = fit
  return (
    <div className="mb-7 rounded-3xl overflow-hidden"
      style={{ border: fits_budget ? '1px solid rgba(52,211,153,0.3)' : '1px solid rgba(251,146,60,0.3)' }}>
      <div className="px-6 py-4 flex items-center gap-3"
        style={{ background: fits_budget ? 'rgba(52,211,153,0.08)' : 'rgba(251,146,60,0.08)' }}>
        <span className="text-3xl">{fits_budget ? '🎉' : '⚡'}</span>
        <div className="flex-1">
          <div className="font-outfit font-black text-white text-lg">
            {fits_budget ? 'Trip fits your budget!' : 'Trip optimized for your budget'}
          </div>
          <div className="text-sm font-medium mt-0.5"
            style={{ color: fits_budget ? '#34d399' : '#fb923c' }}>
            {fits_budget
              ? `${utilization_pct}% utilized · ${fmt(savings)} to spare`
              : `Reduced from ${fmt(original_estimate)} → ${fmt(adjusted_estimate)}`}
          </div>
        </div>
      </div>
      <div className="px-6 py-4" style={{ background: 'rgba(6,9,24,0.5)' }}>
        <p className="text-white/55 text-sm leading-relaxed mb-4">{recommendation}</p>
        {!fits_budget && adjustments_made?.length > 0 && (
          <div className="space-y-2 mb-4">
            <p className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest">✂️ How we fit it</p>
            {adjustments_made.map((adj, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-2xl"
                style={{ background: 'rgba(251,146,60,0.06)', border: '1px solid rgba(251,146,60,0.12)' }}>
                <span className="text-lg shrink-0">{adj.icon || '→'}</span>
                <span className="text-white/60 text-sm flex-1">{adj.text}</span>
                {adj.saves > 0 && (
                  <span className="text-xs font-black px-2.5 py-1 rounded-full"
                    style={{ background: 'rgba(52,211,153,0.15)', color: '#34d399' }}>
                    −{fmt(adj.saves)}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
        {upgrade_plan?.extra_budget_needed > 0 && (
          <div className="rounded-2xl overflow-hidden" style={{ border: '1px solid rgba(245,158,11,0.2)' }}>
            <div className="px-5 py-3 flex items-center gap-3" style={{ background: 'rgba(245,158,11,0.08)' }}>
              <span className="text-2xl">🚀</span>
              <div>
                <div className="font-outfit font-black text-white text-sm">Want the full experience?</div>
                <div className="text-amber-300 text-xs font-bold mt-0.5">
                  Add {fmt(upgrade_plan.extra_budget_needed)} → total {fmt(upgrade_plan.total_with_upgrade)}
                </div>
              </div>
            </div>
            <div className="px-5 py-3 space-y-2" style={{ background: 'rgba(6,9,24,0.4)' }}>
              {upgrade_plan.items?.map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
                  <span className="text-white/55 text-xs flex-1">{item.benefit}</span>
                  <span className="font-black text-amber-300 text-xs">+{fmt(item.cost)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function BudgetCard({ budget, numPeople, budgetProvided, transportOptions }) {
  const total           = budget.total_estimated || 0
  const totalMin        = budget.total_min || Math.round(total * 0.85)
  const totalMax        = budget.total_max || Math.round(total * 1.25)
  const originalBudget  = budget.original_budget || budgetProvided || 0
  const remaining       = budget.remaining_budget ?? Math.round(originalBudget - total)
  const overBudget      = budget.over_budget ?? (total > originalBudget)
  const pct             = originalBudget > 0 ? Math.min(Math.round((total / originalBudget) * 100), 120) : 0
  const daily           = budget.daily_breakdown

  return (
    <div className="p-8 rounded-3xl relative overflow-hidden"
      style={{ background: 'rgba(6,9,24,0.7)', border: '1px solid rgba(245,158,11,0.1)', backdropFilter: 'blur(16px)' }}>
      <div className="absolute -top-16 -right-16 w-64 h-64 rounded-full blur-3xl opacity-10 pointer-events-none"
        style={{ background: 'radial-gradient(circle,#f59e0b,transparent)' }} />

      <div className="relative z-10">
        {/* Header */}
        <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-black uppercase tracking-widest px-4 py-2 rounded-full mb-3"
          style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
          💰 Full Trip Cost Breakdown
        </div>
        <h2 className="font-outfit font-black text-white text-3xl mb-6">
          Budget for {numPeople} Traveler{numPeople > 1 ? 's' : ''}
        </h2>

        <BudgetFitBanner fit={budget.budget_fit} />
        <TransportOptions options={transportOptions} />

        {/* ── Min / Estimated / Max row ──────────────────────────── */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          {[
            { label: 'Minimum',   val: totalMin,  color: '#34d399', bg: 'rgba(52,211,153,0.07)',  border: 'rgba(52,211,153,0.2)' },
            { label: 'Estimated', val: total,     color: '#f59e0b', bg: 'rgba(245,158,11,0.07)', border: 'rgba(245,158,11,0.25)' },
            { label: 'Maximum',   val: totalMax,  color: '#f87171', bg: 'rgba(239,68,68,0.07)',  border: 'rgba(239,68,68,0.2)' },
          ].map(s => (
            <div key={s.label} className="rounded-2xl p-4 text-center"
              style={{ background: s.bg, border: `1px solid ${s.border}` }}>
              <p className="text-[10px] font-black text-white/35 uppercase tracking-widest mb-1">{s.label}</p>
              <p className="font-outfit font-black text-xl leading-tight" style={{ color: s.color }}>{fmtK(s.val)}</p>
            </div>
          ))}
        </div>

        {/* ── Your budget vs total ───────────────────────────────── */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="rounded-2xl p-4 text-center"
            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
            <p className="text-[10px] font-black text-white/35 uppercase tracking-widest mb-1">Your Budget</p>
            <p className="font-outfit font-black text-white text-2xl">{fmt(originalBudget)}</p>
          </div>
          <div className="rounded-2xl p-4 text-center"
            style={{
              background: overBudget ? 'rgba(239,68,68,0.07)' : 'rgba(52,211,153,0.06)',
              border: overBudget ? '1px solid rgba(239,68,68,0.22)' : '1px solid rgba(52,211,153,0.22)',
            }}>
            <p className="text-[10px] font-black text-white/35 uppercase tracking-widest mb-1">
              {overBudget ? 'Over Budget' : 'Remaining'}
            </p>
            <p className="font-outfit font-black text-2xl"
              style={{ color: overBudget ? '#f87171' : '#34d399' }}>
              {fmt(Math.abs(remaining))}
            </p>
          </div>
        </div>

        {/* Utilisation bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm font-bold mb-2">
            <span className="text-white/40">Budget utilisation</span>
            <span style={{ color: overBudget ? '#f87171' : '#34d399' }}>{pct}%</span>
          </div>
          <div className="h-3 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
            <div className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${Math.min(pct, 100)}%`,
                background: overBudget ? 'linear-gradient(90deg,#ef4444,#f97316)' : 'linear-gradient(90deg,#10b981,#34d399)',
              }} />
          </div>
          <div className="text-sm font-bold mt-2" style={{ color: overBudget ? '#f87171' : '#34d399' }}>
            {overBudget ? `⚠️ ${fmt(Math.abs(remaining))} over budget` : `✅ ${fmt(remaining)} under budget`}
          </div>
        </div>

        {/* ── Detailed line-item breakdown ───────────────────────── */}
        <div className="mb-2">
          <p className="text-[10px] font-black text-white/35 uppercase tracking-widest mb-4">Detailed Cost Breakdown</p>
          <div className="space-y-4">
            {LINE_ITEMS.map(item => {
              const val = budget[item.key] || 0
              const p   = total > 0 ? Math.round((val / total) * 100) : 0
              if (val === 0) return null

              // Sub-label: show transport mode or hotel name if available
              let subLabel = ''
              if (item.key === 'intercity_transport') {
                subLabel = budget.intercity_transport_mode || ''
                const src = budget.intercity_transport_label || 'Estimated'
                if (subLabel) subLabel = `${subLabel} · ${src}`
              } else if (item.key === 'accommodation' && budget.hotel_name) {
                subLabel = `${budget.hotel_name} · ${budget.hotel_cost_source || 'Estimated'}`
              }

              return (
                <div key={item.key}>
                  <div className="flex justify-between items-start mb-1.5">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-base">{item.emoji}</span>
                        <span className="text-sm font-semibold text-white/55">{item.label}</span>
                        <span className="text-xs text-white/20">{p}%</span>
                      </div>
                      {subLabel && (
                        <p className="text-[10px] text-amber-400/60 ml-6 mt-0.5 font-medium">{subLabel}</p>
                      )}
                    </div>
                    <span className="font-outfit font-black text-white text-sm">{fmt(val)}</span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
                    <div className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${p}%`, background: `linear-gradient(90deg,${item.from},${item.to})` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Per person */}
        <div className="flex justify-between items-center py-5 mt-4"
          style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <span className="text-white/40 font-medium">Per person (estimated)</span>
          <span className="font-outfit font-black text-amber-300 text-2xl">{fmt(budget.per_person)}</span>
        </div>

        {/* ── Daily breakdown ────────────────────────────────────── */}
        {daily && (
          <div className="mt-4 p-5 rounded-2xl"
            style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
            <div className="flex items-center justify-between mb-4">
              <p className="text-[10px] font-black text-amber-400/60 uppercase tracking-widest">📅 Daily Spend</p>
              <div className="flex items-center gap-3 text-xs">
                <span className="text-emerald-400/70">Min {fmtK(daily.min_total)}</span>
                <span className="text-white/30">·</span>
                <span className="text-amber-300 font-bold">{fmtK(daily.total)}</span>
                <span className="text-white/30">·</span>
                <span className="text-rose-400/70">Max {fmtK(daily.max_total)}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {DAILY_ITEMS.map(item => {
                const val = daily[item.key] || 0
                if (val === 0) return null
                return (
                  <div key={item.key} className="flex items-center justify-between px-3 py-2 rounded-xl"
                    style={{ background: 'rgba(255,255,255,0.03)' }}>
                    <div className="flex items-center gap-2">
                      <span className="text-sm">{item.emoji}</span>
                      <span className="text-white/45 text-xs">{item.label}</span>
                    </div>
                    <span className="font-bold text-white/70 text-xs">{fmt(val)}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Tips */}
        {budget.budget_tips?.length > 0 && (
          <div className="mt-5 space-y-2.5">
            <p className="text-[10px] font-black text-amber-400/50 uppercase tracking-widest">💡 Money-Saving Tips</p>
            {budget.budget_tips.slice(0, 3).map((tip, i) => (
              <div key={i} className="flex items-start gap-3 p-3.5 rounded-2xl"
                style={{ background: 'rgba(52,211,153,0.05)', border: '1px solid rgba(52,211,153,0.12)' }}>
                <span className="text-green-400 font-black text-sm mt-0.5 shrink-0">✓</span>
                <span className="text-white/50 text-sm">{tip}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
