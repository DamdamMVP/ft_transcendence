import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useUserStatus } from '../composables/useUserStatus'

export const useAuthStore = defineStore('auth', () => {
  // État de l'authentification
  const isAuthenticated = ref(false)
  const user = ref(null)
  const { signOut } = useAuth()
  const { closeWebSocket } = useUserStatus()

  // Initialiser l'état d'authentification au démarrage
  const initAuth = () => {
    const userData = localStorage.getItem('user')
    if (userData) {
      user.value = JSON.parse(userData)
      isAuthenticated.value = true
    }
  }

  const login = (userData) => {
    // Mettre à jour l'état
    user.value = userData
    isAuthenticated.value = true

    // Sauvegarder les données utilisateur
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const updateUser = (updatedData) => {
    if (user.value) {
      // Mettre à jour uniquement les champs fournis
      user.value = {
        ...user.value,
        ...updatedData
      }
      // Sauvegarder les données mises à jour
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  const logout = async () => {
    try {
      // Fermer le WebSocket avant la déconnexion
      closeWebSocket()
      
      await signOut()
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    } finally {
      // Nettoyer l'état
      user.value = null
      isAuthenticated.value = false

      // Nettoyer le localStorage
      localStorage.removeItem('user')
    }
  }

  // Initialiser l'état au démarrage
  initAuth()

  return { 
    user,
    isAuthenticated,
    login,
    logout,
    updateUser,
  }
})
