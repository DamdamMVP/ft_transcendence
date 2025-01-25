import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false) // Par défaut, l'utilisateur n'est pas connecté

  const login = () => {
    isAuthenticated.value = true // Simule une connexion
  }

  const logout = () => {
    isAuthenticated.value = false // Simule une déconnexion
  }

  return { isAuthenticated, login, logout }
})
