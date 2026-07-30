/**
 * QuickReplies.jsx
 * ----------------
 * Renders clickable suggestion chips below the message list.
 * Disappears while bot is streaming, reappears with contextual suggestions.
 */

export default function QuickReplies({ replies, onSelect, disabled }) {
    if (!replies || replies.length === 0) return null

    return (
        <div className="px-3 pb-2 flex flex-wrap gap-2 animate-fade-in">
            {replies.map((reply, i) => (
                <button
                    key={i}
                    onClick={() => !disabled && onSelect(reply)}
                    disabled={disabled}
                    className="
            text-xs px-3 py-1.5 rounded-full border border-brand-primary
            text-brand-primary bg-white
            hover:bg-brand-light hover:border-brand-secondary
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-colors duration-150
            whitespace-nowrap
            "
                >
                    {reply}
                </button>
            ))}
        </div>
    )
}