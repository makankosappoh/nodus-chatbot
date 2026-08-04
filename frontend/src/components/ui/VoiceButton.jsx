/**
 * VoiceButton.jsx
 * ---------------
 * Mic button that shows recording/transcribing state.
 */

export default function VoiceButton({
isRecording,
isTranscribing,
onStart,
onStop,
disabled
}) {
function handleClick() {
if (isRecording) {
    onStop()
} else {
    onStart()
}
}

return (
<button
    onClick={handleClick}
    disabled={disabled || isTranscribing}
    title={isRecording ? 'Stop recording' : 'Start voice input'}
    className={`
    w-9 h-9 rounded-xl flex-shrink-0
    flex items-center justify-center
    transition-all duration-150
    ${isRecording
        ? 'bg-red-500 text-white animate-pulse'
        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
    }
    ${isTranscribing ? 'opacity-50 cursor-not-allowed' : ''}
    disabled:opacity-40 disabled:cursor-not-allowed
    `}
>
    {isTranscribing ? (
    // Spinner while transcribing
    <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
    </svg>
    ) : isRecording ? (
    // Stop icon when recording
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
        <rect x="6" y="6" width="12" height="12" rx="2"/>
    </svg>
    ) : (
    // Mic icon
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
        <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>
        <path d="M19 10v2a7 7 0 01-14 0v-2H3v2a9 9 0 008 8.94V23h2v-2.06A9 9 0 0021 12v-2h-2z"/>
    </svg>
    )}
</button>
)
}