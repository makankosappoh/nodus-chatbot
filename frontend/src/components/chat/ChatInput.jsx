/**
 * ChatInput.jsx
 * -------------
 * Message input bar at the bottom of the chat window.
 * Supports Enter to send, Shift+Enter for newline.
 * Auto-expands up to 4 lines.
 * Supports voice input via microphone.
 */

import { useState, useRef, useEffect } from 'react'
import VoiceButton from '../ui/VoiceButton'
import { useVoice } from '../../hooks/useVoice'

export default function ChatInput({ onSend, disabled }) {
const [value, setValue] = useState('')
const textareaRef = useRef(null)

const {
isRecording,
isTranscribing,
isSpeaking,
startRecording,
stopRecording,
stopSpeaking,
} = useVoice({
onTranscribed: (text) => {
    setValue(text)
    // Auto send after transcription
    setTimeout(() => textareaRef.current?.focus(), 100)
}
})

// Auto-resize textarea as user types
useEffect(() => {
const el = textareaRef.current
if (!el) return
el.style.height = 'auto'
el.style.height = Math.min(el.scrollHeight, 96) + 'px'  // max 4 lines ≈ 96px
}, [value])

function handleKeyDown(e) {
if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
}
}

function handleSend() {
const text = value.trim()
if (!text || disabled) return
onSend(text)
setValue('')
// Reset height
if (textareaRef.current) textareaRef.current.style.height = 'auto'
}

return (
<div className="border-t border-gray-100 px-3 py-2.5 bg-white">
    <div className="flex items-end gap-2">

    {/* Voice input button */}
    <VoiceButton
        isRecording={isRecording}
        isTranscribing={isTranscribing}
        onStart={startRecording}
        onStop={stopRecording}
        disabled={disabled}
    />

    <textarea
        ref={textareaRef}
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled || isRecording || isTranscribing}
        placeholder={
        isRecording ? 'Listening...' :
        isTranscribing ? 'Transcribing...' :
        'Ask about Nodus Decoded...'
        }
        rows={1}
        className="
        flex-1 resize-none rounded-xl border border-gray-200
        px-3 py-2 text-sm text-gray-800
        placeholder:text-gray-400
        focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent
        disabled:bg-gray-50 disabled:text-gray-400
        transition-all duration-150
        min-h-[38px] max-h-24
        "
    />

    <button
        onClick={handleSend}
        disabled={!value.trim() || disabled}
        aria-label="Send message"
        className="
        w-9 h-9 rounded-xl flex-shrink-0
        bg-brand-primary text-white
        hover:bg-brand-secondary
        disabled:opacity-40 disabled:cursor-not-allowed
        flex items-center justify-center
        transition-colors duration-150
        shadow-sm
        "
    >
        {/* Send icon */}
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
    </button>
    </div>

    {/* Speaking indicator */}
    {isSpeaking && (
    <div className="flex items-center gap-2 mt-1.5 px-1">
        <span className="text-xs text-brand-primary animate-pulse">
        🔊 Speaking...
        </span>
        <button
        onClick={stopSpeaking}
        className="text-xs text-gray-400 hover:text-gray-600 underline"
        >
        Stop
        </button>
    </div>
    )}

    <p className="text-xs text-gray-400 mt-1.5 px-1">
    Press Enter to send · Shift+Enter for new line · 🎤 tap mic for voice
    </p>
</div>
)
}