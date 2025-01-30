<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <h2>{{ t('security.setup2FA') }}</h2>
      
      <!-- Alert pour les messages d'erreur/succès -->
      <div v-if="alertMessage" :class="['alert', `alert-${alertType}`]">
        {{ alertMessage }}
      </div>

      <div class="qr-container" v-if="qrCode">
        <img :src="`data:image/svg+xml;base64,${qrCode}`" alt="QR Code" />
      </div>
      
      <p class="instructions">{{ t('security.scanQRCode') }}</p>
      
      <div class="verification-section" v-if="showVerification">
        <div class="input-group">
          <input
            type="text"
            v-model="verificationCode"
            :placeholder="t('security.enterCode')"
            class="verification-input"
            maxlength="6"
            pattern="\d*"
            @input="validateInput"
            :disabled="isLoading"
          />
          <button 
            @click="verifyCode" 
            class="verify-btn" 
            :disabled="!isValidCode || isLoading"
          >
            <span v-if="isLoading" class="loader"></span>
            <span v-else>{{ t('security.verify') }}</span>
          </button>
        </div>
        <small class="input-help" v-if="verificationCode && !isValidCode">
          {{ t('security.codeFormat') }}
        </small>
      </div>

      <button class="close-btn" @click="closeModal" :disabled="isLoading">
        {{ t('common.close') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import eventBus from '../../utils/eventBus'

const { t } = useI18n()

// State
const show = ref(false)
const qrCode = ref('')
const verificationCode = ref('')
const showVerification = ref(true)
const isLoading = ref(false)
const alertMessage = ref('')
const alertType = ref('info') // 'success', 'error', 'info'

// Computed
const isValidCode = computed(() => {
  return /^\d{6}$/.test(verificationCode.value)
})

// Input validation
const validateInput = (event) => {
  // Ne permet que les chiffres
  const value = event.target.value
  verificationCode.value = value.replace(/\D/g, '').slice(0, 6)
}

// Gestion des erreurs API
const handleApiError = (error) => {
  isLoading.value = false
  if (error.response) {
    alertMessage.value = t(`errors.${error.response.data.error}`) || error.response.data.error
  } else if (error.request) {
    alertMessage.value = t('errors.networkError')
  } else {
    alertMessage.value = t('errors.unknownError')
  }
  alertType.value = 'error'
  setTimeout(() => {
    alertMessage.value = ''
  }, 5000)
}

// Ouvrir le modal avec le QR code
const openModal = async (qrCodeData) => {
  try {
    qrCode.value = qrCodeData
    show.value = true
    alertMessage.value = t('security.scanInstructions')
    alertType.value = 'info'
  } catch (error) {
    handleApiError(error)
  }
}

// Fermer le modal
const closeModal = () => {
  if (isLoading.value) return
  
  show.value = false
  qrCode.value = ''
  verificationCode.value = ''
  alertMessage.value = ''
}

// Vérifier le code 2FA
const verifyCode = async () => {
  if (!isValidCode.value || isLoading.value) return
  
  isLoading.value = true
  alertMessage.value = ''
  
  try {
    const response = await axios.post(
      '/users/2fa/verify',
      { token: verificationCode.value }, // Changé de 'code' à 'token' pour matcher l'API
      { 
        withCredentials: true,
        timeout: 10000 // 10 secondes timeout
      }
    )

    if (response.data.success) {
      alertMessage.value = t('security.setupSuccess')
      alertType.value = 'success'
      eventBus.emit('2fa-enabled')
      setTimeout(closeModal, 2000)
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    isLoading.value = false
  }
}

// Cleanup
onBeforeUnmount(() => {
  eventBus.off('show-2fa-qr', openModal)
})

// Event listeners
eventBus.on('show-2fa-qr', openModal)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.alert {
  padding: 0.75rem 1rem;
  margin: 1rem 0;
  border-radius: 4px;
  font-size: 0.9rem;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.qr-container {
  margin: 2rem auto;
  max-width: 200px;
}

.qr-container img {
  width: 100%;
  height: auto;
}

.instructions {
  margin-bottom: 1.5rem;
  color: #666;
}

.verification-section {
  margin-bottom: 1.5rem;
}

.input-group {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.verification-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  width: 120px;
  text-align: center;
  letter-spacing: 2px;
}

.verification-input:disabled {
  background-color: #f5f5f5;
}

.input-help {
  color: #666;
  font-size: 0.8rem;
}

.verify-btn {
  background-color: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  min-width: 100px;
  position: relative;
}

.verify-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.close-btn {
  background-color: #f44336;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.close-btn:hover:not(:disabled) {
  background-color: #d32f2f;
}

.close-btn:disabled {
  background-color: #ffcdd2;
  cursor: not-allowed;
}

.loader {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid #ffffff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>