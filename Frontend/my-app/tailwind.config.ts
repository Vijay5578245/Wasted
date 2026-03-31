import type { Config } from 'tailwindcss'

export default {
  content: [
    './app/**/*.{vue,ts}',
    './components/**/*.{vue,ts}',
    './pages/**/*.vue',
  ],
  theme: {
    extend: {
      colors: {
        void: {
          50:  '#f4f0ff',
          100: '#ede5ff',
          200: '#ddd0ff',
          300: '#c4adff',
          400: '#a87dff',
          500: '#8b4cf7',
          600: '#7c2de8',
          700: '#6b1fd0',
          800: '#581aaa',
          900: '#3d1278',
          950: '#1e0840',
        },
        abyss: {
          50:  '#f0eeff',
          100: '#e4e0ff',
          200: '#ccc4ff',
          300: '#ad9cff',
          400: '#8a6aff',
          500: '#6b3fff',
          600: '#5a1ff0',
          700: '#4c14d6',
          800: '#3f10af',
          900: '#2d0d7a',
          950: '#120540',
        },
        ink: {
          50:  '#f5f3ff',
          100: '#ede9ff',
          200: '#d8d0ff',
          300: '#b8aae0',
          400: '#8f83b5',
          500: '#665f87',
          600: '#463f5e',
          700: '#2c2840',
          800: '#1a1728',
          900: '#0e0c18',
          950: '#07050f',
        },
      },
      fontFamily: {
        cormorant: ['"Cormorant Garamond"', 'serif'],
        inter: ['Inter', 'sans-serif'],
      },
      letterSpacing: {
        ultra: '0.35em',
        extreme: '0.55em',
      },
      fontSize: {
        'counter': ['clamp(4.5rem, 9vw, 8.5rem)', { lineHeight: '1', letterSpacing: '-0.02em' }],
        'counter-sm': ['clamp(2.5rem, 5vw, 4.5rem)', { lineHeight: '1' }],
      },
    },
  },
} satisfies Config
