<script setup>
import { useTheme } from '../composables/useTheme'
import { ref } from 'vue'

const emit = defineEmits(['update:theme'])
const { getAvailableThemes, currentTheme } = useTheme()
const themes = getAvailableThemes()
const selectedTheme = ref(currentTheme.value)

const onThemeChange = (theme) => {
  selectedTheme.value = theme
  emit('update:theme', theme)
}
</script>

<template>
  <div class="theme-selector">
    <select v-model="selectedTheme" @change="onThemeChange(selectedTheme)" class="select-field">
      <option v-for="theme in themes" :key="theme" :value="theme">
        {{ theme.charAt(0).toUpperCase() + theme.slice(1) }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.theme-selector {
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
