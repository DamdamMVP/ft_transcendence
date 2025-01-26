import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref(null)

  // Initialiser l'état d'authentification au démarrage
  const initAuth = () => {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    if (token && userData) {
      isAuthenticated.value = true
      user.value = JSON.parse(userData)
    }
  }

  const login = (userData) => {
    isAuthenticated.value = true
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const logout = () => {
    isAuthenticated.value = false
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Initialiser l'état au démarrage
  initAuth()

  return { 
    isAuthenticated, 
    user,
    login, 
    logout 
  }
})
