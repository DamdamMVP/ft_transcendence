import { createI18n } from 'vue-i18n'
import fr from './langues/fr.json'
import en from './langues/en.json'
import ru from './langues/ru.json'
import br from './langues/br.json'

export default createI18n({
  legacy: false,
  locale: localStorage.getItem('language') || 'fr',
  fallbackLocale: 'en',
  messages: {
    fr,
    en,
    ru,
    br
  }
})
