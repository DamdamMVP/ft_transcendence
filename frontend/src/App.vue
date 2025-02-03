<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
import FriendList from './components/chat/FriendList.vue'
import { useAuthStore } from './stores/authStore'
import { useI18n } from 'vue-i18n'
import { useTheme } from './composables/useTheme'
import { onMounted, watch } from 'vue'

const authStore = useAuthStore()
const { locale } = useI18n()
const { setTheme } = useTheme()

// Initialize theme and language on load
onMounted(() => {
  if (authStore.user?.language) {
    locale.value = authStore.user.language
  }
  if (authStore.user?.theme) {
    setTheme(authStore.user.theme)
  }
})

// Watch for changes in authStore.user
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      if (newUser.language) {
        locale.value = newUser.language
      }
      if (newUser.theme) {
        setTheme(newUser.theme)
      }
    }
  },
  { deep: true }
)
</script>

<template>
  <div class="app">
    <NavBar />
    <RouterView />
    <FriendList />
  </div>
</template>

<style>
.app {
  width: 100vw;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background: var(--background-color);
}

  :root {
  transition: all 0.3s ease;
  min-height: 100vh;
  background-image: var(--background-gradient);
}

body {
  background-color: var(--background-color);
}

.card {
  background-color: var(--background-color-secondary);
  border: 1px solid var(--border-color);
  box-shadow: var(--box-shadow);
  border-radius: 12px;
  padding: 1.5rem;
}
</style>
