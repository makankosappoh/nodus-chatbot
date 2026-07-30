/**
 * ChatBubble.jsx
 * --------------
 * The floating button in the bottom-right corner of the website.
 * Click to open/close the ChatWindow.
 * Shows an unread indicator dot when chat is closed.
 */

export default function ChatBubble({ isOpen, onClick, hasUnread }) {
    return (
        <button
            onClick={onClick}
            aria-label={isOpen ? 'Close chat' : 'Open chat'}
            className="
        w-14 h-14 rounded-full
        bg-brand-primary text-white
        shadow-lg hover:shadow-xl
        hover:scale-105 active:scale-95
        transition-all duration-200
        flex items-center justify-center
        relative
        "
        >
            {/* Unread dot */}
            {hasUnread && !isOpen && (
                <span className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-red-500 rounded-full border-2 border-white" />
            )}

            {/* Icon toggles between chat and close */}
            <span className={`transition-transform duration-200 ${isOpen ? 'rotate-0' : 'rotate-0'}`}>
                {isOpen ? (
                    // Close (X) icon
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="w-6 h-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                ) : (
                    // Chat bubble icon
                    <svg viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z" />
                    </svg>
                )}
            </span>
        </button>
    )
}