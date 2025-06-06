/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#1a1a1a',
          chat: '#2d2d2d',
          sidebar: '#252525',
          input: '#3d3d3d',
          border: '#404040',
          text: '#e0e0e0',
          accent: '#4CAF50',
        }
      }
    },
  },
  plugins: [],
} 