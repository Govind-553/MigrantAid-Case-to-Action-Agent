/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary trustworthy blue/indigo family
        brand: {
          50: "#eef4ff",
          100: "#dbe6fe",
          200: "#bfd3fe",
          300: "#93b4fd",
          400: "#608df9",
          500: "#3b66f4",
          600: "#2547e9",
          700: "#1d34d6",
          800: "#1e2dad",
          900: "#1e2b88",
          950: "#171e53",
        },
        // Muted semantic palette
        success: {
          DEFAULT: "#16a34a",
          bg: "#ecfdf3",
          border: "#bbf7d0",
          text: "#14532d",
        },
        warning: {
          DEFAULT: "#d97706",
          bg: "#fffbeb",
          border: "#fde68a",
          text: "#78350f",
        },
        danger: {
          DEFAULT: "#dc2626",
          bg: "#fef2f2",
          border: "#fecaca",
          text: "#7f1d1d",
        },
        neutral_line: "#e2e8f0",
        surface: "#f8fafc",
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "'Segoe UI'",
          "Roboto",
          "Oxygen",
          "Ubuntu",
          "Cantarell",
          "'Open Sans'",
          "'Helvetica Neue'",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "'Liberation Mono'",
          "monospace",
        ],
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(15 23 42 / 0.04), 0 1px 3px 0 rgb(15 23 42 / 0.06)",
        'card-lg': "0 1px 3px 0 rgb(15 23 42 / 0.05), 0 8px 24px -6px rgb(15 23 42 / 0.08)",
        ring: "0 0 0 1px rgb(15 23 42 / 0.05)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.25s ease-out",
        "fade-in-up": "fade-in-up 0.3s ease-out",
      },
    },
  },
  plugins: [],
};
