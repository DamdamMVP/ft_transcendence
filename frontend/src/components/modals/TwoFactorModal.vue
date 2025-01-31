<template>
  <div
    v-if="show"
    class="modal-overlay"
    @keyup.esc="!isLoading && closeModal()"
  >
    <div class="modal-content" @click.stop>
      <button class="close-icon" @click="closeModal" :disabled="isLoading">
        ×
      </button>
      <h2>
        {{
          isVerificationMode ? t('security.verify2FA') : t('security.setup2FA')
        }}
      </h2>

      <!-- Alert pour les messages d'erreur/succès -->
      <div v-if="alertMessage" :class="['alert', `alert-${alertType}`]">
        {{ alertMessage }}
      </div>

      <!-- Mode QR Code -->
      <div v-if="qrCode && !isVerificationMode" class="qr-container">
        <img :src="`data:image/svg+xml;base64,${qrCode}`" alt="QR Code" />
        <p class="instructions">{{ t('security.scanQRCode') }}</p>
      </div>

      <!-- Mode Vérification -->
      <template v-else-if="isVerificationMode">
        <p class="instructions">{{ t('security.enter2FACode') }}</p>
        <div class="input-group">
          <input
            ref="codeInput"
            type="text"
            v-model="verificationCode"
            placeholder=""
            class="verification-input"
            maxlength="6"
            pattern="\d*"
            @input="validateInput"
            @keyup.enter="isValidCode && verifyCode()"
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
      </template>

      <button
        v-if="!isVerificationMode"
        class="close-btn"
        @click="closeModal"
        :disabled="isLoading"
      >
        {{ t('common.close') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../composables/useAuth'
import axios from 'axios'
import eventBus from '../../utils/eventBus'

const { t } = useI18n()
const { verify2FAAndComplete } = useAuth()

// State
const show = ref(false)
const qrCode = ref('')
const verificationCode = ref('')
const isLoading = ref(false)
const alertMessage = ref('')
const alertType = ref('info')
const isVerificationMode = ref(false)
const codeInput = ref(null) // Référence pour l'input

// Computed
const isValidCode = computed(() => {
  return /^\d{6}$/.test(verificationCode.value)
})

// Input validation
const validateInput = (event) => {
  const value = event.target.value
  verificationCode.value = value.replace(/\D/g, '').slice(0, 6)
}

// Gestion des erreurs API
const handleApiError = async (error) => {
  isLoading.value = false
  verificationCode.value = '' // Vider le champ
  if (error.message === 'invalidCode') {
    alertMessage.value = t('security.invalidCode')
  } else {
    alertMessage.value =
      t(`errors.${error.message}`) || t('errors.unknownError')
  }
  alertType.value = 'error'

  // Attendre que le DOM soit mis à jour avec le message d'erreur
  await nextTick()
  // Remettre le focus sur l'input
  if (codeInput.value) {
    codeInput.value.focus()
  }

  setTimeout(() => {
    alertMessage.value = ''
  }, 5000)
}

// Gestionnaire d'événement pour la touche Échap
const handleEscape = (e) => {
  if (e.key === 'Escape' && show.value && !isLoading.value) {
    closeModal()
  }
}

// Ajouter/retirer l'écouteur quand le modal s'ouvre/se ferme
const setupEscapeListener = () => {
  document.addEventListener('keyup', handleEscape)
}

const removeEscapeListener = () => {
  document.removeEventListener('keyup', handleEscape)
}

// Ouvrir le modal avec le QR code
const openModal = (qrCodeData) => {
  qrCode.value = qrCodeData
  show.value = true
  isVerificationMode.value = false
  alertMessage.value = t('security.scanInstructions')
  alertType.value = 'info'
}

// Ouvrir le modal pour la vérification
const openVerificationModal = async () => {
  show.value = true
  isVerificationMode.value = true
  qrCode.value = ''
  verificationCode.value = ''
  alertMessage.value = ''
  alertType.value = 'info'

  setupEscapeListener() // Ajouter l'écouteur

  // Attendre que le DOM soit mis à jour
  await nextTick()
  // Mettre le focus sur l'input
  if (codeInput.value) {
    codeInput.value.focus()
  }
}

const closeModal = () => {
  if (!isLoading.value) {
    show.value = false
    verificationCode.value = ''
    alertMessage.value = ''
    if (isVerificationMode.value) {
      eventBus.emit('2fa-cancelled')
    }
    removeEscapeListener() // Retirer l'écouteur
  }
}

const verifyCode = async () => {
  if (!isValidCode.value || isLoading.value) return

  isLoading.value = true
  try {
    if (isVerificationMode.value) {
      const result = await verify2FAAndComplete(verificationCode.value)
      if (result.success) {
        show.value = false
        eventBus.emit('2fa-verified')
      }
    } else {
      const response = await axios.post('/users/2fa/verify', {
        token: verificationCode.value,
      })

      if (response.status === 200) {
        alertMessage.value = t('security.setupSuccess')
        alertType.value = 'success'
        setTimeout(() => {
          show.value = false
        }, 2000)
      }
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  eventBus.on('show-2fa-qr', openModal)
  eventBus.on('show-2fa-verification', openVerificationModal)
})

onBeforeUnmount(() => {
  eventBus.off('show-2fa-qr', openModal)
  eventBus.off('show-2fa-verification', openVerificationModal)
  removeEscapeListener()
})
</script>

<style scoped>
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
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  text-align: center;
  position: relative;
}

.input-group {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin: 1rem 0;
}

.verification-input {
  width: 120px;
  padding: 0.5rem;
  font-size: 1.2rem;
  text-align: center;
  letter-spacing: 0.2rem;
  border: 2px solid #ccc;
  border-radius: 4px;
}

.verify-btn {
  padding: 0.5rem 1rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.verify-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.instructions {
  margin: 1.5rem 0;
  color: #666;
}

.qr-container {
  margin: 1rem 0;
}

.qr-container img {
  max-width: 200px;
  margin: 0 auto;
}

.input-help {
  color: #666;
  font-size: 0.9rem;
}

.alert {
  margin: 1rem 0;
  padding: 0.75rem;
  border-radius: 4px;
}

.alert-error {
  background-color: #ffebee;
  color: #c62828;
}

.alert-success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.alert-info {
  background-color: #e3f2fd;
  color: #1565c0;
}

.loader {
  display: inline-block;
  width: 1rem;
  height: 1rem;
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

.close-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 24px;
  color: #ff0000;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-icon:hover {
  background-color: rgba(255, 0, 0, 0.1);
}

.close-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
