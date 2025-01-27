import { createI18n } from 'vue-i18n'

// Fonction pour charger les fichiers JSON de manière dynamique
function loadLocaleMessages() {
  const locales = import.meta.glob('./src/langues/*.json', { eager: true }) // Chargement des fichiers JSON
  const messages = {}
  for (const path in locales) {
    const locale = path.match(/([A-Za-z0-9-_]+)\.json$/i)[1] // Récupérer le code langue (ex : "en" ou "fr")
    messages[locale] = locales[path].default
  }
  return messages
}

const i18n = createI18n({
  legacy: false, // Utiliser l'API Composition
  locale: localStorage.getItem('language') || 'fr', // Langue par défaut
  fallbackLocale: 'en',
  globalInjection: true, // Permet d'utiliser $t directement dans les composants
  messages: loadLocaleMessages(), // Charger les messages dynamiquement
})

export default i18n
