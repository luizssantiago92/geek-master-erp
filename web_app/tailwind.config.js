/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#ea580c", // Laranja estilo referência
        dark: "#171717", // Preto
        light: "#fafafa", // Branco
        accent: "#fbbf24", // Amarelão
      }
    },
  },
  plugins: [],
}
