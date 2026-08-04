import { useState, useRef, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || ''

export function useVoice({ onTranscribed }) {
const [isRecording, setIsRecording] = useState(false)
const [isTranscribing, setIsTranscribing] = useState(false)
const [isSpeaking, setIsSpeaking] = useState(false)
const mediaRecorderRef = useRef(null)
const chunksRef = useRef([])

const startRecording = useCallback(async () => {
try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mediaRecorder = new MediaRecorder(stream)
    mediaRecorderRef.current = mediaRecorder
    chunksRef.current = []

    mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) chunksRef.current.push(e.data)
    }

    mediaRecorder.onstop = async () => {
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
    stream.getTracks().forEach(t => t.stop())
    await transcribeAudio(blob)
    }

    mediaRecorder.start()
    setIsRecording(true)
} catch (err) {
    console.error('Microphone error:', err)
    alert('Please allow microphone access to use voice input.')
}
}, [])

const stopRecording = useCallback(() => {
if (mediaRecorderRef.current && isRecording) {
    mediaRecorderRef.current.stop()
    setIsRecording(false)
}
}, [isRecording])

const transcribeAudio = useCallback(async (blob) => {
setIsTranscribing(true)
try {
    const formData = new FormData()
    formData.append('audio', blob, 'recording.webm')

    const response = await fetch(`${API_BASE}/api/voice/transcribe`, {
    method: 'POST',
    body: formData,
    })

    const data = await response.json()
    if (data.text) {
    // Just fill the input box — user decides to send or edit
    onTranscribed(data.text)
    }
} catch (err) {
    console.error('Transcription error:', err)
} finally {
    setIsTranscribing(false)
}
}, [onTranscribed])

const speak = useCallback((text) => {
if (!window.speechSynthesis) return
window.speechSynthesis.cancel()
const utterance = new SpeechSynthesisUtterance(text)
utterance.rate = 1.0
utterance.pitch = 1.0
utterance.volume = 1.0
utterance.onstart = () => setIsSpeaking(true)
utterance.onend = () => setIsSpeaking(false)
utterance.onerror = () => setIsSpeaking(false)
window.speechSynthesis.speak(utterance)
}, [])

const stopSpeaking = useCallback(() => {
window.speechSynthesis.cancel()
setIsSpeaking(false)
}, [])

return {
isRecording,
isTranscribing,
isSpeaking,
startRecording,
stopRecording,
speak,
stopSpeaking,
}
}