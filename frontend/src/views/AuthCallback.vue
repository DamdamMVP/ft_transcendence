<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const userDataStr = params.get('user')
  const token = params.get('token')

  if (userDataStr && token) {
    const userData = JSON.parse(decodeURIComponent(userDataStr))
    authStore.login(userData)
    router.push('/pong')
  } else {
    router.push('/login')
  }
})
</script>

<template>
  <div class="auth-callback">
    <p>Authentification en cours...</p>
  </div>
</template>