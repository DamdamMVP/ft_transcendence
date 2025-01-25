<script setup>
import { defineProps } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  items: {
    type: Array,
    default: () => ['Pong', 'Tic-Tac-Toe', 'Settings'],
  },
})

const { t } = useI18n() // Utilisation directe de la fonction `t`
</script>

<template>
  <nav class="navbar-profil">
    <ul class="navbar-list">
      <li v-for="(item, index) in items" :key="index" class="navbar-item">
        <a href="#" class="navbar-link">{{ t(`navbarProfil.${item}`) }}</a>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.navbar-profil {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color);
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  padding: 8px 16px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

.navbar-list {
  display: flex;
  gap: 16px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.navbar-item {
  font-size: 14px;
  font-weight: bold;
}

.navbar-link {
  text-decoration: none;
  color: var(--text-color);
  padding: 8px 12px;
  border-radius: 4px;
  transition:
    background-color 0.3s,
    color 0.3s;
}

.navbar-link:hover {
  background-color: var(--background-color);
  color: var(--text-color);
}
</style>
