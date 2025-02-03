import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useUserStatus } from '../composables/useUserStatus'

export const useAuthStore = defineStore('auth', () => {
  // Authentication state
  const isAuthenticated = ref(false)
  const user = ref(null)
  const { signOut } = useAuth()
  const { closeWebSocket } = useUserStatus()

  // Initialize authentication state on startup
  const initAuth = () => {
    const userData = localStorage.getItem('user')
    if (userData) {
      user.value = JSON.parse(userData)
      isAuthenticated.value = true
    }
  }

  const login = (userData) => {
    // Update state
    user.value = userData
    isAuthenticated.value = true

    // Save user data
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const updateUser = (updatedData) => {
    if (user.value) {
      // Update only provided fields
      user.value = {
        ...user.value,
        ...updatedData
      }
      // Save updated data
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  const logout = async () => {
    try {
      // Close WebSocket before logout
      closeWebSocket()
      
      await signOut()
    } catch (error) {
      console.error('Error during logout:', error)
    } finally {
      // Clean up state
      user.value = null
      isAuthenticated.value = false

      // Clean up localStorage
      localStorage.removeItem('user')
    }
  }

  // Initialize state on startup
  initAuth()

  return { 
    user,
    isAuthenticated,
    login,
    logout,
    updateUser,
  }
})
