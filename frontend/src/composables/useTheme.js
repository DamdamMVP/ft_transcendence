import { ref } from 'vue'

const themes = {
  light: {
    '--background-color': '#f0f0f0',
    '--background-color-secondary': '#ffffff',
    '--text-color': '#333',
    '--text-color-secondary': '#666',
    '--primary-color': '#007bff',
    '--secondary-color': '#6c757d',
    '--accent-color': '#f1c40f',
    '--error-color': '#e74c3c',
    '--success-color': '#2ecc71',
    '--warning-color': '#f39c12',
    '--info-color': '#3498db',
    '--primary-hover-color': '#0056b3',
    '--error-hover-color': '#c0392b',
    '--border-color': '#e0e0e0',
	'--primary-shadow-color': 'rgba(0, 123, 255, 0.3)'
  },
  dark: {
    '--background-color': '#1a1a1a',
    '--background-color-secondary': '#2d2d2d',
    '--text-color': '#ffffff',
    '--text-color-secondary': '#aaaaaa',
    '--primary-color': '#3498db',
    '--secondary-color': '#95a5a6',
    '--accent-color': '#f39c12',
    '--error-color': '#e74c3c',
    '--success-color': '#2ecc71',
    '--warning-color': '#f39c12',
    '--info-color': '#3498db',
    '--primary-hover-color': '#2980b9',
    '--error-hover-color': '#c0392b',
    '--border-color': '#404040',
	'--primary-shadow-color': 'rgba(52, 152, 219, 0.3)'
  },
  forest: {
    '--background-color': '#2c3e50',
    '--background-color-secondary': '#34495e',
    '--text-color': '#ecf0f1',
    '--text-color-secondary': '#bdc3c7',
    '--primary-color': '#27ae60',
    '--secondary-color': '#95a5a6',
    '--accent-color': '#e67e22',
    '--error-color': '#c0392b',
    '--success-color': '#27ae60',
    '--warning-color': '#f39c12',
    '--info-color': '#2980b9',
    '--primary-hover-color': '#219a52',
    '--error-hover-color': '#962c22',
	'--primary-shadow-color': 'rgba(39, 174, 96, 0.3)'
  },
  coffee: {
	'--background-color': '#F5E6D3',
    '--background-color-secondary': '#FFF8E7',
    '--text-color': '#2C1810',
    '--text-color-secondary': '#5D4037',
    '--primary-color': '#795548',
    '--secondary-color': '#8D6E63',
    '--accent-color': '#A1887F',
    '--error-color': '#EF5350',
    '--success-color': '#66BB6A',
    '--warning-color': '#FFA726',
    '--info-color': '#42A5F5',
    '--primary-hover-color': '#5D4037',
    '--error-hover-color': '#E53935',
    '--border-color': '#D7CCC8',
    '--primary-shadow-color': 'rgba(121, 85, 72, 0.2)'
  },
  neon: {
	'--background-color': '#1B0B2B',
    '--background-color-secondary': '#2D1B42',
    '--text-color': '#FF7ED4',
    '--text-color-secondary': '#7EE8FA',
    '--primary-color': '#EF709D',
    '--secondary-color': '#FAE8E0',
    '--accent-color': '#89CFF0',
    '--error-color': '#FF2E63',
    '--success-color': '#98FB98',
    '--warning-color': '#FFA07A',
    '--info-color': '#87CEEB',
    '--primary-hover-color': '#D84E7F',
    '--error-hover-color': '#E61A4D',
    '--border-color': '#432C44',
    '--primary-shadow-color': 'rgba(239, 112, 157, 0.3)'
  },
  mint: {
	'--background-color': '#081C15',
    '--background-color-secondary': '#1B4332',
    '--text-color': '#D8F3DC',
    '--text-color-secondary': '#95D5B2',
    '--primary-color': '#40916C',
    '--secondary-color': '#52B788',
    '--accent-color': '#74C69D',
    '--error-color': '#FF686B',
    '--success-color': '#2D6A4F',
    '--warning-color': '#FFB703',
    '--info-color': '#48CAE4',
    '--primary-hover-color': '#2D6A4F',
    '--error-hover-color': '#FF4D4F',
    '--border-color': '#2D6A4F',
    '--primary-shadow-color': 'rgba(64, 145, 108, 0.3)'
  }
}

const currentTheme = ref(localStorage.getItem('theme') || 'dark')

export function useTheme() {
  const setTheme = (themeName) => {
    if (themes[themeName]) {
      const root = document.documentElement
      Object.entries(themes[themeName]).forEach(([property, value]) => {
        root.style.setProperty(property, value)
      })
      currentTheme.value = themeName
      localStorage.setItem('theme', themeName)
    }
  }

  const getAvailableThemes = () => Object.keys(themes)

  const getCurrentTheme = () => currentTheme.value

  // Apply initial theme
  setTheme(currentTheme.value)

  return {
    setTheme,
    getAvailableThemes,
    getCurrentTheme,
    currentTheme,
  }
}
