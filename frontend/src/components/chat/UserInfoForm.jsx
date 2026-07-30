import { useState } from 'react'

export default function UserInfoForm({ onSubmit }) {
const [name, setName] = useState('')
const [email, setEmail] = useState('')
const [error, setError] = useState('')

function handleSubmit() {
if (!name.trim()) { setError('Please enter your name'); return }
if (!email.trim() || !email.includes('@')) { setError('Please enter a valid email'); return }
setError('')
onSubmit(name, email)
}

return (
<div className="px-4 py-3 bg-white border-t border-gray-100">
    <p className="text-xs text-gray-500 mb-2 font-medium">Enter your details to start chatting</p>
    <input
    type="text"
    placeholder="Your name"
    value={name}
    onChange={e => setName(e.target.value)}
    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-brand-primary"
    />
    <input
    type="email"
    placeholder="Your email"
    value={email}
    onChange={e => setEmail(e.target.value)}
    onKeyDown={e => e.key === 'Enter' && handleSubmit()}
    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-brand-primary"
    />
    {error && <p className="text-xs text-red-500 mb-2">{error}</p>}
    <button
    onClick={handleSubmit}
    className="w-full bg-brand-primary text-white rounded-lg py-2 text-sm font-medium hover:bg-brand-secondary transition-colors"
    >
    Start Chatting →
    </button>
</div>
)
}