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
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  color: var(--text-color);
  animation: fadeIn 0.6s ease;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--background-secondary-color);
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  width: 100%;
  box-sizing: border-box;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px var(--primary-shadow-color);
  backdrop-filter: blur(10px);
}

.setting-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

h2, h3 {
  color: var(--primary-color);
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  text-shadow: 0 0 10px var(--primary-shadow-color);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.input-field {
  padding: 1rem;
  background: var(--background-color);
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  color: var(--text-color);
  font-size: 1rem;
  transition: all 0.3s ease;
  width: 100%;
  box-sizing: border-box;
  max-width: 100%;
}

.input-field:hover {
  border-color: var(--primary-hover-color);
  box-shadow: 0 0 15px var(--primary-shadow-color);
}

.input-field:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 20px var(--primary-shadow-color);
  transform: translateY(-2px);
}

.select-field {
  padding: 1rem;
  background: var(--background-color);
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  color: var(--text-color);
  font-size: 1rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.select-field:hover {
  border-color: var(--primary-hover-color);
  box-shadow: 0 0 15px var(--primary-shadow-color);
}

.select-field:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 20px var(--primary-shadow-color);
}

.save-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover-color));
  color : --text-color;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  font-weight: 600;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.save-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

.save-button:active {
  transform: translateY(-1px);
  box-shadow: 0 2px 10px var(--primary-shadow-color);
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Media Queries */
@media (max-width: 768px) {
  .settings-container {
    padding: 1rem;
  }

  .setting-item {
    padding: 1rem;
  }

  h2, h3 {
    font-size: 1.2rem;
  }

  .input-field,
  .select-field,
  .save-button {
    padding: 0.8rem;
    font-size: 0.9rem;
  }
}
</style>