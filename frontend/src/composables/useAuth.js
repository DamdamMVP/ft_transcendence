import { ref } from 'vue'
import axios from 'axios'
import eventBus from '../utils/eventBus'

export function useAuth() {
  const error = ref('')
  const user = ref(null)
  const isAuthenticated = ref(false)
  const requires2FA = ref(false)
  const tempAuthToken = ref(null)

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
        err.response?.data?.error || 'Error while creating account'
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
        // Check 2FA status
        try {
          const twoFAResponse = await axios.get('/users/2fa/status')
          console.log('2FA status:', twoFAResponse.data.enabled ? 'Enabled' : 'Disabled')
          
          if (twoFAResponse.data.enabled) {
            requires2FA.value = true
            tempAuthToken.value = response.data.token // Store token temporarily
            // Open 2FA modal
            eventBus.emit('show-2fa-verification')
            return { success: true, requires2FA: true, data: response.data }
          }
        } catch (error) {
          console.warn('Failed to retrieve 2FA status:', error)
        }

        // If no 2FA or verification status error, proceed with normal login
        user.value = response.data.user
        isAuthenticated.value = true
        return { success: true, data: response.data }
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || 'Error while logging in'
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
        eventBus.emit('2fa-success', response.data)
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
      // Call logout endpoint to delete cookie
      await axios.post('/users/logout')
    } catch (err) {
      // If error is 401, it's normal (token expired), continue with logout
      if (err.response?.status !== 401) {
        console.error('Error while logging out:', err)
        throw err
      }
    } finally {
      // Clean up local user data
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
