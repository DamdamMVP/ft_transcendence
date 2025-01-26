<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const emit = defineEmits(['success', 'switch-mode'])
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const { signIn } = useAuth()

const handleSignIn = async () => {
  if (!email.value || !password.value) {
    error.value = 'Veuillez remplir tous les champs'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const result = await signIn({
      email: email.value,
      password: password.value,
    })
    
    if (result.success) {
      email.value = ''
      password.value = ''
      error.value = ''
      emit('success', result.data)
      // Redirection vers la page Pong
      router.push('/pong')
    }
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

const forgotPassword = () => {
  console.log('Forgot password clicked')
}
</script>

<template>
  <div class="form-container">
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

    <div class="forgot-password">
      <a href="#" @click.prevent="forgotPassword">
        {{ $t('login.forgotPassword') }}
      </a>
    </div>
  </div>
</template>

<style scoped>
.form-container {
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
