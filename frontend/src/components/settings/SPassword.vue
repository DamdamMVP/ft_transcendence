<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const emit = defineEmits(['showNotification'])
const authStore = useAuthStore()
const { t } = useI18n()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const savePassword = async () => {
  try {
    if (!currentPassword.value) {
      emit('showNotification', {
        message: t('settings.notifications.passwordError'),
        type: 'error'
      })
      return
    }

    if (!newPassword.value || !confirmPassword.value) {
      emit('showNotification', {
        message: t('settings.notifications.passwordError'),
        type: 'error'
      })
      return
    }

    if (newPassword.value !== confirmPassword.value) {
      emit('showNotification', {
        message: t('settings.notifications.passwordError'),
        type: 'error'
      })
      return
    }

    const response = await axios.put(
      `/users/update_password/${authStore.user.id}`,
      {
        old_password: currentPassword.value,
        password: newPassword.value,
        username: authStore.user.username,
        email: authStore.user.email
      },
      { withCredentials: true }
    )

    if (
      response.data &&
      response.data.message === 'Password updated successfully'
    ) {
      emit('showNotification', {
        message: t('settings.notifications.passwordChanged'),
        type: 'success'
      })
      currentPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    }
  } catch (error) {
    if (error.response?.data?.error === 'Invalid old password') {
      emit('showNotification', {
        message: t('settings.notifications.invalidOldPassword'),
        type: 'error'
      })
    } else {
      emit('showNotification', {
        message: error.response?.data?.error || t('settings.notifications.passwordError'),
        type: 'error'
      })
    }
  }
}
</script>

<template>
  <div class="setting-item">
    <h3>{{ $t('settings.password') }}</h3>
    <div class="input-group">
      <input
        v-model="currentPassword"
        type="password"
        :placeholder="$t('settings.passwordPlaceholders.current')"
        class="input-field"
      />
      <input
        v-model="newPassword"
        type="password"
        :placeholder="$t('settings.passwordPlaceholders.new')"
        class="input-field"
      />
      <input
        v-model="confirmPassword"
        type="password"
        :placeholder="$t('settings.passwordPlaceholders.confirm')"
        class="input-field"
      />
      <button class="save-button" @click="savePassword">
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
