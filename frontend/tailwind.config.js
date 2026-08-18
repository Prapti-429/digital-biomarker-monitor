/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        nuvyra: {
          bg: '#0B0F17',
          surface: '#111827',
          card: '#161F30',
          border: '#1E293B',
          muted: '#64748B',
          text: '#F8FAFC',
          accent: '#0EA5E9',
          teal: '#14B8A6',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#F43F5E'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      letterSpacing: {
        brand: '0.12em',
      }
    },
  },
  plugins: [],
};