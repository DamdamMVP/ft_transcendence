import { createI18n } from 'vue-i18n'

function loadLocaleMessages() {
  const locales = import.meta.glob('./src/langues/*.json', { eager: true })
  const messages = {}
  for (const path in locales) {
    const locale = path.match(/([A-Za-z0-9-_]+)\.json$/i)[1]
    messages[locale] = locales[path].default
  }
  return messages
}

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('language') || 'fr',
  fallbackLocale: 'en',
  globalInjection: true,
  messages: loadLocaleMessages(),
})

export default i18n
