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

// Initialiser le thème et la langue au chargement
onMounted(() => {
  if (authStore.user?.language) {
    locale.value = authStore.user.language
  }
  if (authStore.user?.theme) {
    setTheme(authStore.user.theme)
  }
})

// Surveiller les changements dans authStore.user
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
</style>
