<script setup>
import { ref } from 'vue'

const email = ref('')
const password = ref('')

const handleSignIn = () => {
  console.log('Sign In clicked with:', email.value, password.value)
}

const forgotPassword = () => {
  console.log('Forgot password clicked')
}
</script>

<template>
  <div class="container">
    <!-- Form Section -->
    <div class="form-container">
      <div class="form-group">
        <label for="email">{{ $t('login.email') }}</label>
        <input
          id="email"
          type="email"
          v-model="email"
          :placeholder="$t('login.placeholders.email')"
          class="input-field"
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
        />
      </div>

      <div class="button-group">
        <button class="submit-button" @click="handleSignIn">
          {{ $t('login.signIn') }}
        </button>
      </div>

      <div class="forgot-password">
        <a href="#" @click.prevent="forgotPassword">{{
          $t('login.forgotPassword')
        }}</a>
      </div>

      <div class="button-group">
        <button class="submit-button" @click="$router.push('/profil')">
          {{ $t('login.goToProfil') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 85vh;
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
  font-family: Inter, sans-serif;
  color: #b3b3b3;
  width: 100%;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: #1e90ff;
}

.button-group {
  width: 100%;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.submit-button {
  flex: 1;
  height: 40px;
  padding: 12px;
  background: #2c2c2c;
  border: 1px solid #2c2c2c;
  border-radius: 8px;
  color: #f5f5f5;
  font-size: 16px;
  font-family: Inter, sans-serif;
  font-weight: 400;
  line-height: 16px;
  cursor: pointer;
  transition:
    background 0.3s,
    border-color 0.3s;
}

.submit-button:hover {
  background: #3a3a3a;
}

.forgot-password {
  width: 100%;
  display: flex;
  justify-content: flex-start;
}

.forgot-password a {
  color: #1e1e1e;
  font-size: 16px;
  font-family: Inter, sans-serif;
  font-weight: 400;
  line-height: 22.4px;
  text-decoration: underline;
  cursor: pointer;
}

.forgot-password a:hover {
  color: #1e90ff;
}
</style>
