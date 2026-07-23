export default function WeatherCard({ weather, destination }) {
  return (
    <div className="p-6 rounded-3xl h-full relative overflow-hidden"
      style={{ background: 'rgba(6,9,24,0.65)', border: '1px solid rgba(34,211,238,0.15)', backdropFilter: 'blur(16px)' }}>
      {/* Background orb */}
      <div className="absolute -top-8 -right-8 w-40 h-40 rounded-full blur-3xl opacity-15 pointer-events-none"
        style={{ background: 'radial-gradient(circle,#06b6d4,transparent)' }} />

      <div className="relative z-10">
        <p className="text-xs font-black text-cyan-400/60 uppercase tracking-widest mb-5 flex items-center gap-2">
          <span>🌤️</span> Weather · {destination}
        </p>

        {/* Current */}
        <div className="flex items-center gap-5 mb-6">
          <div className="text-6xl">{weather.icon}</div>
          <div className="flex-1">
            <div className="font-outfit font-black text-white leading-none" style={{ fontSize: '3.5rem' }}>
              {weather.temperature}°<span className="text-3xl text-white/50">C</span>
            </div>
            <div className="text-white/60 font-medium mt-1">{weather.description}</div>
            <div className="text-white/30 text-xs mt-0.5">Feels like {weather.feels_like}°C</div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-2 justify-end">
              <span className="text-sm">💧</span>
              <div>
                <div className="text-white font-bold text-sm">{weather.humidity}%</div>
                <div className="text-white/30 text-[10px]">Humidity</div>
              </div>
            </div>
            <div className="flex items-center gap-2 justify-end">
              <span className="text-sm">💨</span>
              <div>
                <div className="text-white font-bold text-sm">{weather.wind_speed} km/h</div>
                <div className="text-white/30 text-[10px]">Wind</div>
              </div>
            </div>
          </div>
        </div>

        {/* Forecast */}
        {weather.forecast?.length > 0 && (
          <>
            <p className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-3">5-Day Forecast</p>
            <div className="flex gap-2">
              {weather.forecast.map((d, i) => (
                <div key={i} className="flex-1 rounded-2xl p-3 text-center transition-all hover:-translate-y-1"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' }}>
                  <div className="text-[10px] text-white/40 font-bold mb-1">
                    {new Date(d.date).toLocaleDateString('en-IN', { weekday: 'short' })}
                  </div>
                  <div className="text-2xl my-1.5">{d.icon}</div>
                  <div className="text-sm font-black text-cyan-300">{d.max_temp}°</div>
                  <div className="text-[10px] text-white/30">{d.min_temp}°</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
