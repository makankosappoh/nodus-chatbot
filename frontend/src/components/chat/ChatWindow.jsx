/**
 * ChatWindow.jsx
 * --------------
 * The main chat panel: header + message list + quick replies + input.
 * Receives all state from useChat() via props — this component is purely presentational.
 */
import UserInfoForm from './UserInfoForm'
import MessageBubble from './MessageBubble'
import QuickReplies from './QuickReplies'
import ChatInput from './ChatInput'
import TypingIndicator from '../ui/TypingIndicator'

export default function ChatWindow({
messages,
isStreaming,
quickReplies,
error,
messagesEndRef,
onSend,
onClear,
onClose,
userInfoSubmitted,
onSubmitUserInfo,
}) {
// Show typing indicator only if streaming AND the last assistant message is empty
const lastMsg = messages[messages.length - 1]
const showTyping = isStreaming && lastMsg?.role === 'assistant' && !lastMsg.content

return (
    <div className="flex flex-col h-full bg-gray-50 rounded-2xl overflow-hidden shadow-2xl border border-gray-200">

        {/* ── Header ─────────────────────────────────────────────────────────── */}
        <div className="bg-brand-primary px-4 py-3 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-2.5">
                {/* Bot avatar */}
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white font-semibold text-sm">
                    N
                </div>
                <div>
                    {/* ← Replace with Nodus Decoded actual bot name */}
                    <p className="text-white font-medium text-sm leading-tight">Nodus AI</p>
                    <div className="flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                        <span className="text-white/70 text-xs">Online · Typically replies instantly</span>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-1">
                {/* Clear chat button */}
                <button
                    onClick={onClear}
                    title="Clear conversation"
                    className="p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors"
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                </button>
                {/* Close button */}
                <button
                    onClick={onClose}
                    title="Close chat"
                    className="p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors"
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>

        {/* ── Message list ────────────────────────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto px-3 pt-4 pb-2 scroll-smooth">
            {messages.map(message => (
                <MessageBubble key={message.id} message={message} />
            ))}

            {/* Typing indicator shows while stream starts but content is empty */}
            {showTyping && <TypingIndicator />}

            {/* Error banner */}
            {error && (
                <div className="text-xs text-red-500 bg-red-50 border border-red-100 rounded-lg px-3 py-2 mb-2 text-center">
                    {error}
                </div>
            )}

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
        </div>

        {/* ── Quick replies ────────────────────────────────────────────────────── */}
        <QuickReplies
        replies={quickReplies}
        onSelect={onSend}
        disabled={isStreaming}
        />


        {userInfoSubmitted ? (
        <ChatInput onSend={onSend} disabled={isStreaming} />
        ) : (
        <UserInfoForm onSubmit={onSubmitUserInfo} />
        )}

        {/* Branding footer */}
        <div className="text-center pb-2 pt-0.5 bg-white">
            <span className="text-[10px] text-gray-300">Powered by Nodus Decoded AI</span>
        </div>
    </div>
)
}