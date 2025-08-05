/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0A0A0A',
          800: '#141414',
          700: '#1E1E1E',
          600: '#282828',
          500: '#323232',
        },
        accent: {
          green: '#10B981',
          red: '#EF4444',
          yellow: '#F59E0B',
          blue: '#3B82F6',
        }
      },
      fontFamily: {
        mono: ['Fira Code', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}