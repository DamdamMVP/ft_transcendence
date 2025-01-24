<script setup>
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'

const { locale } = useI18n() // Utilisation de vue-i18n pour gérer la langue
const currentLanguage = ref(locale.value) // Langue actuelle

function changeLanguage(lng) {
  locale.value = lng // Met à jour la langue dans vue-i18n
}
</script>

<template>
  <div class="language-selector">
    <select v-model="currentLanguage" @change="changeLanguage(currentLanguage)">
      <option value="en">English</option>
      <option value="fr">Français</option>
    </select>
  </div>
</template>

<style scoped>
.language-selector {
  margin: 0 12px;
}

.language-selector select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid var(--secondary-color);
  background: var(--background-color);
  color: var(--text-color);
  cursor: pointer;
  font-family: Inter, sans-serif;
  transition: all 0.3s ease;
}

.language-selector select:hover {
  border-color: var(--primary-color);
}

.language-selector select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-alpha);
}

.language-selector option {
  background: var(--background-color);
  color: var(--text-color);
  padding: 8px;
}
</style>
