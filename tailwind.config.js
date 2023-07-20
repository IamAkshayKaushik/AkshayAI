/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // "**/templates/**/*.{html,js}",
    "./*/templates/core/*.{html,js}",
    "./templates/*.{html,js}",
    "./node_modules/tw-elements/dist/js/**/*.js",
  ],
  theme: {
    extend: {},
  },
  darkMode: "class",
  plugins: [require("tw-elements/dist/plugin.cjs")],
};
