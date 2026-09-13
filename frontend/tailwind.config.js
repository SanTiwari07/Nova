/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"Amazon Ember"',
          '"Helvetica Neue"',
          'Roboto',
          'Arial',
          'sans-serif'
        ],
      },
    },
  },
  plugins: [],
}
