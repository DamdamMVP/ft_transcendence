<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import eventBus from '@/utils/eventBus'
import axios from 'axios'
import TwoFactorModal from '@/components/modals/TwoFactorModal.vue'

// Configure axios to include cookies
axios.defaults.withCredentials = true

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const userDataStr = params.get('user')
  const token = params.get('token')

  if (userDataStr && token) {
    const userData = JSON.parse(decodeURIComponent(userDataStr))
    
    // Check 2FA status exactly as in signIn
    try {
      const twoFAResponse = await axios.get('/users/2fa/status')
      console.log('2FA status:', twoFAResponse.data.enabled ? 'Enabled' : 'Disabled')
      
      if (twoFAResponse.data.enabled) {
        // Listen for 2FA success event
        eventBus.on('2fa-success', (data) => {
          console.log('2FA validated, logging in...')
          authStore.login(userData, token)
          eventBus.off('2fa-success')
          eventBus.off('2fa-cancelled')  // Don't forget to remove this listener too
          router.push('/pong')
        })
        
        // Listen for cancellation event
        eventBus.on('2fa-cancelled', () => {
          console.log('2FA cancelled, redirecting to login')
          eventBus.off('2fa-success')
          eventBus.off('2fa-cancelled')
          router.push('/')
        })
        
        // Open 2FA modal
        eventBus.emit('show-2fa-verification')
        return
      }
    } catch (error) {
      console.warn('Failed to retrieve 2FA status:', error)
    }

    // If no 2FA or verification status error, proceed with normal login
    authStore.login(userData, token)
    router.push('/pong')
  } else {
    router.push('/')
  }
})

// Clean up listeners when component is unmounted
onBeforeUnmount(() => {
  eventBus.off('2fa-success')
  eventBus.off('2fa-cancelled')
})
</script>

<template>
  <div class="auth-callback">
    <p>Authenticating...</p>
    <TwoFactorModal />
  </div>
</template>