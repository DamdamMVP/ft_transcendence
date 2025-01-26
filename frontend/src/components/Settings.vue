<script setup>
import ThemeSelector from './ThemeSelector.vue'
import Langage from './Langage.vue'
import { useAuthStore } from '../stores/authStore'
import { useRouter } from 'vue-router'
import { ref, computed, watch } from 'vue'
import { useTheme } from '../composables/useTheme'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const authStore = useAuthStore()
const router = useRouter()
const { setTheme } = useTheme()
const { locale, t } = useI18n()

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

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
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

const savePassword = () => {
  if (newPassword.value !== confirmPassword.value) {
    console.error('Les mots de passe ne correspondent pas')
    return
  }
  console.log(`Mot de passe mis à jour : ${newPassword.value}`)
}

const saveLanguage = () => {
  if (tempLanguage.value) {
    locale.value = tempLanguage.value
    tempLanguage.value = null
  }
}

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
    <!-- Photo de profil -->
    <div class="profile-section">
      <h3>{{ t('settings.profilePhoto') }}</h3>
      <div class="profile-photo-container">
        <img
          :src="profilePhotoUrl"
          :alt="t('settings.profilePhoto')"
          class="profile-photo"
        />
        <div class="photo-overlay" @click="triggerFileInput">
          <span>{{ t('settings.clickToChange') }}</span>
        </div>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleFileSelect"
        style="display: none"
      />
      <button
        class="save-button"
        @click="saveProfilePhoto"
        :disabled="!selectedFile"
      >
        <i class="icon-save"></i> {{ t('settings.save') }}
      </button>
    </div>

    <!-- Pseudo -->
    <div class="setting-item">
      <h3>{{ t('settings.username') }}</h3>
      <div class="input-group">
        <input v-model="username" type="text" class="input-field" />
        <button class="save-button" @click="saveUsername">
          <i class="icon-save"></i> {{ t('settings.save') }}
        </button>
      </div>
    </div>

    <!-- Mot de passe -->
    <div class="setting-item">
      <h3>{{ t('settings.password') }}</h3>
      <div class="input-group">
        <input
          v-model="currentPassword"
          type="password"
          :placeholder="t('settings.passwordPlaceholders.current')"
          class="input-field"
        />
        <input
          v-model="newPassword"
          type="password"
          :placeholder="t('settings.passwordPlaceholders.new')"
          class="input-field"
        />
        <input
          v-model="confirmPassword"
          type="password"
          :placeholder="t('settings.passwordPlaceholders.confirm')"
          class="input-field"
        />
        <button class="save-button" @click="savePassword">
          <i class="icon-save"></i> {{ t('settings.save') }}
        </button>
      </div>
    </div>

    <!-- Langue -->
    <div class="setting-item">
      <h3>{{ t('settings.language') }}</h3>
      <div class="input-group">
        <Langage @update:language="onLanguageUpdate" />
        <button class="save-button" @click="saveLanguage">
          <i class="icon-save"></i> {{ t('settings.save') }}
        </button>
      </div>
    </div>

    <!-- Thème -->
    <div class="setting-item">
      <h3>{{ t('settings.theme') }}</h3>
      <div class="input-group">
        <ThemeSelector @update:theme="onThemeUpdate" />
        <button class="save-button" @click="saveTheme">
          <i class="icon-save"></i> {{ t('settings.save') }}
        </button>
      </div>
    </div>

    <!-- Suppression du compte -->
    <div class="delete-account-section">
      <button class="delete-button" @click="deleteAccount">
        {{ t('settings.deleteAccount') }} <i class="icon-delete"></i>
      </button>
      <button class="logout-button" @click="handleLogout">
        {{ t('navbar.disconnect') }}
      </button>
    </div>
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

.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--background-color);
  border-radius: 8px;
  border: 1px solid var(--secondary-color);
  text-align: center;
}

.profile-photo-container {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto;
  cursor: pointer;
}

.profile-photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  transition: filter 0.3s ease;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.photo-overlay span {
  color: white;
  text-align: center;
  padding: 10px;
  font-size: 14px;
}

.profile-photo-container:hover .photo-overlay {
  opacity: 1;
}

.profile-photo-container:hover .profile-photo {
  filter: brightness(0.8);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  box-sizing: border-box;
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

.delete-account-section {
  text-align: center;
  padding: 16px;
  background: var(--background-color);
  border-radius: 8px;
  display: flex;
  gap: 24px;
  justify-content: center;
}

.delete-button {
  padding: 8px 16px;
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.delete-button:hover {
  background: var(--error-hover-color);
}

.logout-button {
  padding: 8px 16px;
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.logout-button:hover {
  background: var(--error-hover-color);
}
</style>
