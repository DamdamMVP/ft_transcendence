<script setup>
import SProfil from './settings/SProfil.vue'
import SPseudo from './settings/SPseudo.vue'
import SPassword from './settings/SPassword.vue'
import SLangage from './settings/SLangage.vue'
import STheme from './settings/STheme.vue'
import SDisconnect from './settings/SDisconnect.vue'
import Notification from './Notification.vue'
import ThemeSelector from './ThemeSelector.vue'
import Langage from './Langage.vue'
import { useAuthStore } from '../stores/authStore'
import { useRouter } from 'vue-router'
import { ref, computed, watch, onMounted } from 'vue'
import { useTheme } from '../composables/useTheme'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('success')

// Variables temporaires pour le thème et la langue
const tempTheme = ref(null)
const tempLanguage = ref(null)

// Référence vers l'input file caché
const fileInput = ref(null)
const selectedFile = ref(null)

// Champs pour la mise à jour des paramètres
const username = ref(authStore.user?.username || '')

// Surveiller les changements dans authStore.user
watch(() => authStore.user, (newUser) => {
  if (newUser) {
    username.value = newUser.username
    // Mettre à jour la langue si elle change
    if (newUser.language) {
      locale.value = newUser.language
    }
  }
}, { deep: true })

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const profilePhotoUrl = computed(() => {
  if (selectedFile.value) {
    return URL.createObjectURL(selectedFile.value)
  }
  return authStore.user?.profile_picture
    ? `http://localhost:8000${authStore.user.profile_picture}`
    : null
})

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

const showError = (message) => {
  notificationMessage.value = message
  notificationType.value = 'error'
  showNotification.value = true
}

const handleNotification = ({ message, type }) => {
  if (type === 'success') {
    showSuccess(message)
  } else {
    showError(message)
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const saveProfilePhoto = async () => {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('profile_picture', selectedFile.value)

  try {
    const response = await axios.put(
      `http://localhost:8000/users/update_profile_picture/${authStore.user.id}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
      }
    )
    console.log('Réponse du serveur update:', response.data)

    // Si la requête réussit (pas d'erreur), on considère que c'est un succès
    if (response.data.message === 'Profile picture updated successfully') {
      // On recharge les données de l'utilisateur pour obtenir la nouvelle URL de la photo
      const userResponse = await axios.get(
        `http://localhost:8000/users/read/${authStore.user.id}`,
        { withCredentials: true }
      )
      console.log('Réponse user data:', userResponse.data)
      if (userResponse.data) {
        // On garde l'URL relative
        authStore.updateUser(userResponse.data)
      }
      selectedFile.value = null
    }
  } catch (error) {
    console.error(
      'Erreur lors de la mise à jour de la photo de profil:',
      error.response?.data || error
    )
  }
}

const saveUsername = async () => {
  try {
    const response = await axios.put(
      `http://localhost:8000/users/update/${authStore.user.id}`,
      { username: username.value },
      { withCredentials: true }
    )

    if (response.data && response.data.username === username.value) {
      console.log('✅ Username mis à jour:', response.data.username)
      authStore.updateUser(response.data)
    }
  } catch (error) {
    console.error(
      "Erreur lors de la mise à jour du nom d'utilisateur:",
      error.response?.data || error
    )
  }
}

const savePassword = async () => {
  try {
    if (!currentPassword.value) {
      console.error('❌ Le mot de passe actuel est requis')
      return
    }
    
    if (!newPassword.value || !confirmPassword.value) {
      console.error('❌ Le nouveau mot de passe et sa confirmation sont requis')
      return
    }

    if (newPassword.value !== confirmPassword.value) {
      console.error('❌ Les mots de passe ne correspondent pas')
      return
    }

    const response = await axios.put(
      `http://localhost:8000/users/update_password/${authStore.user.id}`,
      {
        old_password: currentPassword.value,
        password: newPassword.value,
        username: authStore.user.username,
        email: authStore.user.email
      },
      { withCredentials: true }
    )

    if (response.data && response.data.message === 'Password updated successfully') {
      console.log('✅ Mot de passe mis à jour')
      // Réinitialiser les champs
      currentPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    }
  } catch (error) {
    if (error.response?.data?.error === 'Invalid old password') {
      console.error('❌ Le mot de passe actuel est incorrect')
    } else if (error.response?.data?.error === 'User not found') {
      console.error('❌ Utilisateur non trouvé')
    } else {
      console.error('❌ Erreur lors de la mise à jour du mot de passe')
    }
  }
}

const saveLanguage = async () => {
  if (tempLanguage.value) {
    try {
      const response = await axios.put(
        `http://localhost:8000/users/update_language/${authStore.user.id}`,
        {
          language: tempLanguage.value,
          username: authStore.user.username,
          email: authStore.user.email
        },
        { withCredentials: true }
      )

      if (response.data?.user) {
        locale.value = tempLanguage.value
        authStore.updateUser(response.data.user)
        tempLanguage.value = null
      }
    } catch (error) {
      if (error.response?.data?.error === 'Invalid language') {
        console.error('❌ Langue non valide')
      } else {
        console.error('❌ Erreur lors de la mise à jour de la langue')
      }
      tempLanguage.value = authStore.user.language
    }
  }
}

// Initialiser la langue au chargement
onMounted(() => {
  if (authStore.user?.language) {
    locale.value = authStore.user.language
  }
})

const saveTheme = () => {
  if (tempTheme.value) {
    setTheme(tempTheme.value)
    tempTheme.value = null
  }
}

const onThemeUpdate = (theme) => {
  tempTheme.value = theme
}

const onLanguageUpdate = (lang) => {
  tempLanguage.value = lang
}

const deleteAccount = () => {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="settings-container">
    <SProfil @showNotification="handleNotification" />
    <SPseudo @showNotification="handleNotification" />
    <SPassword @showNotification="handleNotification" />
    <SLangage @showNotification="handleNotification" />
    <STheme @showNotification="handleNotification" />
    <SDisconnect @showNotification="handleNotification" />

    <!-- Notification -->
    <Notification
      v-if="showNotification"
      :message="notificationMessage"
      :type="notificationType"
      @close="closeNotification"
    />
  </div>
</template>

<style scoped>
.settings-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: var(--text-color);
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: var(--background-color);
  border-radius: 8px;
  border: 1px solid var(--secondary-color);
  width: 100%;
  box-sizing: border-box;
}

h2,
h3 {
  color: var(--text-color);
  margin: 0;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  box-sizing: border-box;
}

.input-field {
  padding: 8px 12px;
  background: var(--background-color);
  border: 2px solid var(--secondary-color);
  border-radius: 4px;
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
}

.input-field:hover {
  border-color: var(--primary-color);
}

.input-field:focus {
  border-color: var(--info-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.select-field {
  padding: 8px 12px;
  background: var(--background-color);
  border: 2px solid var(--secondary-color);
  border-radius: 4px;
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.select-field:hover {
  border-color: var(--primary-color);
}

.select-field:focus {
  border-color: var(--info-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.save-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
}

.save-button:hover {
  background: var(--primary-hover-color);
}
</style>
