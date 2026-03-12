/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{svelte,js,ts}', './index.html'],
  theme: {
    extend: {
      colors: {
        bg:       '#0e0e12',
        surface:  '#16161d',
        surface2: '#1e1e28',
        border:   '#2a2a38',
        accent:   '#6c63ff',
        'accent-hover': '#857cff',
        text:     '#e8e8f0',
        'text-sub': '#7878a0',
        bubble:   '#1e1e2e',
      },
    },
  },
  plugins: [],
}
