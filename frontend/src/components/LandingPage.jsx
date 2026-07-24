import { useAuth } from '../context/AuthContext'
import { useState, useEffect } from 'react'
import FeatureDetail from './FeatureDetail'

const HERO_SLIDES = [
  { img: 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1600&q=80', label: 'Swiss Alps, Switzerland' },
  { img: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1600&q=80', label: 'Maldives' },
  { img: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1600&q=80', label: 'Paris, France' },
  { img: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=1600&q=80', label: 'Tokyo, Japan' },
  { img: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1600&q=80', label: 'Dubai, UAE' },
  { img: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=1600&q=80', label: 'Bali, Indonesia' },
]

const TRUST_ITEMS = [
  { icon: '🔒', text: 'No credit card required' },
  { icon: '⚡', text: 'Results in under 30 seconds' },
  { icon: '🌍', text: '30+ cities worldwide' },
  { icon: '🤖', text: 'Powered by Google Gemini' },
  { icon: '📍', text: 'Real places, zero fake data' },
  { icon: '🆓', text: 'Free forever plan' },
]

const DESTINATIONS = [
  { name: 'Goa', country: 'India', desc: 'Sun, Sand & Spice', img: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800', accent: '#06b6d4' },
  { name: 'Jaipur', country: 'India', desc: 'The Pink City', img: 'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800', accent: '#f472b6' },
  { name: 'Paris', country: 'France', desc: 'City of Love & Lights', img: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800', accent: '#e879f9' },
  { name: 'Dubai', country: 'UAE', desc: 'Land of the Future', img: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800', accent: '#f59e0b' },
  { name: 'Bali', country: 'Indonesia', desc: 'Island Paradise', img: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800', accent: '#34d399' },
  { name: 'Istanbul', country: 'Turkey', desc: 'Where East Meets West', img: 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800', accent: '#60a5fa' },
  { name: 'Tokyo', country: 'Japan', desc: 'Tradition Meets Tech', img: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800', accent: '#f87171' },
  { name: 'Manali', country: 'India', desc: 'Himalayan Escape', img: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800', accent: '#818cf8' },
]

const FEATURES = [
  { icon: '🤖', title: 'Groq + Gemini AI',        desc: 'Llama 3 & Gemini generate rich, personalised day-by-day narratives — not generic text. Falls back automatically if one is rate-limited.',                    gradient: 'from-violet-500 to-purple-600', glow: 'rgba(139,92,246,0.3)' },
  { icon: '🗺️', title: 'Smart Route Planning',     desc: 'ML-powered nearest-neighbor algorithm groups nearby attractions and minimises your daily travel time — like a TSP solver in your pocket.',             gradient: 'from-blue-500 to-cyan-500',    glow: 'rgba(6,182,212,0.3)'   },
  { icon: '💰', title: 'Budget Prediction',         desc: 'Regression-based cost model estimates hotel, food, transport and activity costs per person accurately — with a min/estimated/max breakdown.',         gradient: 'from-emerald-500 to-green-500',glow: 'rgba(52,211,153,0.3)'  },
  { icon: '🌤️', title: 'Live Weather',              desc: 'OpenWeatherMap integration shows real-time weather at your destination — temperature, humidity, wind speed and a 5-day forecast.',                    gradient: 'from-amber-500 to-orange-500', glow: 'rgba(245,158,11,0.3)'  },
  { icon: '📍', title: 'Real Places Only',          desc: 'Google Places API + curated data for 50+ cities ensures only real tourist attractions — zero AI-hallucinated or fake place names.',                  gradient: 'from-rose-500 to-pink-500',    glow: 'rgba(244,63,94,0.3)'   },
  { icon: '✈️', title: 'Global Coverage',           desc: 'Plan trips to any city worldwide — from Shimla to Sydney, Jaipur to Tokyo. Special curated data for 50+ Indian destinations.',                       gradient: 'from-teal-500 to-cyan-600',    glow: 'rgba(20,184,166,0.3)'  },
  { icon: '🏨', title: 'Hotel Selection',           desc: 'Browse real hotels near your arrival point — OSM + Google Places + curated database for 30+ Indian cities with price ranges per travel style.',      gradient: 'from-sky-500 to-blue-600',     glow: 'rgba(14,165,233,0.3)'  },
  { icon: '🚆', title: 'Transport Options',         desc: 'Flight, train, bus, taxi and self-drive options with realistic INR fares. Live Amadeus flight prices when configured.',                              gradient: 'from-orange-500 to-red-500',   glow: 'rgba(239,68,68,0.3)'   },
  { icon: '🤖', title: 'AI Travel Chatbot',         desc: 'Ask anything about your trip — hotel prices, local food, transport fares, entry fees. Powered by Groq with OpenRouter fallback.',                   gradient: 'from-fuchsia-500 to-pink-600', glow: 'rgba(217,70,239,0.3)'  },
  { icon: '🎒', title: 'Smart Packing List',        desc: 'AI generates a personalised packing checklist based on destination, weather and trip duration. Check off items as you pack.',                        gradient: 'from-lime-500 to-green-600',   glow: 'rgba(132,204,22,0.3)'  },
  { icon: '⚖️', title: 'Budget Comparison',         desc: 'Compare Budget vs Moderate vs Luxury costs for the same trip side-by-side — see exactly where the money goes per category.',                        gradient: 'from-indigo-500 to-violet-600',glow: 'rgba(99,102,241,0.3)'  },
  { icon: '💱', title: 'Currency Converter',        desc: 'Instantly see your budget in local currencies — AED for Dubai, THB for Bangkok, EUR for Paris. 20+ currencies, no API key needed.',                 gradient: 'from-cyan-500 to-teal-600',    glow: 'rgba(6,182,212,0.3)'   },
  { icon: '📅', title: 'Best Time Calendar',        desc: 'Month-by-month visual showing Peak / Good / Avoid seasons for 40+ destinations. Know exactly when to visit before you book.',                       gradient: 'from-purple-500 to-indigo-600',glow: 'rgba(167,139,250,0.3)' },
  { icon: '🍽️', title: 'Nearby Restaurants',       desc: 'Toggle the map to show restaurants near your destination instead of attractions. Powered by Google Maps embed — no extra API needed.',             gradient: 'from-orange-400 to-amber-500', glow: 'rgba(251,146,60,0.3)'  },
  { icon: '🎲', title: 'Surprise Me!',              desc: 'Let AI pick a destination for you based on your budget and travel style — budget gets hill stations, luxury gets Maldives.',                        gradient: 'from-pink-500 to-rose-600',    glow: 'rgba(244,63,94,0.3)'   },
  { icon: '📋', title: 'Trip History',              desc: 'Every itinerary is saved automatically. Revisit past trips, reload a full plan, or delete old ones — your travel archive in one click.',           gradient: 'from-slate-500 to-gray-600',   glow: 'rgba(100,116,139,0.3)' },
  { icon: '⭐', title: 'Trip Rating',               desc: 'Rate and review your AI-planned itinerary with 1–5 stars and a written note. Stored in the database for feedback analysis.',                       gradient: 'from-yellow-400 to-amber-500', glow: 'rgba(251,191,36,0.3)'  },
  { icon: '🔗', title: 'Share Itinerary',           desc: 'Generate a public share link for any trip. Anyone with the link can view the full itinerary — no login required.',                                  gradient: 'from-indigo-400 to-blue-500',  glow: 'rgba(99,102,241,0.3)'  },
  { icon: '📱', title: 'Offline Mode',              desc: 'Save any itinerary to your device before travelling. View your full trip plan — places, budget, schedule — even with no internet.',                gradient: 'from-emerald-400 to-teal-500', glow: 'rgba(52,211,153,0.3)'  },
  { icon: '📄', title: 'PDF Export',                desc: 'Download your complete itinerary as a clean, print-ready PDF with a single click. Share with family or save for offline reference.',               gradient: 'from-red-400 to-rose-500',     glow: 'rgba(239,68,68,0.3)'   },
  { icon: '📊', title: 'Analytics Dashboard',       desc: 'See stats across all your planned trips — top destinations, favourite travel styles, average budget. Your personal travel data visualised.',        gradient: 'from-violet-400 to-purple-500',glow: 'rgba(167,139,250,0.3)' },
  { icon: '🔐', title: 'Google Sign-In',            desc: 'Login with your real Gmail account via Google OAuth. Your trips are linked to your profile — accessible from any device.',                          gradient: 'from-blue-400 to-indigo-500',  glow: 'rgba(59,130,246,0.3)'  },
]

const STATS = [
  { number: '30+', label: 'Cities Covered', icon: '🌍' },
  { number: '10K+', label: 'Trips Planned', icon: '✈️' },
  { number: '98%', label: 'Accuracy Rate', icon: '🎯' },
  { number: '< 30s', label: 'Generation Time', icon: '⚡' },
]

const HOW_IT_WORKS = [
  { title: 'Enter Your Trip Details', desc: 'Tell us your destination, budget, travel dates, group size and interests.', icon: '📝', color: '#f59e0b' },
  { title: 'AI Processes Your Request', desc: 'Gemini AI + ML algorithms rank attractions, optimize routes and predict costs.', icon: '⚙️', color: '#a78bfa' },
  { title: 'Get Your Perfect Itinerary', desc: 'Receive a full day-wise plan with real places, timings, maps and budget breakdown.', icon: '🗺️', color: '#34d399' },
]

const TESTIMONIALS = [
  { name: 'Priya Sharma', location: 'Mumbai → Goa', text: 'Planned a 4-day Goa trip in under a minute! The budget estimate was spot on and the places were exactly what we wanted.', rating: 5, avatar: 'P', gradient: 'from-pink-500 to-rose-600' },
  { name: 'Rahul Mehta', location: 'Delhi → Istanbul', text: 'Hagia Sophia, Grand Bazaar, Bosphorus Cruise — all the must-visits were there. The AI knew exactly what a first-timer needs.', rating: 5, avatar: 'R', gradient: 'from-blue-500 to-cyan-600' },
  { name: 'Sneha Patel', location: 'Bangalore → Paris', text: 'The weather integration is genius. It suggested indoor museums on rainy days and outdoor spots when sunny. Perfect planning!', rating: 5, avatar: 'S', gradient: 'from-violet-500 to-purple-600' },
]

const BLOG_PREVIEWS = [
  {
    tag: 'Travel Tips',
    title: '10 Things to Know Before Visiting Bali',
    img: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80',
    time: '5 min read',
    content: `Bali is one of the world's most magical destinations — but a little preparation goes a long way. Here's what every first-time visitor should know:

**1. Choose the right season.** Bali has two seasons — dry (April–October) is ideal for beaches and outdoor activities. The wet season (November–March) brings daily rain but fewer tourists and lush green scenery.

**2. Respect temple etiquette.** Always wear a sarong and sash when entering temples. They're often available for rent at the entrance. Never point your feet at sacred objects.

**3. Negotiate transport fares upfront.** Unlike metered taxis in cities, many Bali drivers quote fixed prices. Agree before you get in. Grab is available in major areas and is more transparent.

**4. Try the local warungs.** These small family-owned restaurants serve authentic Balinese food at a fraction of tourist restaurant prices. Nasi goreng, mie goreng, and babi guling are must-tries.

**5. Explore beyond Kuta.** Kuta is crowded and touristy. Ubud offers culture and rice terraces, Seminyak has upscale dining, Canggu is for digital nomads, and Nusa Penida has dramatic cliffs.

**6. Carry cash.** While cards are accepted at hotels and larger restaurants, many small shops, markets, and temples only take cash. ATMs are widely available but use trusted bank ATMs.

**7. Book accommodation early in peak season.** July–August and December–January see massive tourist surges. Book at least 2–3 months ahead for good villas.

**8. Rent a scooter or hire a driver.** Public transport is minimal. Renting a scooter gives freedom but requires an international driving permit. A private driver for the day costs around ₹2,000–3,000 and is worth it.

**9. Bali belly is real.** Stick to bottled water, avoid ice in street stalls, and carry rehydration salts. Your stomach needs a few days to adjust to local food.

**10. The people are the destination.** Balinese culture is deeply spiritual. Festivals, ceremonies, and daily offerings are everywhere. Slow down, be present, and engage respectfully — it's what makes Bali unforgettable.`,
  },
  {
    tag: 'AI Travel',
    title: 'How AI Is Changing the Way We Plan Trips',
    img: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    time: '4 min read',
    content: `Travel planning has traditionally been a time-consuming process — hours spent on booking sites, forums, and spreadsheets. Artificial Intelligence is changing all of that.

**From Search to Generation**
Traditional travel planning means searching for information across dozens of websites. AI-powered planners generate a complete itinerary from a single prompt. Instead of "find hotels in Jaipur", you say "plan a 4-day moderate-budget trip to Jaipur for 2 people interested in history" — and get a fully structured plan in seconds.

**Machine Learning for Smarter Recommendations**
Modern AI travel tools use ML algorithms to rank attractions by tourist popularity, not just ratings. This means famous landmarks like Amber Fort or Hawa Mahal naturally surface above generic "local spots" that might have artificially inflated reviews.

**Route Optimization**
The Nearest-Neighbor heuristic — a classical computer science algorithm — is now applied to daily itinerary planning. Instead of visiting attractions in a random order, AI calculates the most efficient route so you spend less time in transit and more time exploring.

**Budget Intelligence**
AI can now estimate realistic trip costs based on destination type, travel style, and group size. A budget trip to Goa costs fundamentally differently from a luxury trip to Dubai — and modern systems model these differences across accommodation, food, transport, and activities.

**Real-Time Context**
Integration with live APIs means AI itineraries can now factor in current weather, real hotel availability near your arrival point, and live transport schedules — making recommendations that are not just smart but also practical.

**The Human Element**
Despite all this, the best AI travel tools don't replace the human joy of exploration — they amplify it. By handling the logistics, they free you to focus on the experiences that make travel meaningful.`,
  },
  {
    tag: 'Budget Travel',
    title: 'Europe on ₹80,000: A Complete Guide',
    img: 'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=600&q=80',
    time: '7 min read',
    content: `Travelling Europe on a tight budget sounds impossible — but with the right strategy, ₹80,000 (roughly €850) can cover 10–12 days across multiple countries. Here's how.

**Choose Budget-Friendly Countries**
Western Europe (Paris, London, Amsterdam) is expensive. Eastern Europe (Prague, Budapest, Krakow, Warsaw) offers the same historical richness at 40–60% lower cost. A hostel dorm in Prague costs €10–15/night vs €40–60 in Paris.

**Fly Smart**
Book flights 6–8 weeks in advance. Use budget airlines like Ryanair, Wizz Air, and EasyJet for intra-Europe travel. Flying into Frankfurt or Vienna and taking trains/buses onward is often cheaper than direct flights.

**Sleep in Hostels**
Europe has a world-class hostel network. Generator, Zostel, and local independent hostels offer clean dorms with free breakfast for €12–20/night. Book on Hostelworld or Booking.com.

**Eat Like a Local**
Avoid tourist-strip restaurants. Look for daily lunch menus (menu del día in Spain, dagschotel in Belgium) — a 3-course meal for €8–12. Supermarket meals, street food, and food markets keep costs to €10–15/day for food.

**Free Attractions**
Most of Europe's greatest attractions are free or low-cost:
- Rome: Colosseum area walk, Trevi Fountain, Vatican Square
- Paris: Louvre (free first Sunday), Eiffel Tower exterior, Sacré-Cœur
- Prague: Old Town Square, Charles Bridge, castle exterior
- Budapest: Parliament exterior, Fisherman's Bastion, thermal bath entry ~€15

**Use Rail Passes Wisely**
An Interrail Global Pass for 5 days in a month costs ~€185 — worth it if crossing 3+ countries. For shorter itineraries, point-to-point tickets on Trainline or Omio are often cheaper.

**Sample 10-Day Budget (₹80,000 / €850)**
- Flights: €250 (India–Europe return)
- Accommodation: €140 (10 nights hostel)
- Food: €120 (€12/day)
- Transport: €180 (rail + buses)
- Attractions: €80
- Miscellaneous: €80
**Total: €850**

Europe on a budget isn't about sacrifice — it's about priorities. Spend on the experiences, save on the logistics.`,
  },
]

export default function LandingPage({ onStartPlanning }) {
  const { openLogin, openSignup, user } = useAuth()
  const [currentSlide, setCurrentSlide] = useState(0)
  const [activeFeature, setActiveFeature] = useState(null)
  const [activeBlog, setActiveBlog] = useState(null)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % HERO_SLIDES.length)
    }, 5000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="min-h-screen" style={{ background: '#060918' }}>
      {/* ── FEATURE DETAIL OVERLAY ── */}
      {activeFeature && (
        <FeatureDetail feature={activeFeature} onClose={() => setActiveFeature(null)} />
      )}

      {/* ── HERO ─────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex flex-col overflow-hidden">
        <div className="absolute inset-0">
          {HERO_SLIDES.map((slide, i) => (
            <div key={i} className={`hero-slide ${i === currentSlide ? 'active' : ''}`}
              style={{ backgroundImage: `url(${slide.img})` }} />
          ))}
          <div className="absolute inset-0" style={{ background: 'linear-gradient(to bottom, rgba(4,8,20,0.6) 0%, rgba(4,8,20,0.3) 40%, rgba(4,8,20,0.7) 80%, rgba(6,9,24,1) 100%)' }} />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, rgba(120,40,0,0.2) 0%, transparent 50%, rgba(8,100,140,0.15) 100%)' }} />
        </div>

        {/* Navbar */}
        <nav className="relative z-10 flex items-center justify-between px-6 md:px-14 py-4"
          style={{ background: 'rgba(6,9,24,0.5)', backdropFilter: 'blur(16px)', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          {/* Logo */}
          <div className="flex items-center gap-3">
            <span className="text-3xl" style={{ animation: 'float 4s ease-in-out infinite' }}>✈️</span>
            <div>
              <div className="font-outfit font-black text-white text-lg tracking-tight leading-none">Smart Travel Planner</div>
              <div className="text-amber-400 text-[10px] font-semibold tracking-widest uppercase mt-0.5">AI-Powered Itineraries</div>
            </div>
          </div>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-7 text-sm font-semibold text-white/55">
            <a href="#features" className="hover:text-amber-300 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-amber-300 transition-colors">How It Works</a>
            <a href="#destinations" className="hover:text-amber-300 transition-colors">Destinations</a>
            <a href="#blog" className="hover:text-amber-300 transition-colors">Blog</a>
          </div>

          {/* Auth buttons */}
          <div className="flex items-center gap-2">
            {user ? (
              /* Logged-in state */
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-2 rounded-xl"
                  style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-black text-white"
                    style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
                    {user.name?.[0]?.toUpperCase() || '?'}
                  </div>
                  <span className="text-white text-sm font-semibold hidden sm:block max-w-[100px] truncate">{user.name}</span>
                </div>
                <button onClick={onStartPlanning}
                  className="text-sm font-black px-5 py-2.5 rounded-xl text-white transition-all hover:scale-105 hover:-translate-y-0.5"
                  style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)', boxShadow: '0 0 16px rgba(245,158,11,0.4)' }}>
                  🚀 Plan a Trip
                </button>
              </div>
            ) : (
              /* Logged-out state — prominent Sign In + Sign Up */
              <>
                {/* Log In — outlined */}
                <button
                  onClick={openLogin}
                  className="text-sm font-bold px-5 py-2.5 rounded-xl text-white transition-all hover:text-amber-300 hover:border-amber-400/50"
                  style={{
                    background: 'rgba(255,255,255,0.07)',
                    border: '1px solid rgba(255,255,255,0.18)',
                    backdropFilter: 'blur(8px)',
                  }}>
                  Log In
                </button>

                {/* Sign Up — filled amber */}
                <button
                  onClick={openSignup}
                  className="text-sm font-black px-5 py-2.5 rounded-xl text-white transition-all hover:scale-105 hover:-translate-y-0.5"
                  style={{
                    background: 'linear-gradient(135deg,#f59e0b,#ea580c)',
                    boxShadow: '0 0 18px rgba(245,158,11,0.45)',
                  }}>
                  Sign Up Free ✨
                </button>
              </>
            )}
          </div>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 flex-1 flex items-center justify-center px-6 py-16">
          <div className="text-center max-w-5xl mx-auto hero-content">
            <div className="inline-flex items-center gap-2 badge-shimmer text-amber-300 text-xs font-bold uppercase tracking-widest px-5 py-2.5 rounded-full mb-8">
              <span className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
              Powered by Gemini AI + Machine Learning
            </div>
            <h1 className="font-outfit font-black text-white leading-[1.05] mb-6" style={{ fontSize: 'clamp(2.8rem, 8vw, 5.5rem)' }}>
              Your Dream Trip,<br />
              <span className="text-gold-gradient">Planned by AI</span>
            </h1>
            <p className="text-white/65 text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
              Enter your destination, budget and preferences. Get a complete day-wise itinerary with real places, route optimization, weather insights and budget estimates — in under 30 seconds.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-14">
              <button onClick={user ? onStartPlanning : openSignup}
                className="font-black text-lg px-10 py-5 rounded-2xl shadow-2xl transition-all hover:-translate-y-1 hover:scale-105 text-white"
                style={{ background: 'linear-gradient(135deg, #f59e0b, #ea580c)', boxShadow: '0 0 40px rgba(245,158,11,0.5)' }}>
                ✨ Start Planning for Free
              </button>
              <button onClick={user ? onStartPlanning : openLogin}
                className="text-lg px-10 py-5 rounded-2xl font-bold transition-all hover:-translate-y-1 text-white"
                style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.2)', backdropFilter: 'blur(8px)' }}>
                🚀 Plan a Trip Now
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
              {STATS.map((s, i) => (
                <div key={i} className="rounded-2xl p-5 text-center"
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(12px)' }}>
                  <div className="text-3xl mb-2">{s.icon}</div>
                  <div className="text-white font-black text-2xl font-outfit">{s.number}</div>
                  <div className="text-amber-200/60 text-xs font-medium mt-1">{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Slide dots */}
        <div className="relative z-10 pb-8 flex flex-col items-center gap-3">
          <div className="flex items-center gap-2 text-white/40 text-xs tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            {HERO_SLIDES[currentSlide].label}
          </div>
          <div className="flex items-center gap-2">
            {HERO_SLIDES.map((_, i) => (
              <button key={i} className={`slide-dot ${i === currentSlide ? 'active' : ''}`}
                style={{ width: i === currentSlide ? '28px' : '8px' }}
                onClick={() => setCurrentSlide(i)} />
            ))}
          </div>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-28 pointer-events-none"
          style={{ background: 'linear-gradient(to bottom, transparent, #060918)' }} />
      </section>

      {/* ── TRUST BAR ────────────────────────────────────────── */}
      <div style={{ background: 'rgba(255,255,255,0.03)', borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <div className="max-w-6xl mx-auto px-6 py-5">
          <div className="flex flex-wrap justify-center gap-x-10 gap-y-3">
            {TRUST_ITEMS.map((t, i) => (
              <div key={i} className="flex items-center gap-2 text-white/50 text-sm font-medium">
                <span className="text-base">{t.icon}</span>
                <span>{t.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── FEATURES ─────────────────────────────────────────── */}
      <section id="features" className="py-24 px-4 md:px-10" style={{ background: 'linear-gradient(180deg, #060918 0%, #0a0f20 100%)' }}>
        <div className="max-w-[1400px] mx-auto">

          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-4"
              style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
              ⚡ Powered by AI + ML
            </div>
            <h2 className="font-outfit font-black text-white text-4xl md:text-6xl mb-4">
              Everything You Need,<br /><span className="text-gold-gradient">All in One Place</span>
            </h2>
            <p className="text-white/40 text-lg max-w-2xl mx-auto">
              22 features built for serious travellers — from AI itinerary generation to offline access, currency conversion and real-time hotel search.
            </p>
          </div>

          {/* ── Row 1: 3 hero cards ── */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* AI hero */}
            <div className="group relative rounded-3xl p-8 overflow-hidden transition-all hover:-translate-y-1"
              style={{ background: 'linear-gradient(135deg,rgba(139,92,246,0.15),rgba(99,102,241,0.08))', border: '1px solid rgba(139,92,246,0.3)' }}>
              <div className="absolute -top-8 -right-8 w-40 h-40 rounded-full blur-3xl opacity-20 pointer-events-none"
                style={{ background: 'radial-gradient(circle,#8b5cf6,transparent)' }} />
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mb-5 shadow-xl"
                style={{ background: 'linear-gradient(135deg,#8b5cf6,#6366f1)' }}>🤖</div>
              <div className="inline-flex items-center gap-1.5 text-violet-400 text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full mb-3"
                style={{ background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.25)' }}>✦ Core AI</div>
              <h3 className="font-outfit font-black text-white text-2xl mb-2">Groq + Gemini AI</h3>
              <p className="text-white/50 text-sm leading-relaxed">Llama 3 & Gemini generate rich, personalised day-by-day narratives — not generic text. Auto-fallback when one is rate-limited.</p>
            </div>
            {/* Route hero */}
            <div className="group relative rounded-3xl p-8 overflow-hidden transition-all hover:-translate-y-1"
              style={{ background: 'linear-gradient(135deg,rgba(6,182,212,0.15),rgba(59,130,246,0.08))', border: '1px solid rgba(6,182,212,0.3)' }}>
              <div className="absolute -top-8 -right-8 w-40 h-40 rounded-full blur-3xl opacity-20 pointer-events-none"
                style={{ background: 'radial-gradient(circle,#06b6d4,transparent)' }} />
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mb-5 shadow-xl"
                style={{ background: 'linear-gradient(135deg,#06b6d4,#3b82f6)' }}>🗺️</div>
              <div className="inline-flex items-center gap-1.5 text-cyan-400 text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full mb-3"
                style={{ background: 'rgba(6,182,212,0.15)', border: '1px solid rgba(6,182,212,0.25)' }}>✦ ML Algorithm</div>
              <h3 className="font-outfit font-black text-white text-2xl mb-2">Smart Route Planning</h3>
              <p className="text-white/50 text-sm leading-relaxed">Nearest-neighbor TSP algorithm minimises daily travel time. Optimised routes so you spend less time commuting, more time exploring.</p>
            </div>
            {/* Budget hero */}
            <div className="group relative rounded-3xl p-8 overflow-hidden transition-all hover:-translate-y-1"
              style={{ background: 'linear-gradient(135deg,rgba(52,211,153,0.15),rgba(16,185,129,0.08))', border: '1px solid rgba(52,211,153,0.3)' }}>
              <div className="absolute -top-8 -right-8 w-40 h-40 rounded-full blur-3xl opacity-20 pointer-events-none"
                style={{ background: 'radial-gradient(circle,#34d399,transparent)' }} />
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mb-5 shadow-xl"
                style={{ background: 'linear-gradient(135deg,#34d399,#10b981)' }}>💰</div>
              <div className="inline-flex items-center gap-1.5 text-emerald-400 text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full mb-3"
                style={{ background: 'rgba(52,211,153,0.15)', border: '1px solid rgba(52,211,153,0.25)' }}>✦ Budget AI</div>
              <h3 className="font-outfit font-black text-white text-2xl mb-2">Smart Budget Prediction</h3>
              <p className="text-white/50 text-sm leading-relaxed">Regression-based model estimates hotel, food, transport & activities per person. Compare Budget vs Moderate vs Luxury instantly.</p>
            </div>
          </div>

          {/* ── Row 2: 4 medium cards ── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {[
              { icon: '🌤️', title: 'Live Weather',      desc: 'Real-time OpenWeatherMap data — temp, humidity, wind & 5-day forecast.',         grad: 'from-amber-500 to-orange-500',   glow: 'rgba(245,158,11,0.2)',   border: 'rgba(245,158,11,0.25)'  },
              { icon: '📍', title: 'Real Places Only',  desc: 'Google Places + curated data for 50+ cities. Zero AI-hallucinated attractions.',  grad: 'from-rose-500 to-pink-500',      glow: 'rgba(244,63,94,0.2)',    border: 'rgba(244,63,94,0.25)'   },
              { icon: '✈️', title: 'Global Coverage',   desc: 'Any city worldwide — Shimla to Sydney, Jaipur to Tokyo. 50+ Indian cities.',      grad: 'from-teal-500 to-cyan-600',      glow: 'rgba(20,184,166,0.2)',   border: 'rgba(20,184,166,0.25)'  },
              { icon: '🏨', title: 'Hotel Search',      desc: 'Real hotels near your arrival point with INR price ranges per travel style.',     grad: 'from-sky-500 to-blue-600',       glow: 'rgba(14,165,233,0.2)',   border: 'rgba(14,165,233,0.25)'  },
            ].map((f, i) => (
              <div key={i} className="group relative rounded-2xl p-6 overflow-hidden transition-all hover:-translate-y-1"
                style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${f.border}` }}>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl pointer-events-none"
                  style={{ background: `radial-gradient(circle at top right, ${f.glow}, transparent 60%)` }} />
                <div className={`w-12 h-12 bg-gradient-to-br ${f.grad} rounded-xl flex items-center justify-center text-2xl mb-4 shadow-lg group-hover:scale-110 transition-transform`}>{f.icon}</div>
                <h3 className="font-outfit font-black text-white text-base mb-1.5">{f.title}</h3>
                <p className="text-white/40 text-xs leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* ── Row 3: wide chatbot + 3 small ── */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
            {/* Wide chatbot card */}
            <div className="md:col-span-2 group relative rounded-2xl p-7 overflow-hidden transition-all hover:-translate-y-1"
              style={{ background: 'linear-gradient(135deg,rgba(217,70,239,0.12),rgba(99,102,241,0.08))', border: '1px solid rgba(217,70,239,0.25)' }}>
              <div className="absolute -bottom-8 -right-8 w-32 h-32 rounded-full blur-3xl opacity-20 pointer-events-none"
                style={{ background: 'radial-gradient(circle,#d946ef,transparent)' }} />
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl mb-4 shadow-xl"
                style={{ background: 'linear-gradient(135deg,#d946ef,#8b5cf6)' }}>🤖</div>
              <h3 className="font-outfit font-black text-white text-xl mb-2">AI Travel Chatbot</h3>
              <p className="text-white/50 text-sm leading-relaxed">Ask anything about your trip — hotel prices, local food, transport fares, attraction entry fees. Context-aware, powered by Groq with OpenRouter fallback.</p>
            </div>
            {/* 3 small cards */}
            {[
              { icon: '🚆', title: 'Transport Options', desc: 'Flight, train, bus, taxi with live INR fares via Amadeus API.',  grad: 'from-orange-500 to-red-500',     border: 'rgba(239,68,68,0.2)'    },
              { icon: '🎒', title: 'Packing List',       desc: 'AI-generated checklist based on destination & weather.',         grad: 'from-lime-500 to-green-600',     border: 'rgba(132,204,22,0.2)'   },
              { icon: '💱', title: 'Currency Widget',    desc: 'Budget in 20+ currencies — AED, EUR, THB and more. Instant.',   grad: 'from-cyan-500 to-teal-600',      border: 'rgba(6,182,212,0.2)'    },
            ].map((f, i) => (
              <div key={i} className="group relative rounded-2xl p-5 overflow-hidden transition-all hover:-translate-y-1"
                style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${f.border}` }}>
                <div className={`w-11 h-11 bg-gradient-to-br ${f.grad} rounded-xl flex items-center justify-center text-xl mb-3 shadow-md group-hover:scale-110 transition-transform`}>{f.icon}</div>
                <h3 className="font-outfit font-black text-white text-sm mb-1">{f.title}</h3>
                <p className="text-white/35 text-xs leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* ── Row 4: 5 equal cards ── */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
            {[
              { icon: '📅', title: 'Best Time Calendar',  desc: 'Peak/Good/Avoid by month for 40+ destinations.',          grad: 'from-purple-500 to-indigo-600',  border: 'rgba(167,139,250,0.2)'  },
              { icon: '🍽️', title: 'Nearby Restaurants',  desc: 'Toggle map to show restaurants near your destination.',    grad: 'from-orange-400 to-amber-500',   border: 'rgba(251,146,60,0.2)'   },
              { icon: '🎲', title: 'Surprise Me!',         desc: 'AI picks destination by budget & style. Budget = hills, Luxury = Maldives.', grad: 'from-pink-500 to-rose-600', border: 'rgba(244,63,94,0.2)' },
              { icon: '⚖️', title: 'Budget Comparison',   desc: 'Budget vs Moderate vs Luxury — cost breakdown per category.', grad: 'from-indigo-500 to-violet-600', border: 'rgba(99,102,241,0.2)' },
              { icon: '🔐', title: 'Google Sign-In',       desc: 'Real Gmail OAuth — trips linked to your profile.',         grad: 'from-blue-400 to-indigo-500',    border: 'rgba(59,130,246,0.2)'   },
            ].map((f, i) => (
              <div key={i} className="group relative rounded-2xl p-5 overflow-hidden transition-all hover:-translate-y-1"
                style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${f.border}` }}>
                <div className={`w-11 h-11 bg-gradient-to-br ${f.grad} rounded-xl flex items-center justify-center text-xl mb-3 shadow-md group-hover:scale-110 transition-transform`}>{f.icon}</div>
                <h3 className="font-outfit font-black text-white text-sm mb-1">{f.title}</h3>
                <p className="text-white/35 text-xs leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* ── Row 5: save/share strip ── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: '📋', title: 'Trip History',        desc: 'Every itinerary saved. Reload any past trip in one click.',  grad: 'from-slate-400 to-gray-500',    border: 'rgba(148,163,184,0.2)', tag: '💾 Auto-saved'    },
              { icon: '⭐', title: 'Rate & Review',       desc: 'Star rating + written review stored in database.',            grad: 'from-yellow-400 to-amber-500',  border: 'rgba(251,191,36,0.2)',  tag: '⭐ 1–5 stars'     },
              { icon: '🔗', title: 'Share Itinerary',     desc: 'Public share link — anyone can view, no login needed.',       grad: 'from-indigo-400 to-blue-500',   border: 'rgba(99,102,241,0.2)',  tag: '🌐 Public link'   },
              { icon: '📱', title: 'Offline Mode',        desc: 'Save trip to device. Full plan available with no internet.',  grad: 'from-emerald-400 to-teal-500',  border: 'rgba(52,211,153,0.2)',  tag: '📴 Works offline' },
            ].map((f, i) => (
              <div key={i} className="group relative rounded-2xl p-6 overflow-hidden transition-all hover:-translate-y-1 flex gap-4 items-start"
                style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${f.border}` }}>
                <div className={`w-12 h-12 bg-gradient-to-br ${f.grad} rounded-xl flex items-center justify-center text-2xl flex-shrink-0 shadow-md group-hover:scale-110 transition-transform`}>{f.icon}</div>
                <div>
                  <div className="text-[10px] font-black uppercase tracking-wider text-white/30 mb-0.5">{f.tag}</div>
                  <h3 className="font-outfit font-black text-white text-sm mb-1">{f.title}</h3>
                  <p className="text-white/35 text-xs leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom PDF + Analytics row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="group relative rounded-2xl p-6 overflow-hidden transition-all hover:-translate-y-1 flex gap-5 items-center"
              style={{ background: 'linear-gradient(135deg,rgba(239,68,68,0.08),rgba(244,63,94,0.05))', border: '1px solid rgba(239,68,68,0.2)' }}>
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 shadow-xl"
                style={{ background: 'linear-gradient(135deg,#ef4444,#f43f5e)' }}>📄</div>
              <div>
                <h3 className="font-outfit font-black text-white text-lg mb-1">PDF Export</h3>
                <p className="text-white/45 text-sm">Download a clean, print-ready PDF of your full itinerary with one click. Share with family or save for offline reference.</p>
              </div>
            </div>
            <div className="group relative rounded-2xl p-6 overflow-hidden transition-all hover:-translate-y-1 flex gap-5 items-center"
              style={{ background: 'linear-gradient(135deg,rgba(167,139,250,0.1),rgba(139,92,246,0.06))', border: '1px solid rgba(167,139,250,0.2)' }}>
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0 shadow-xl"
                style={{ background: 'linear-gradient(135deg,#a78bfa,#8b5cf6)' }}>📊</div>
              <div>
                <h3 className="font-outfit font-black text-white text-lg mb-1">Analytics Dashboard</h3>
                <p className="text-white/45 text-sm">Visualise your travel history — top destinations, favourite styles, average spend. Your personal travel data in one view.</p>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────── */}
      <section id="how-it-works" className="py-28 px-6 relative overflow-hidden" style={{ background: '#0a0f20' }}>
        {/* Background orb */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
          style={{ background: 'radial-gradient(circle, rgba(245,158,11,0.06) 0%, transparent 70%)' }} />
        <div className="max-w-5xl mx-auto relative z-10">
          <div className="text-center mb-20">
            <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-4"
              style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
              🔄 Simple Process
            </div>
            <h2 className="font-outfit font-black text-white text-4xl md:text-5xl mb-4">How It <span className="text-gold-gradient">Works</span></h2>
            <p className="text-white/50 text-lg">Three simple steps to your perfect travel plan</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Connector line */}
            <div className="hidden md:block absolute top-14 left-[calc(16.6%+2rem)] right-[calc(16.6%+2rem)] h-0.5"
              style={{ background: 'linear-gradient(90deg, #f59e0b, #a78bfa, #34d399)' }} />
            {HOW_IT_WORKS.map((s, i) => (
              <div key={i} className="relative text-center group">
                <div className="relative inline-block mb-8">
                  <div className="w-28 h-28 rounded-3xl flex items-center justify-center text-5xl mx-auto transition-all duration-300 group-hover:scale-110 group-hover:-translate-y-2"
                    style={{ background: `rgba(255,255,255,0.04)`, border: `2px solid ${s.color}30`, boxShadow: `0 0 30px ${s.color}20` }}>
                    {s.icon}
                  </div>
                  <div className="absolute -top-3 -right-3 w-9 h-9 rounded-full flex items-center justify-center text-white text-xs font-black border-2 shadow-lg"
                    style={{ background: s.color, borderColor: '#0a0f20' }}>
                    {i + 1}
                  </div>
                </div>
                <h3 className="font-outfit font-bold text-white text-xl mb-3">{s.title}</h3>
                <p className="text-white/45 text-sm leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-16">
            <button onClick={user ? onStartPlanning : openSignup}
              className="font-black text-lg px-14 py-5 rounded-2xl text-white transition-all hover:-translate-y-1 hover:scale-105"
              style={{ background: 'linear-gradient(135deg, #f59e0b, #ea580c)', boxShadow: '0 0 40px rgba(245,158,11,0.4)' }}>
              🗺️ Try It Now — It's Free
            </button>
          </div>
        </div>
      </section>

      {/* ── DESTINATIONS ─────────────────────────────────────── */}
      <section id="destinations" className="py-28 px-6" style={{ background: 'linear-gradient(180deg, #0a0f20, #060918)' }}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-4"
              style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
              🌍 Popular Destinations
            </div>
            <h2 className="font-outfit font-black text-white text-4xl md:text-5xl mb-4">Where Will <span className="text-gold-gradient">You Go?</span></h2>
            <p className="text-white/50 text-lg">Click any destination to start planning your trip instantly</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {DESTINATIONS.map((d, i) => (
              <button key={i} onClick={user ? onStartPlanning : openSignup}
                className="text-left relative overflow-hidden rounded-3xl group transition-all duration-300 hover:-translate-y-2"
                style={{ minHeight: '260px', border: `1px solid rgba(255,255,255,0.06)` }}>
                <img src={d.img} alt={d.name} className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 60%, transparent 100%)' }} />
                {/* Accent border glow on hover */}
                <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
                  style={{ boxShadow: `inset 0 0 0 2px ${d.accent}` }} />
                <div className="relative z-10 flex flex-col justify-end h-full p-5" style={{ minHeight: '260px' }}>
                  <p className="text-white/50 text-[10px] font-bold uppercase tracking-widest mb-1">{d.country}</p>
                  <h3 className="font-outfit font-black text-white text-2xl leading-tight">{d.name}</h3>
                  <p className="text-white/60 text-sm mt-1">{d.desc}</p>
                  <div className="mt-4 flex items-center gap-2 text-sm font-bold transition-all duration-200"
                    style={{ color: d.accent }}>
                    <span>Plan Trip</span><span>→</span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ─────────────────────────────────────── */}
      <section className="py-28 px-6" style={{ background: '#060918' }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-4"
              style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
              ⭐ Traveler Reviews
            </div>
            <h2 className="font-outfit font-black text-white text-4xl md:text-5xl mb-4">Loved by <span className="text-gold-gradient">Travelers</span></h2>
            <p className="text-white/50 text-lg">Real stories from real adventurers</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((t, i) => (
              <div key={i} className="p-7 rounded-3xl transition-all duration-300 hover:-translate-y-2 relative overflow-hidden group"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                <div className="absolute top-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{ background: 'linear-gradient(90deg, #f59e0b, #ea580c)' }} />
                <div className="flex gap-0.5 mb-5">
                  {Array.from({ length: t.rating }).map((_, j) => (
                    <span key={j} className="text-amber-400 text-xl">★</span>
                  ))}
                </div>
                <p className="text-white/60 text-sm leading-relaxed mb-7 italic">"{t.text}"</p>
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 bg-gradient-to-br ${t.gradient} text-white rounded-2xl flex items-center justify-center font-black text-base shadow-lg`}>
                    {t.avatar}
                  </div>
                  <div>
                    <div className="font-bold text-white text-sm font-outfit">{t.name}</div>
                    <div className="text-amber-400/50 text-xs mt-0.5">{t.location}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── BLOG PREVIEWS ────────────────────────────────────── */}
      <section id="blog" className="py-28 px-6" style={{ background: 'linear-gradient(180deg, #060918, #0a0f20)' }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full mb-4"
              style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.2)' }}>
              📖 Travel Insights
            </div>
            <h2 className="font-outfit font-black text-white text-4xl md:text-5xl mb-4">From Our <span className="text-gold-gradient">Travel Blog</span></h2>
            <p className="text-white/50 text-lg">Tips, guides and AI travel secrets</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {BLOG_PREVIEWS.map((b, i) => (
              <div key={i} onClick={() => setActiveBlog(b)}
                className="group rounded-3xl overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-2"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                <div className="relative overflow-hidden" style={{ height: '180px' }}>
                  <img src={b.img} alt={b.title} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                  <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, rgba(6,9,24,0.7), transparent)' }} />
                  <span className="absolute top-4 left-4 text-xs font-bold px-3 py-1 rounded-full text-white"
                    style={{ background: 'rgba(245,158,11,0.8)' }}>{b.tag}</span>
                </div>
                <div className="p-6">
                  <h3 className="font-outfit font-bold text-white text-lg mb-3 leading-snug group-hover:text-amber-300 transition-colors">{b.title}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-white/35 text-xs">{b.time}</span>
                    <span className="text-amber-400 text-xs font-bold group-hover:gap-2 flex items-center gap-1 transition-all">Read →</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── BLOG ARTICLE MODAL ─────────────────────────────── */}
      {activeBlog && (
        <div className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-10 overflow-y-auto"
          onClick={() => setActiveBlog(null)}>
          <div className="absolute inset-0" style={{ background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)' }} />
          <div className="relative w-full max-w-3xl rounded-3xl overflow-hidden mb-8"
            style={{ background: 'rgba(6,9,24,0.98)', border: '1px solid rgba(245,158,11,0.2)' }}
            onClick={e => e.stopPropagation()}>
            {/* Hero image */}
            <div className="relative h-56 overflow-hidden">
              <img src={activeBlog.img} alt={activeBlog.title} className="w-full h-full object-cover" />
              <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, rgba(6,9,24,1) 0%, rgba(6,9,24,0.3) 60%, transparent 100%)' }} />
              <button onClick={() => setActiveBlog(null)}
                className="absolute top-4 right-4 w-9 h-9 rounded-xl flex items-center justify-center text-white/70 hover:text-white transition-colors"
                style={{ background: 'rgba(6,9,24,0.7)', backdropFilter: 'blur(8px)' }}>✕</button>
              <span className="absolute bottom-4 left-6 text-xs font-bold px-3 py-1 rounded-full text-white"
                style={{ background: 'rgba(245,158,11,0.85)' }}>{activeBlog.tag}</span>
            </div>
            {/* Content */}
            <div className="px-8 py-6">
              <h2 className="font-outfit font-black text-white text-2xl md:text-3xl mb-2">{activeBlog.title}</h2>
              <p className="text-amber-400/60 text-xs font-medium mb-6">⏱ {activeBlog.time}</p>
              <div className="prose-custom space-y-4">
                {activeBlog.content.split('\n\n').map((para, i) => {
                  if (!para.trim()) return null
                  // Bold headings like **text**
                  const isHeading = para.startsWith('**') && para.includes('**')
                  const rendered = para.split(/\*\*(.*?)\*\*/g).map((part, j) =>
                    j % 2 === 1
                      ? <strong key={j} className="text-amber-300 font-bold">{part}</strong>
                      : <span key={j}>{part}</span>
                  )
                  return (
                    <p key={i} className={`leading-relaxed ${isHeading ? 'text-white/90 text-base' : 'text-white/55 text-sm'}`}>
                      {rendered}
                    </p>
                  )
                })}
              </div>
              <div className="mt-8 pt-6 flex items-center justify-between"
                style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}>
                <button onClick={() => setActiveBlog(null)}
                  className="text-white/40 text-sm hover:text-white transition-colors">← Back to Blog</button>
                <button onClick={user ? onStartPlanning : openSignup}
                  className="text-sm px-6 py-2.5 rounded-xl font-black text-white transition-all hover:scale-105"
                  style={{ background: 'linear-gradient(135deg,#f59e0b,#ea580c)' }}>
                  Plan Your Trip Now →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── CTA BANNER ───────────────────────────────────────── */}
      <section className="relative py-32 px-6 text-center overflow-hidden">
        {/* Slideshow background for CTA too */}
        <div className="absolute inset-0">
          <div style={{
            position: 'absolute', inset: 0,
            backgroundImage: `url(https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1600&q=80)`,
            backgroundSize: 'cover', backgroundPosition: 'center',
          }} />
          <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, rgba(6,9,24,0.88) 0%, rgba(20,10,50,0.82) 50%, rgba(6,9,24,0.92) 100%)' }} />
          <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-20 pointer-events-none"
            style={{ background: 'radial-gradient(circle, #f59e0b, transparent)' }} />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-15 pointer-events-none"
            style={{ background: 'radial-gradient(circle, #a78bfa, transparent)' }} />
        </div>
        <div className="relative z-10 max-w-3xl mx-auto">
          <div className="text-7xl mb-6" style={{ animation: 'float 4s ease-in-out infinite' }}>🌍</div>
          <h2 className="font-outfit font-black text-white text-5xl md:text-6xl mb-5 leading-tight">
            Ready for Your<br /><span className="text-gold-gradient">Next Adventure?</span>
          </h2>
          <p className="text-white/60 text-lg mb-10 max-w-xl mx-auto leading-relaxed">
            Join thousands of travelers. Create your AI-powered itinerary in seconds — completely free.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button onClick={user ? onStartPlanning : openSignup}
              className="font-black text-lg px-14 py-5 rounded-2xl text-white transition-all hover:-translate-y-1 hover:scale-105"
              style={{ background: 'linear-gradient(135deg, #f59e0b, #ea580c)', boxShadow: '0 0 50px rgba(245,158,11,0.5)' }}>
              ✨ Start Planning Free
            </button>
            {!user && (
              <button onClick={openLogin}
                className="text-lg px-14 py-5 rounded-2xl font-bold text-white transition-all hover:-translate-y-1"
                style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.2)', backdropFilter: 'blur(8px)' }}>
                Sign In →
              </button>
            )}
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────── */}
      <footer style={{ background: '#030510', borderTop: '1px solid rgba(255,255,255,0.05)' }} className="pt-16 pb-8 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-14">
            {/* Brand */}
            <div className="md:col-span-1">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">✈️</span>
                <div>
                  <div className="font-outfit font-black text-white text-lg leading-none">Smart Travel Planner</div>
                  <div className="text-amber-400/50 text-[10px] font-semibold uppercase tracking-wider mt-0.5">AI-Powered Itineraries</div>
                </div>
              </div>
              <p className="text-white/35 text-sm leading-relaxed">
                Plan smarter trips with AI. Real places, accurate budgets, weather-aware itineraries in under 30 seconds.
              </p>
              <div className="flex gap-3 mt-5">
                {['𝕏', 'in', 'ig', 'yt'].map((s, i) => (
                  <div key={i} className="w-9 h-9 rounded-xl flex items-center justify-center text-white/50 text-xs font-bold cursor-pointer hover:text-amber-400 transition-colors"
                    style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}>{s}</div>
                ))}
              </div>
            </div>
            {/* Product */}
            <div>
              <h4 className="font-outfit font-bold text-white text-sm mb-4 uppercase tracking-widest">Product</h4>
              <ul className="space-y-3 text-white/40 text-sm">
                {['Features', 'How It Works', 'Destinations', 'Pricing', 'Changelog'].map(l => (
                  <li key={l}><a href="#" className="hover:text-amber-300 transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            {/* Destinations */}
            <div>
              <h4 className="font-outfit font-bold text-white text-sm mb-4 uppercase tracking-widest">Top Destinations</h4>
              <ul className="space-y-3 text-white/40 text-sm">
                {['Goa, India', 'Paris, France', 'Bali, Indonesia', 'Tokyo, Japan', 'Dubai, UAE'].map(l => (
                  <li key={l}><a href="#" className="hover:text-amber-300 transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
            {/* Support */}
            <div>
              <h4 className="font-outfit font-bold text-white text-sm mb-4 uppercase tracking-widest">Company</h4>
              <ul className="space-y-3 text-white/40 text-sm">
                {['About Us', 'Blog', 'Privacy Policy', 'Terms of Service', 'Contact'].map(l => (
                  <li key={l}><a href="#" className="hover:text-amber-300 transition-colors">{l}</a></li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bottom bar */}
          <div className="pt-8 flex flex-col md:flex-row items-center justify-between gap-4"
            style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <p className="text-white/25 text-xs">© 2025 Smart Travel Planner · Built with ❤️ using Gemini AI + FastAPI + React</p>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-white/30 text-xs">All systems operational</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
