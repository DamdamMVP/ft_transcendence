import { ref } from 'vue'

const themes = {
  light: {
    '--background-color': '#f0f0f0',
    '--text-color': '#333',
    '--primary-color': '#007bff',
    '--secondary-color': '#6c757d',
    '--accent-color': '#f1c40f',
    '--error-color': '#e74c3c',
    '--success-color': '#2ecc71',
    '--warning-color': '#f39c12',
    '--info-color': '#3498db',
    '--primary-hover-color': '#0056b3',
    '--error-hover-color': '#c0392b',
  },
  dark: {
    '--background-color': '#1a1a1a',
    '--text-color': '#ffffff',
    '--primary-color': '#3498db',
    '--secondary-color': '#95a5a6',
    '--accent-color': '#f39c12',
    '--error-color': '#e74c3c',
    '--success-color': '#2ecc71',
    '--warning-color': '#f39c12',
    '--info-color': '#3498db',
    '--primary-hover-color': '#2980b9',
    '--error-hover-color': '#c0392b',
  },
  forest: {
    '--background-color': '#2c3e50',
    '--text-color': '#ecf0f1',
    '--primary-color': '#27ae60',
    '--secondary-color': '#95a5a6',
    '--accent-color': '#e67e22',
    '--error-color': '#c0392b',
    '--success-color': '#27ae60',
    '--warning-color': '#f39c12',
    '--info-color': '#2980b9',
    '--primary-hover-color': '#219a52',
    '--error-hover-color': '#962c22',
  },
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

  // Appliquer le thème initial
  setTheme(currentTheme.value)

  return {
    setTheme,
    getAvailableThemes,
    getCurrentTheme,
    currentTheme,
  }
}
