<script setup>
import { ref } from 'vue'

const isLogin = ref(true)
const email = ref('')
const password = ref('')
const username = ref('')
const confirmPassword = ref('')

const handleSignIn = () => {
  console.log('Sign In clicked with:', email.value, password.value)
}

const handleSignUp = () => {
  console.log('Sign Up clicked with:', username.value, email.value, password.value)
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  email.value = ''
  password.value = ''
  username.value = ''
  confirmPassword.value = ''
}

const forgotPassword = () => {
  console.log('Forgot password clicked')
}
</script>

<template>
  <div class="container">
    <div class="form-container">
      <div class="mode-toggle">
        <button 
          :class="{ active: isLogin }" 
          @click="toggleMode"
        >
          {{ $t('auth.login') }}
        </button>
        <button 
          :class="{ active: !isLogin }" 
          @click="toggleMode"
        >
          {{ $t('auth.signup') }}
        </button>
      </div>

      <template v-if="!isLogin">
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
      </template>

      <div class="form-group">
        <label for="email">{{ isLogin ? $t('login.email') : $t('signup.email') }}</label>
        <input
          id="email"
          type="email"
          v-model="email"
          :placeholder="isLogin ? $t('login.placeholders.email') : $t('signup.placeholders.email')"
          class="input-field"
        />
      </div>

      <div class="form-group">
        <label for="password">{{ isLogin ? $t('login.password') : $t('signup.password') }}</label>
        <input
          id="password"
          type="password"
          v-model="password"
          :placeholder="isLogin ? $t('login.placeholders.password') : $t('signup.placeholders.password')"
          class="input-field"
        />
      </div>

      <template v-if="!isLogin">
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
      </template>

      <div class="button-group">
        <button class="submit-button" @click="isLogin ? handleSignIn : handleSignUp">
          {{ isLogin ? $t('login.signIn') : $t('signup.signUp') }}
        </button>
      </div>

      <div v-if="isLogin" class="forgot-password">
        <a href="#" @click.prevent="forgotPassword">{{
          $t('login.forgotPassword')
        }}</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.form-container {
  width: 700px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 24px;
}

.mode-toggle {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 8px;
}

.mode-toggle button {
  padding: 8px 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.mode-toggle button.active {
  border-bottom: 2px solid #1e1e1e;
  font-weight: bold;
}

.mode-toggle button:hover {
  opacity: 0.8;
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
  font-family: Inter, sans-serif;
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
