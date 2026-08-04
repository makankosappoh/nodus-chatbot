import { useState, useCallback, useEffect, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useStream } from './useStream'

const QUICK_REPLIES = [
'What is Nodus Decoded?',
'What services do you offer?',
'How do I get started?',
]

function getOrCreateSessionId() {
const key = 'nodus_session_id'
let id = localStorage.getItem(key)
if (!id) {
id = uuidv4()
localStorage.setItem(key, id)
}
return id
}

// Browser TTS speak function — used to speak bot responses aloud
function speakText(text) {
if (!window.speechSynthesis) return
window.speechSynthesis.cancel()
const utterance = new SpeechSynthesisUtterance(text)
utterance.rate = 1.0
utterance.pitch = 1.0
utterance.volume = 1.0
window.speechSynthesis.speak(utterance)
}

export function useChat() {
const sessionId = useRef(getOrCreateSessionId())
const messagesEndRef = useRef(null)
const { stream, cancel } = useStream()

// user info state
const [userInfo, setUserInfo] = useState({ name: '', email: '' })
const [userInfoSubmitted, setUserInfoSubmitted] = useState(false)

// voice auto-speak toggle — user can turn this on/off
const [voiceEnabled, setVoiceEnabled] = useState(false)

// chat state
const [messages, setMessages] = useState([
{
    id: 'welcome',
    role: 'assistant',
    content: "Hi! 👋 Welcome to Nodus Decoded. Please enter your name and email to get started.",
    timestamp: new Date(),
}
])
const [isStreaming, setIsStreaming] = useState(false)
const [quickReplies, setQuickReplies] = useState([])
const [error, setError] = useState(null)

useEffect(() => {
messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [messages])

// submit user info — saves to backend and unlocks chat
const submitUserInfo = useCallback(async (name, email) => {
if (!name.trim() || !email.trim()) return

setUserInfo({ name, email })

// Save lead to backend immediately on info submit
try {
    await fetch('/api/lead/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        session_id: sessionId.current,
        name: name.trim(),
        email: email.trim(),
        requirement: 'POC Chat User',
    })
    })
} catch (e) {
    console.error('Lead save failed:', e)
}

setUserInfoSubmitted(true)
setMessages(prev => [...prev, {
    id: uuidv4(),
    role: 'assistant',
    content: `Thanks ${name}! 😊 I'm Nodus AI. You can ask me anything about Nodus Decoded. Try one of the questions below.`,
    timestamp: new Date(),
}])
setQuickReplies(QUICK_REPLIES)
}, [])

const sendMessage = useCallback(async (text) => {
if (!text.trim() || isStreaming || !userInfoSubmitted) return

setError(null)
setQuickReplies([])

const userMsg = {
    id: uuidv4(),
    role: 'user',
    content: text.trim(),
    timestamp: new Date(),
}

const assistantMsgId = uuidv4()
const assistantMsg = {
    id: assistantMsgId,
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    streaming: true,
}

setMessages(prev => [...prev, userMsg, assistantMsg])
setIsStreaming(true)

let fullContent = ''

await stream(
    sessionId.current,
    text.trim(),
    (token) => {
    fullContent += token
    setMessages(prev =>
        prev.map(m =>
        m.id === assistantMsgId
            ? { ...m, content: fullContent }
            : m
        )
    )
    },
    () => {
    setMessages(prev =>
        prev.map(m =>
        m.id === assistantMsgId
            ? { ...m, streaming: false }
            : m
        )
    )
    setIsStreaming(false)
    setQuickReplies(QUICK_REPLIES)

    // Auto speak bot response if voice enabled
    if (voiceEnabled && fullContent) {
        speakText(fullContent)
    }
    },
    () => {
    setIsStreaming(false)
    setError('Connection issue. Please try again.')
    setMessages(prev =>
        prev.map(m =>
        m.id === assistantMsgId
            ? { ...m, content: 'Sorry, something went wrong. Please try again.', streaming: false }
            : m
        )
    )
    }
)
}, [isStreaming, stream, userInfoSubmitted, voiceEnabled])

const clearChat = useCallback(() => {
const newId = uuidv4()
localStorage.setItem('nodus_session_id', newId)
sessionId.current = newId
setMessages([{
    id: 'welcome',
    role: 'assistant',
    content: "Hi! 👋 Welcome to Nodus Decoded. Please enter your name and email to get started.",
    timestamp: new Date(),
}])
setQuickReplies([])
setUserInfoSubmitted(false)
setUserInfo({ name: '', email: '' })
setError(null)
window.speechSynthesis?.cancel()
}, [])

return {
messages,
isStreaming,
quickReplies,
error,
messagesEndRef,
sendMessage,
cancelStream: cancel,
clearChat,
sessionId: sessionId.current,
userInfo,
userInfoSubmitted,
submitUserInfo,
voiceEnabled,
setVoiceEnabled,
}
}