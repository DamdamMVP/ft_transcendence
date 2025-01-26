<script setup>
import { ref } from 'vue'
import SignIn from './SignIn.vue'
import SignUp from './SignUp.vue'

const isLogin = ref(true)

const toggleMode = () => {
  isLogin.value = !isLogin.value
}

const handleAuthSuccess = () => {
  // Gérer le succès de l'authentification
  console.log('Authentification réussie')
}
</script>

<template>
  <div class="container">
    <div class="form-container">
      <div class="mode-toggle">
        <button :class="{ active: isLogin }" @click="toggleMode">
          {{ $t('auth.login') }}
        </button>
        <button :class="{ active: !isLogin }" @click="toggleMode">
          {{ $t('auth.signup') }}
        </button>
      </div>

      <component
        :is="isLogin ? SignIn : SignUp"
        @success="handleAuthSuccess"
        @switch-mode="toggleMode"
      />
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
</style>
