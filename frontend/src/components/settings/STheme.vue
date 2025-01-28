<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import { useTheme } from '../../composables/useTheme'
import axios from 'axios'

const emit = defineEmits(['showNotification'])
const authStore = useAuthStore()
const { setTheme } = useTheme()

const tempTheme = ref(authStore.user.theme)

const themes = ['light', 'dark', 'forest']

const saveTheme = async () => {
  if (tempTheme.value) {
    try {
      const response = await axios.put(
        `/users/update_theme/${authStore.user.id}`,
        {
          theme: tempTheme.value,
          username: authStore.user.username,
          email: authStore.user.email,
        },
        { withCredentials: true }
      )

      if (response.data?.user) {
        emit('showNotification', {
          message: 'Thème mis à jour avec succès',
          type: 'success',
        })
        setTheme(tempTheme.value)
        authStore.updateUser(response.data.user)
      }
    } catch (error) {
      emit('showNotification', {
        message:
          error.response?.data?.error ||
          'Erreur lors de la mise à jour du thème',
        type: 'error',
      })
      tempTheme.value = authStore.user.theme
    }
  }
}
</script>

<template>
  <div class="setting-item">
    <h3>{{ $t('settings.theme') }}</h3>
    <div class="input-group">
      <select v-model="tempTheme" class="select-field">
        <option v-for="theme in themes" :key="theme" :value="theme">
          {{ $t(`settings.themes.${theme}`) }}
        </option>
      </select>
      <button class="save-button" @click="saveTheme">
        <i class="icon-save"></i> {{ $t('settings.save') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
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

.select-field {
  padding: 8px 12px;
  background: var(--background-color);
  border: 2px solid var(--secondary-color);
  border-radius: 4px;
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  cursor: pointer;
  width: 100%;
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
