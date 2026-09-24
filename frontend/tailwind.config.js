/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        heritage: {
          bg: '#0D0B08',
          bgLight: '#14100C',
          card: '#1A140F',
          cardHover: '#231B14',
          border: 'rgba(212, 175, 55, 0.2)',
          gold: '#D4AF37',
          goldLight: '#F3E5AB',
          goldBright: '#E6C280',
          teal: '#14B8A6',
          tealLight: '#2DD4BF',
          tealDark: '#0F766E',
          text: '#E8DCC4',
          textMuted: '#A09382',
          heading: '#FFF5E4'
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
        serifHeading: ['Cinzel', 'serif'],
        tamilSerif: ['Noto Serif Tamil', 'serif'],
        tamilSans: ['Noto Sans Tamil', 'sans-serif'],
      },
      boxShadow: {
        'gold-glow': '0 0 25px -5px rgba(212, 175, 55, 0.15)',
        'teal-glow': '0 0 25px -5px rgba(20, 184, 166, 0.2)',
      }
    },
  },
  plugins: [],
}
