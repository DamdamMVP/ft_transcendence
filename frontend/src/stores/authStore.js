import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // État de l'authentification
  const isAuthenticated = ref(false)
  const user = ref(null)

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

  const logout = () => {
    // Nettoyer l'état
    user.value = null
    isAuthenticated.value = false

    // Nettoyer le localStorage
    localStorage.removeItem('user')
  }

  // Initialiser l'état au démarrage
  initAuth()

  return { 
    // État
    isAuthenticated,
    user,
    
    // Actions
    login,
    logout
  }
})
