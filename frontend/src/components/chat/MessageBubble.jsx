export default function MessageBubble({ message }) {
const isUser = message.role === 'user'
const isStreaming = message.streaming

const timeStr = message.timestamp
? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
: ''

// Clean up response text
const cleanContent = (text) => {
if (!text) return ''
return text
    .replace(/\[DONE\]/g, '')
    .replace(/\*\*/g, '')
    .replace(/\*/g, '• ')
    .replace(/#+\s/g, '')
    .trim()
}

if (isUser) {
return (
    <div className="flex justify-end mb-3 animate-slide-up">
    <div className="max-w-[75%]">
        <div className="bg-brand-primary text-white rounded-2xl rounded-br-sm px-4 py-2.5 shadow-sm">
        <p className="text-sm leading-relaxed">{message.content}</p>
        </div>
        <p className="text-xs text-gray-400 text-right mt-1 mr-1">{timeStr}</p>
    </div>
    </div>
)
}

return (
<div className="flex items-end gap-2 mb-3 animate-slide-up">
    <div className="w-7 h-7 rounded-full bg-brand-primary flex-shrink-0 flex items-center justify-center text-white text-xs font-semibold self-end mb-5">
    N
    </div>

    <div className="max-w-[80%]">
    <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-2.5 shadow-sm">
        <div className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
        {cleanContent(message.content)}
        {isStreaming && (
            <span className="inline-block w-0.5 h-4 bg-brand-primary ml-0.5 animate-pulse align-middle" />
        )}
        </div>
    </div>
    <p className="text-xs text-gray-400 mt-1 ml-1">{timeStr}</p>
    </div>
</div>
)
}