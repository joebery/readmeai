/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      colors: {
        bg: "#0a0c10",
        surface: "#10141c",
        surface2: "#161b26",
        border: "#1e2636",
        border2: "#2a3448",
        accent: "#3de87a",
        accent2: "#00c4ff",
        accent3: "#ff6b35",
        muted: "#6b7a99",
      },
    },
  },
  plugins: [],
};