<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUserStatus } from '@/composables/useUserStatus'
import eventBus from '@/utils/eventBus'

const emit = defineEmits(['success', 'switch-mode'])
const router = useRouter()
const authStore = useAuthStore()
const { initializeWebSocket } = useUserStatus()

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const { signIn } = useAuth()

const handleSignIn = async () => {
  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const result = await signIn({
      email: email.value,
      password: password.value,
    })
    
    console.log('Complete result:', result)
    
    if (result.success) {
      if (result.requires2FA) {
        console.log('2FA required, waiting for validation...')
        // 2FA modal will be displayed via eventBus
        // Store partial data for later use
        const userData = result.data
        
        // Listen for 2FA success event
        eventBus.on('2fa-success', (data) => {
          console.log('2FA validated, logging in...')
          authStore.login(userData.user, userData.token)
          router.push('/pong')
          // Don't forget to remove the listener
          eventBus.off('2fa-success')
        })
        return
      }
      
      // Case without 2FA
      authStore.login(result.data.user, result.data.token)
      
      // Initialize WebSocket
      initializeWebSocket()
      
      email.value = ''
      password.value = ''
      error.value = ''
      emit('success', result.data)
      
      // Redirect to Pong page
      router.push('/pong')
    }
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

const handle42SignIn = () => {
  window.location.href = '/users/fortytwo/login/'
}

const forgotPassword = () => {
  console.log('Forgot password clicked')
}
</script>

<template>
  <div class="form-content">
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div class="form-group">
      <label for="email">{{ $t('login.email') }}</label>
      <input
        id="email"
        type="email"
        v-model="email"
        :placeholder="$t('login.placeholders.email')"
        class="input-field"
        :disabled="isLoading"
        @keyup.enter="handleSignIn"
      />
    </div>

    <div class="form-group">
      <label for="password">{{ $t('login.password') }}</label>
      <input
        id="password"
        type="password"
        v-model="password"
        :placeholder="$t('login.placeholders.password')"
        class="input-field"
        :disabled="isLoading"
        @keyup.enter="handleSignIn"
      />
    </div>

    <div class="button-group">
      <button 
        class="submit-button" 
        @click="handleSignIn"
        :disabled="isLoading"
      >
        <span v-if="isLoading">Connexion en cours...</span>
        <span v-else>{{ $t('login.signIn') }}</span>
      </button>
    </div>

    <div class="social-buttons">
      <button 
        class="fortytwo-button"
        @click="handle42SignIn"
        :disabled="isLoading"
      >
        {{ $t('login.connectWith') }} <img src="@/assets/42_logo.png" alt="42 Logo" />
      </button>
    </div>

    <div class="forgot-password">
      <a href="#" @click.prevent="forgotPassword">
        {{ $t('login.forgotPassword') }}
      </a>
    </div>
  </div>
</template>

<style scoped>
.form-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 10px;
  text-align: center;
}

.form-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #1e1e1e;
  font-size: 16px;
  font-weight: 400;
  line-height: 22.4px;
}

.input-field {
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  font-size: 16px;
  width: calc(100% - 32px);
}

.input-field:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.button-group {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.submit-button {
  padding: 12px 24px;
  background: #1e1e1e;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
  min-width: 120px;
}

.submit-button:hover:not(:disabled) {
  background: #333;
}

.submit-button:disabled {
  background: #666;
  cursor: not-allowed;
}

.social-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.fortytwo-button {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.fortytwo-button img {
  width: 20px;
  height: 20px;
}

.fortytwo-button {
  background-color: #00babc;
  color: white;
}

.fortytwo-button:hover {
  background-color: #00a2a4;
}

.forgot-password {
  text-align: center;
}

.forgot-password a {
  color: #1e1e1e;
  text-decoration: none;
  font-size: 14px;
}

.forgot-password a:hover {
  text-decoration: underline;
}
</style>
