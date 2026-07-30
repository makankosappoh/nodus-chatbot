/**
 * services/api.js
 * ---------------
 * All HTTP calls to the FastAPI backend live here.
 * Components never import axios directly — they use these functions.
 */

import axios from 'axios'

// In development: Vite proxy forwards /api → localhost:8000
// In production: set VITE_API_URL in your Vercel environment variables
const BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
    baseURL: BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
})

// ── Non-streaming chat (use for testing) ──────────────────
export async function sendMessageSync(sessionId, message) {
    const { data } = await api.post('/api/chat/sync', {
        session_id: sessionId,
        message,
    })
    return data  // { session_id, reply, intent, sources }
}

// ── Lead submission ───────────────────────────────────────────────────────────
export async function submitLead(payload) {
    // payload: { session_id, name, email, phone?, requirement }
    const { data } = await api.post('/api/lead/', payload)
    return data  // { success, lead_id, message }
}

// ── Health check ──────────────────────────────────────────────────────────────
export async function healthCheck() {
    const { data } = await api.get('/health')
    return data
}

// ── Clear session ─────────────────────────────────────────────────────────────
export async function clearSession(sessionId) {
    await api.delete(`/api/chat/${sessionId}`)
}

export default api