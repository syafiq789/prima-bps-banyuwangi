/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'navy-main': '#142B4A',
        'navy-dark': '#0D1B2A',
        'navy-light': '#1E3E66',
        'orange-prima': '#F28C28',
        'orange-hover': '#D9771C',
        'light-bg': '#F4F6F9',
        'border-light': '#E2E8F0',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(13, 27, 42, 0.06), 0 2px 6px -1px rgba(13, 27, 42, 0.04)',
        'card': '0 10px 25px -5px rgba(20, 43, 74, 0.07), 0 8px 10px -6px rgba(20, 43, 74, 0.03)',
      }
    },
  },
  plugins: [],
}

