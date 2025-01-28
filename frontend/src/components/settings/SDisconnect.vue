<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import { useRouter } from 'vue-router'
import axios from 'axios'

const emit = defineEmits(['showNotification'])
const authStore = useAuthStore()
const router = useRouter()
const showDeleteConfirm = ref(false)

const deleteAccount = async () => {
  try {
    const response = await axios.delete(
      `/users/delete/${authStore.user.id}`,
      { withCredentials: true }
    )

    if (response.data?.message === 'User successfully deleted!') {
      emit('showNotification', {
        message: 'Compte supprimé avec succès',
        type: 'success'
      })
      authStore.logout()
      showDeleteConfirm.value = false
      router.push('/')
    }
  } catch (error) {
    emit('showNotification', {
      message: error.response?.data?.error || 'Erreur lors de la suppression du compte',
      type: 'error'
    })
    showDeleteConfirm.value = false
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="buttons-container">
    <button class="delete-button" @click="showDeleteConfirm = true">
      <i class="icon-delete"></i>{{ $t('settings.deleteAccount') }}
    </button>
    <button class="logout-button" @click="handleLogout">
      <i class="icon-logout"></i>{{ $t('settings.logout') }}
    </button>
  </div>

  <!-- Popup de confirmation -->
  <div v-if="showDeleteConfirm" class="modal-overlay" @click="showDeleteConfirm = false">
    <div class="modal-content" @click.stop>
      <h3>{{ $t('settings.deleteAccount') }}</h3>
      <p class="confirm-text">{{ $t('settings.deleteConfirm') }}</p>
      <div class="modal-buttons">
        <button class="delete-button" @click="deleteAccount">
          {{ $t('settings.deleteAccountConfirm') }}
        </button>
        <button class="cancel-button" @click="showDeleteConfirm = false">
          {{ $t('settings.cancel') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.buttons-container {
  display: flex;
  gap: 24px;
  justify-content: center;
  align-items: center;
  padding: 8px 0;
}

.delete-button,
.logout-button,
.cancel-button {
  min-width: 160px;
  height: 40px;
  padding: 0 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.delete-button {
  background: var(--error-color);
  color: white;
}

.delete-button:hover {
  background: var(--error-hover-color);
}

.logout-button {
  background: var(--primary-color);
  color: white;
}

.logout-button:hover {
  background: var(--primary-hover-color);
}

.cancel-button {
  background: var(--secondary-color);
  color: var(--text-color);
}

.cancel-button:hover {
  background: var(--hover-color);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: var(--background-color);
  padding: 24px;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-content h3 {
  color: var(--text-color);
  margin: 0 0 16px 0;
  text-align: center;
}

.confirm-text {
  color: var(--error-color);
  text-align: center;
  margin: 0 0 24px 0;
}

.modal-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.modal-buttons button {
  min-width: 120px;
}
</style>
