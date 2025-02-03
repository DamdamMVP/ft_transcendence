<template>
  <button 
    :class="['twofa-button', has2FAEnabled ? 'twofa-enabled' : 'twofa-disabled']"
    @click="toggle2FA"
  >
    <i class="icon-lock"></i>
    {{ has2FAEnabled ? $t('settings.disable2FA') : $t('settings.enable2FA') }}
  </button>

  <!-- Modal QR Code -->
  <div v-if="showQRModal" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <h3>{{ $t('settings.enable2FA') }}</h3>
      <div class="qr-container" v-if="qrCode">
        <img :src="`data:image/svg+xml;base64,${qrCode}`" alt="QR Code" />
      </div>
      <div class="verification-section">
        <input
          type="text"
          v-model="verificationCode"
          :placeholder="$t('settings.enterVerificationCode')"
          class="verification-input"
        />
        <button @click="verifyCode" class="verify-button" :disabled="!verificationCode">
          {{ $t('settings.verify') }}
        </button>
      </div>
      <button class="cancel-button" @click="closeModal">
        {{ $t('settings.cancel') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const emit = defineEmits(['showNotification'])
const has2FAEnabled = ref(false)
const showQRModal = ref(false)
const qrCode = ref('')
const verificationCode = ref('')

// Check 2FA status
const check2FAStatus = async () => {
  try {
    const response = await axios.get('/users/2fa/status', { withCredentials: true })
    has2FAEnabled.value = response.data.enabled
  } catch (error) {
    console.error('Error when checking 2FA status:', error)
  }
}

// Enable 2FA
const setup2FA = async () => {
  try {
    const response = await axios.post('/users/2fa/setup', {}, { withCredentials: true })
    if (response.data.qr_code) {
      qrCode.value = response.data.qr_code
      showQRModal.value = true
    }
  } catch (error) {
    emit('showNotification', {
      message: error.response?.data?.error || 'Error when setting up 2FA',
      type: 'error'
    })
  }
}

// Disable 2FA
const disable2FA = async () => {
  try {
    await axios.post('/users/2fa/disable', {}, { withCredentials: true })
    has2FAEnabled.value = false
    emit('showNotification', {
      message: $t('settings.notifications.2faDisabled'),
      type: 'success'
    })
  } catch (error) {
    emit('showNotification', {
      message: error.response?.data?.error || $t('settings.notifications.2faDisableError'),
      type: 'error'
    })
  }
}

// Verify code
const verifyCode = async () => {
  try {
    const response = await axios.post(
      '/users/2fa/verify',
      { token: verificationCode.value }, 
      { withCredentials: true }
    )
    if (response.data.success) { 
      has2FAEnabled.value = true
      closeModal()
      emit('showNotification', {
        message: $t('settings.notifications.2faEnabled'),
        type: 'success'
      })
    }
  } catch (error) {
    emit('showNotification', {
      message: error.response?.data?.error || $t('settings.notifications.2faError'),
      type: 'error'
    })
  }
}

const toggle2FA = () => {
  if (has2FAEnabled.value) {
    disable2FA()
  } else {
    setup2FA()
  }
}

const closeModal = () => {
  showQRModal.value = false
  qrCode.value = ''
  verificationCode.value = ''
}

onMounted(() => {
  check2FAStatus()
})
</script>

<style scoped>
.twofa-button {
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

.twofa-disabled {
  background: var(--primary-color);
  color: white;
}

.twofa-enabled {
  background: var(--secondary-color);
  color: white;
}

.twofa-button:hover {
  opacity: 0.9;
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
  color: var(--text-color);
}

.qr-container {
  margin: 24px 0;
  display: flex;
  justify-content: center;
}

.qr-container img {
  max-width: 200px;
  height: auto;
}

.verification-section {
  margin: 24px 0;
  display: flex;
  gap: 12px;
}

.verification-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--input-background);
  color: var(--text-color);
}

.verify-button {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.verify-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-button {
  width: 100%;
  padding: 8px 16px;
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 12px;
}

.cancel-button:hover {
  opacity: 0.9;
}
</style>
