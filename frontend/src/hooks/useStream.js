import { useRef, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || ''

export function useStream() {
const abortRef = useRef(null)

const stream = useCallback(async (sessionId, message, onToken, onDone, onError) => {
if (abortRef.current) {
    abortRef.current.abort()
}
abortRef.current = new AbortController()

try {
    const response = await fetch(`${API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
    signal: abortRef.current.signal,
    })

    if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
        if (line.startsWith('data: ')) {
        const data = line.slice(6)
        
        if (data.includes('[DONE]')) {
            const cleanData = data.replace('[DONE]', '').trim()
            if (cleanData) {
                onToken(cleanData)
            }
            onDone()
            return
        }
        if (data) {
            onToken(data)
        }
        }
    }
    }

    onDone()
} catch (err) {
    if (err.name === 'AbortError') return
    console.error('Stream error:', err)
    onError(err)
}
}, [])

const cancel = useCallback(() => {
abortRef.current?.abort()
}, [])

return { stream, cancel }
}