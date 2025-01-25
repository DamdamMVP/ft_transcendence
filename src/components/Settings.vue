<script setup>
import ThemeSelector from './ThemeSelector.vue'
import Langage from './Langage.vue'
import { useAuthStore } from '../stores/authStore'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { useTheme } from '../composables/useTheme'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const router = useRouter()
const { setTheme } = useTheme()
const { locale, t } = useI18n()

// Variables temporaires pour le thème et la langue
const tempTheme = ref(null)
const tempLanguage = ref(null)

// Champs pour la mise à jour des paramètres
const username = ref('Lisa')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

// Actions de sauvegarde
const saveProfilePhoto = () => {
  console.log('Photo de profil sauvegardée')
}

const saveUsername = () => {
  console.log(`Pseudo sauvegardé : ${username.value}`)
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
    console.log('Langue sauvegardée:', tempLanguage.value)
    tempLanguage.value = null
  }
}

const saveTheme = () => {
  if (tempTheme.value) {
    setTheme(tempTheme.value)
    console.log('Thème sauvegardé:', tempTheme.value)
    tempTheme.value = null
  }
}

const deleteAccount = () => {
  console.log('Compte supprimé')
  authStore.logout()
  router.push('/')
}

// Gestionnaires d'événements pour les changements de thème et de langue
const onThemeUpdate = (theme) => {
  tempTheme.value = theme
}

const onLanguageUpdate = (lang) => {
  tempLanguage.value = lang
}
</script>

<template>
  <div class="settings-container">
    <!-- Photo de profil -->
    <div class="profile-section">
      <h3>{{ t('settings.profilePhoto') }}</h3>
      <img
        src="https://via.placeholder.com/150"
        :alt="t('settings.profilePhoto')"
        class="profile-photo"
      />
      <button class="save-button" @click="saveProfilePhoto">
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
    </div>

    <button class="logout-button" @click="handleLogout">
      {{ t('navbar.disconnect') }}
    </button>
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

.profile-photo {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--primary-color);
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
  margin-top: 32px;
  text-align: center;
  padding: 16px;
  background: var(--background-color);
  border-radius: 8px;
  border: 1px solid var(--secondary-color);
}

.delete-button {
  padding: 12px 16px;
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
  margin-top: 24px;
  padding: 8px 16px;
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  align-self: center;
}

.logout-button:hover {
  background: var(--error-hover-color);
}
</style>
