import { ref } from 'vue'
import axios from 'axios'

export function useAuth() {
  const error = ref('')
  
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
      const errorMessage = err.response?.data?.error || 'Erreur lors de la création du compte'
      throw new Error(errorMessage)
    }
  }

  const signIn = async ({ email, password }) => {
    try {
      // Implémenter la logique de connexion ici
      console.log('Sign In with:', email, password)
    } catch (err) {
      throw new Error('Erreur lors de la connexion')
    }
  }

  return {
    error,
    signUp,
    signIn
  }
}
