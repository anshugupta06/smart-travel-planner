// Central API base URL — reads from .env in development, Vercel env var in production
// In development: set VITE_API_URL=http://localhost:8000 in frontend/.env
// In production:  set VITE_API_URL=https://your-backend.onrender.com in Vercel dashboard
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
