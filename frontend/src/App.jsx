/**
 * App.jsx
 * -------
 * Root component. Renders the floating chat widget on top of the website.
 *
 * The widget position (bottom-right) is fixed — it overlays whatever
 * page is behind it. When you integrate into the Next.js company website,
 * import and drop <ChatWidget /> into the root layout component.
 */

import { useState } from 'react'
import ChatBubble from './components/ui/ChatBubble'
import ChatWindow from './components/chat/ChatWindow'
import { useChat } from './hooks/useChat'
import './index.css'

function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false)

    const {
        messages,
        isStreaming,
        quickReplies,
        error,
        messagesEndRef,
        sendMessage,
        clearChat,
        userInfoSubmitted,
        submitUserInfo,
        voiceEnabled,
        setVoiceEnabled,
    } = useChat()

    function handleOpen() {
        setIsOpen(prev => !prev)
    }

    async function handleSend(text) {
        if (!isOpen) setIsOpen(true)
        await sendMessage(text)
    }

    return (
        // Fixed position — bottom-right of viewport, above all page content
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">

            {/* Chat panel — slides in when isOpen */}
            {isOpen && (
                <div className="
            w-[360px] h-[560px]
            animate-slide-up
            origin-bottom-right
        ">
                    <ChatWindow
                        messages={messages}
                        isStreaming={isStreaming}
                        quickReplies={quickReplies}
                        error={error}
                        messagesEndRef={messagesEndRef}
                        onSend={handleSend}
                        onClear={clearChat}
                        onClose={() => setIsOpen(false)}
                        userInfoSubmitted={userInfoSubmitted}
                        onSubmitUserInfo={submitUserInfo}
                        voiceEnabled={voiceEnabled}
                        onToggleVoice={() => setVoiceEnabled(prev => !prev)}
                    />
                </div>
            )}

            {/* Floating trigger button */}
            <ChatBubble
                isOpen={isOpen}
                onClick={handleOpen}
                hasUnread={!isOpen && messages.length === 1}  // show dot on first open hint
            />
        </div>
    )
}

export default function App() {
    return (
        <>
            {/*
        Your Next.js website pages render here.
        In the actual Next.js app, you'll move <ChatWidget /> to
        app/layout.jsx so it appears on every page.
        For this standalone React demo, just a placeholder.
      */}
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-center text-gray-500">
                    <h1 className="text-2xl font-semibold text-gray-700 mb-2">Nodus Decoded</h1>
                    <p className="text-sm">Company website goes here. Chat widget is bottom-right →</p>
                </div>
            </div>

            {/* Chat widget — drop this into Next.js layout.jsx */}
            <ChatWidget />
        </>
    )
}