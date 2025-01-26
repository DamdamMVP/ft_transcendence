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
      <router-link to="/pong" class="nav-link">
        {{ $t('navbar.pong') }}
      </router-link>
      <router-link to="/profil/pong" class="nav-link">
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
  padding-right: 32px;
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

.nav-link {
  color: var(--text-color);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: var(--secondary-color);
}

.settings-link {
  color: var(--text-color);
  text-decoration: none;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  transition: background-color 0.3s;
}

.settings-link:hover {
  background-color: var(--secondary-color);
}

.sign-in-button {
  background: transparent;
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.sign-in-button:hover {
  background: var(--primary-color);
  color: var(--background-color);
}

.register-button {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--background-color);
}

.register-button:hover {
  opacity: 0.9;
}
</style>
