/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          primary: '#212121',
          secondary: '#171717',
          tertiary: '#2A2B2D',
          quaternary: '#343536',
        },
        text: {
          primary: '#ECECF1',
          secondary: '#A0A0AB',
          tertiary: '#6E6E80',
        },
        accent: {
          primary: '#10A37F',
          user: '#4ECDC4',
          ai: '#5436DA',
        },
        border: {
          primary: '#353740',
          secondary: '#444654',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['Söhne Mono', 'Monaco', 'Andale Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-subtle': 'pulseSubtle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}