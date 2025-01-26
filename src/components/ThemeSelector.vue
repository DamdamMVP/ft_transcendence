<script setup>
import { useTheme } from '../composables/useTheme'

const { setTheme, getAvailableThemes, currentTheme } = useTheme()
const themes = getAvailableThemes()
</script>

<template>
  <div class="theme-selector">
    <select v-model="currentTheme" @change="setTheme(currentTheme)">
      <option v-for="theme in themes" :key="theme" :value="theme">
        {{ theme.charAt(0).toUpperCase() + theme.slice(1) }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.theme-selector {
  margin-left: 1rem;
}

select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--secondary-color);
  background-color: transparent;
  color: var(--text-color);
  cursor: pointer;
}

select:focus {
  outline: none;
  border-color: var(--primary-color);
}

option {
  background-color: var(--background-color);
  color: var(--text-color);
}
</style>
