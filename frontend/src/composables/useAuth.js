import { ref } from 'vue'
import axios from 'axios'

export function useAuth() {
  const error = ref('')
  const user = ref(null)
  const isAuthenticated = ref(false)

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
        // Stocker uniquement les informations de l'utilisateur
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

  const signOut = async () => {
    try {
      // Appeler le endpoint de déconnexion pour supprimer le cookie
      await axios.post('http://localhost:800/users/logout')
    } catch (err) {
      console.error('Erreur lors de la déconnexion:', err)
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
    signUp,
    signIn,
    signOut,
  }
}
