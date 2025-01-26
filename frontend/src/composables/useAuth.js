import { ref } from 'vue'
import axios from 'axios'

export function useAuth() {
  const error = ref('')
  const user = ref(null)
  const isAuthenticated = ref(false)

  const signUp = async ({ username, email, password }) => {
    try {
      const response = await axios.post('http://localhost:8000/users/create', {
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
      const response = await axios.post('http://localhost:8000/users/login', {
        email,
        password,
      })

      if (response.status === 200) {
        // Stocker les informations de l'utilisateur
        user.value = response.data.user
        isAuthenticated.value = true

        // Si l'API renvoie un token, le stocker
        if (response.data.token) {
          localStorage.setItem('token', response.data.token)
          // Configurer axios pour inclure le token dans les futures requêtes
          axios.defaults.headers.common['Authorization'] =
            `Bearer ${response.data.token}`
        }

        return { success: true, data: response.data }
      }
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || 'Erreur lors de la connexion'
      throw new Error(errorMessage)
    }
  }

  const signOut = () => {
    // Nettoyer les données de l'utilisateur
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
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
