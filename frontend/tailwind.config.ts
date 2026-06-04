import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        hirebot: {
          green: '#1D9E75',
          'green-dark': '#0F6E56',
          'green-light': '#E1F5EE',
          'green-mid': '#9FE1CB',
          blue: '#378ADD',
          'blue-light': '#E6F1FB',
          amber: '#EF9F27',
          'amber-light': '#FAEEDA',
          rose: '#D4537E',
          'rose-light': '#FBEAF0',
        },
        surface: {
          primary: '#FFFFFF',
          secondary: '#F9FAFB',
          tertiary: '#F3F4F6',
        },
        border: {
          primary: '#E5E7EB',
          secondary: '#D1D5DB',
          tertiary: '#E5E7EB',
        },
        text: {
          primary: '#111827',
          secondary: '#6B7280',
          tertiary: '#9CA3AF',
        }
      },
      borderRadius: {
        md: '6px',
        lg: '8px',
        xl: '12px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
};

export default config;
