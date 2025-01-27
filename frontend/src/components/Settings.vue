<script setup>
import SProfil from './settings/SProfil.vue'
import SPseudo from './settings/SPseudo.vue'
import SPassword from './settings/SPassword.vue'
import SLangage from './settings/SLangage.vue'
import STheme from './settings/STheme.vue'
import SDisconnect from './settings/SDisconnect.vue'
import { ref } from 'vue'
import Notification from './Notification.vue'

const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('success')

const showSuccess = (message) => {
  notificationMessage.value = message
  notificationType.value = 'success'
  showNotification.value = true
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

const closeNotification = () => {
  showNotification.value = false
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
