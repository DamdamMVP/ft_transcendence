import { ref } from 'vue'
import axios from 'axios'
import eventBus from '../utils/eventBus'
import { useAuthStore } from '../stores/authStore'

export function useAuth() {
  const error = ref('')
  const user = ref(null)
  const isAuthenticated = ref(false)
  const requires2FA = ref(false)
  const tempAuthToken = ref(null)

  // Configuration d'axios pour inclure les cookies
  axios.defaults.withCredentials = true

  const signUp = async ({ username, email, password }) => {
    try {
      const response = await axios.post('/users/create', {
        username,
        email,
        password,
      })

      if (response.status === 201) {
        return { success: true, data: response.data }
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || 'Erreur lors de la création du compte'
      throw new Error(errorMessage)
    }
  }

  const signIn = async ({ email, password }) => {
    try {
      const response = await axios.post('/users/login', {
        email,
        password,
      })

      if (response.status === 200) {
        // Vérifier le statut 2FA
        try {
          const twoFAResponse = await axios.get('/users/2fa/status')
          console.log('Statut 2FA:', twoFAResponse.data.enabled ? 'Activé' : 'Désactivé')
          
          if (twoFAResponse.data.enabled) {
            requires2FA.value = true
            tempAuthToken.value = response.data.token // Stocker temporairement le token
            // Ouvrir le modal 2FA
            eventBus.emit('show-2fa-verification')
            return { success: true, requires2FA: true, data: response.data }
          }
        } catch (error) {
          console.warn('Impossible de récupérer le statut 2FA:', error)
        }

        // Si pas de 2FA ou erreur de vérification du statut, procéder à la connexion normale
        user.value = response.data.user
        isAuthenticated.value = true
        return { success: true, data: response.data }
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || 'Erreur lors de la connexion'
      throw new Error(errorMessage)
    }
  }

  const verify2FAAndComplete = async (code) => {
    try {
      const response = await axios.post('/users/2fa/verify', {
        token: code
      })

      if (response.status === 200) {
        user.value = response.data.user
        isAuthenticated.value = true
        requires2FA.value = false
        tempAuthToken.value = null
        return { success: true, data: response.data }
      }
    } catch (err) {
      if (err.response?.status === 400) {
        throw new Error('invalidCode')
      }
      const errorMessage = err.response?.data?.error || 'unknownError'
      throw new Error(errorMessage)
    }
  }

  const signOut = async () => {
    try {
      // Appeler le endpoint de déconnexion pour supprimer le cookie
      await axios.post('/users/logout')
    } catch (err) {
      // Si l'erreur est 401, c'est normal (token expiré), on continue la déconnexion
      if (err.response?.status !== 401) {
        console.error('Erreur lors de la déconnexion:', err)
        throw err
      }
    } finally {
      // Nettoyer les données locales de l'utilisateur
      user.value = null
      isAuthenticated.value = false
    }
  }

  return {
    user,
    error,
    isAuthenticated,
    requires2FA,
    signIn,
    signUp,
    signOut,
    verify2FAAndComplete,
  }
}
