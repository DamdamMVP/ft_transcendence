<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import eventBus from '@/utils/eventBus'
import axios from 'axios'
import TwoFactorModal from '@/components/modals/TwoFactorModal.vue'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const userDataStr = params.get('user')
  const token = params.get('token')

  if (userDataStr && token) {
    const userData = JSON.parse(decodeURIComponent(userDataStr))
    
    // Vérifier le statut 2FA exactement comme dans signIn
    try {
      const twoFAResponse = await axios.get('/users/2fa/status')
      console.log('Statut 2FA:', twoFAResponse.data.enabled ? 'Activé' : 'Désactivé')
      
      if (twoFAResponse.data.enabled) {
        // Écouter l'événement de succès 2FA
        eventBus.on('2fa-success', (data) => {
          console.log('2FA validée, connexion...')
          authStore.login(userData, token)
          eventBus.off('2fa-success')
          router.push('/pong')
        })
        // Ouvrir le modal 2FA
        eventBus.emit('show-2fa-verification')
        return
      }
    } catch (error) {
      console.warn('Impossible de récupérer le statut 2FA:', error)
    }

    // Si pas de 2FA ou erreur de vérification du statut, procéder à la connexion normale
    authStore.login(userData, token)
    router.push('/pong')
  } else {
    router.push('/login')
  }
})
</script>

<template>
  <div class="auth-callback">
    <p>Authentification en cours...</p>
    <TwoFactorModal />
  </div>
</template>