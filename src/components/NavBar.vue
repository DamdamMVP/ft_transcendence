<script setup>
import IconGolem from './icons/IconGolem.vue'
import { useAuthStore } from '../stores/authStore'
import IconSettings from './icons/IconSettings.vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = () => {
  authStore.login()
  router.push('/profil/pong')
}
</script>

<template>
  <div class="header">
    <div class="logo-container">
      <div class="logo-border">
        <IconGolem style="color: var(--primary-color)" />
      </div>
    </div>
    <div class="spacer"></div>

    <div class="auth-buttons" v-if="!authStore.isAuthenticated">
      <button class="sign-in-button" @click="handleLogin">
        {{ $t('navbar.connect') }}
      </button>
      <button class="register-button" @click="handleLogin">
        {{ $t('navbar.create') }}
      </button>
    </div>

    <div class="user-options" v-else>
      <router-link to="/profil/pong" class="profil-link">
        {{ $t('navbar.profil') }}
      </router-link>
      <router-link to="/settings" class="settings-link">
        <IconSettings />
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.header {
  align-self: stretch;
  padding: 32px 0;
  margin: 0;
  background: var(--background-color);
  border-bottom: 1px solid var(--secondary-color);
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 24px;
  box-sizing: border-box;
}

.logo-container {
  padding-left: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo-border {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.spacer {
  flex: 1;
}

.auth-buttons,
.user-options {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sign-in-button,
.register-button,
.logout-button {
  flex: 1;
  height: 32px;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid;
  font-family: Inter, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 16px;
  cursor: pointer;
  transition:
    background 0.3s,
    border-color 0.3s,
    color 0.3s;
}

.sign-in-button {
  background: var(--background-color);
  border-color: var(--secondary-color);
  color: var(--text-color);
}

.sign-in-button:hover {
  background: var(--secondary-color);
  color: var(--text-color);
}

.register-button {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--text-color);
}

.register-button:hover {
  background: var(--info-color);
  border-color: var(--info-color);
  color: var(--text-color);
}

.logout-button {
  background: var(--secondary-color);
  border-color: var(--secondary-color);
  color: white;
}

.logout-button:hover {
  background: var(--danger-color);
  border-color: var(--danger-color);
}

.profil-link,
.settings-link {
  text-decoration: none;
  color: var(--primary-color);
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  margin-right: 16px;
}

.profil-link:hover,
.settings-link:hover {
  text-decoration: underline;
}
</style>
