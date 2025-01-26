<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const emit = defineEmits(['success', 'switch-mode'])

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')

const { signUp } = useAuth()

const handleSignUp = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Les mots de passe ne correspondent pas'
    return
  }

  try {
    await signUp({
      username: username.value,
      email: email.value,
      password: password.value,
    })
    
    // Réinitialiser les champs
    username.value = ''
    email.value = ''
    password.value = ''
    confirmPassword.value = ''
    error.value = ''
    
    emit('success')
    emit('switch-mode')
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <div class="form-content">
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div class="form-group">
      <label for="username">{{ $t('signup.username') }}</label>
      <input
        id="username"
        type="text"
        v-model="username"
        :placeholder="$t('signup.placeholders.username')"
        class="input-field"
      />
    </div>

    <div class="form-group">
      <label for="email">{{ $t('signup.email') }}</label>
      <input
        id="email"
        type="email"
        v-model="email"
        :placeholder="$t('signup.placeholders.email')"
        class="input-field"
      />
    </div>

    <div class="form-group">
      <label for="password">{{ $t('signup.password') }}</label>
      <input
        id="password"
        type="password"
        v-model="password"
        :placeholder="$t('signup.placeholders.password')"
        class="input-field"
      />
    </div>

    <div class="form-group">
      <label for="confirmPassword">{{ $t('signup.confirmPassword') }}</label>
      <input
        id="confirmPassword"
        type="password"
        v-model="confirmPassword"
        :placeholder="$t('signup.placeholders.confirmPassword')"
        class="input-field"
      />
    </div>

    <div class="button-group">
      <button class="submit-button" @click="handleSignUp">
        {{ $t('signup.signUp') }}
      </button>
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
  transition: background-color 0.2s;
}

.submit-button:hover {
  background: #333;
}
</style>
