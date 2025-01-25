<script setup>
import { useI18n } from 'vue-i18n'
import { ref, defineEmits } from 'vue'

const emit = defineEmits(['update:language'])
const { locale } = useI18n() // Utilisation de vue-i18n pour gérer la langue
const selectedLanguage = ref(locale.value) // Langue actuelle

const onLanguageChange = (lang) => {
  selectedLanguage.value = lang
  emit('update:language', lang)
}
</script>

<template>
  <div class="language-selector">
    <select
      v-model="selectedLanguage"
      @change="onLanguageChange(selectedLanguage)"
      class="select-field"
    >
      <option value="en">English</option>
      <option value="fr">Français</option>
    </select>
  </div>
</template>

<style scoped>
.language-selector {
  width: 100%;
}

.select-field {
  padding: 8px 12px;
  background: var(--background-color);
  border: 2px solid var(--secondary-color);
  border-radius: 4px;
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  cursor: pointer;
  width: 100%;
  box-sizing: border-box;
}

.select-field:hover {
  border-color: var(--primary-color);
}

.select-field:focus {
  border-color: var(--info-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

option {
  background: var(--background-color);
  color: var(--text-color);
  padding: 8px;
}
</style>
