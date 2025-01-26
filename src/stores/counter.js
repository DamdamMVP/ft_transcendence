import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useLangStore = defineStore('lang', () => {
  const lang = ref('en')
  const setLang = (newLang) => {
    lang.value = newLang
  }

  return { count, doubleCount, increment }
})
