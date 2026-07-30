/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,jsx}'],
    theme: {
        extend: {
            // ← Replace these with Nodus Decoded brand colors when you have them
            colors: {
                brand: {
                    primary: '#2D6BE4',  // swap for Nodus primary brand color
                    secondary: '#1A4DB5',  // darker shade
                    accent: '#F59E0B',  // highlight / CTA color
                    light: '#EEF3FD',  // chat bubble background
                }
            },
            animation: {
                'fade-in': 'fadeIn 0.2s ease-out',
                'slide-up': 'slideUp 0.25s ease-out',
                'bounce-dots': 'bounceDots 1.2s infinite',
            },
            keyframes: {
                fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
                slideUp: { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
                bounceDots: {
                    '0%, 60%, 100%': { transform: 'translateY(0)' },
                    '30%': { transform: 'translateY(-5px)' }
                }
            }
        }
    },
    plugins: []
}
