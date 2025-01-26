<script setup>
import { defineProps } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  items: {
    type: Array,
    default: () => ['Pong', 'Tic-Tac-Toe'],
  },
})

const { t } = useI18n()
</script>

<template>
  <nav class="navbar-profil">
    <ul class="navbar-list">
      <li v-for="(item, index) in items" :key="index" class="navbar-item">
        <router-link
          :to="`/profil/${item.toLowerCase().replace(/ /g, '-')}`"
          class="navbar-link"
          active-class="navbar-link-selected"
        >
          {{ t(`navbarProfil.${item}`) }}
        </router-link>
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
  background-color: var(--primary-color);
  color: white;
}

.navbar-link-selected {
  background-color: var(--primary-color);
  color: white;
}

.navbar-link:hover:not(.navbar-link-selected) {
  background-color: var(--primary-color);
  color: white;
}
</style>
