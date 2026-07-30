/**
 * TypingIndicator.jsx
 * Shows animated dots while the bot is generating a response.
 */

export default function TypingIndicator() {
    return (
        <div className="flex items-end gap-2 mb-3 animate-fade-in">
            {/* Bot avatar */}
            <div className="w-7 h-7 rounded-full bg-brand-primary flex items-center justify-center flex-shrink-0 text-white text-xs font-semibold">
                N
            </div>
            {/* Dots bubble */}
            <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1 items-center h-4">
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce-dots" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce-dots" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce-dots" style={{ animationDelay: '300ms' }} />
                </div>
            </div>
        </div>
    )
}