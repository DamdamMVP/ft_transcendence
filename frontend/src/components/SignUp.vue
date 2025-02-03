<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const emit = defineEmits(['success', 'switch-mode'])

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const showGdprModal = ref(false);
const gdprConsent = ref(false);

const { signUp } = useAuth()

const handleSignUp = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Les mots de passe ne correspondent pas'
    return
  }

  if (!gdprConsent.value) {
	showGdprModal.value = true;
	return;
  }

  try {
    await signUp({
      username: username.value,
      email: email.value,
      password: password.value,
    })

    username.value = ''
    email.value = ''
    password.value = ''
    confirmPassword.value = ''
    error.value = ''
    gdprConsent.value = false;
    
    emit('success')
    emit('switch-mode')
  } catch (err) {
    error.value = err.message
  }
}
const acceptGdpr = () => {
  gdprConsent.value = true
  showGdprModal.value = false
  handleSignUp()
}

const declineGdpr = () => {
  showGdprModal.value = false
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
	<div v-if="showGdprModal" class="modal-backdrop">
      <div class="modal">
        <h2>{{ $t('gdpr.title') }}</h2>
        <p>{{ $t('gdpr.message') }}</p>
        <div class="modal-actions">
			<button @click="acceptGdpr">{{ $t('gdpr.accept') }}</button>
			<button @click="declineGdpr">{{ $t('gdpr.decline') }}</button>
        </div>
      </div>
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
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: white;
  padding: 24px;
  border-radius: 8px;
  max-width: 500px;
  width: 100%;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 16px;
}

.modal-actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.modal-actions button:first-child {
  background: #1e1e1e;
  color: white;
}

.modal-actions button:first-child:hover {
  background: #333;
}

.modal-actions button:last-child {
  background: #f8d7da;
  color: #dc3545;
}

.modal-actions button:last-child:hover {
  background: #f1b0b7;
}
</style>