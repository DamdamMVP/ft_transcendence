<script setup>
import IconGolem from './icons/IconGolem.vue'
import { useAuthStore } from '../stores/authStore'
import IconSettings from './icons/IconSettings.vue'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
</script>

<template>
  <div class="header">
    <div class="logo-container">
      <div class="logo-border">
        <router-link to="/pong" class="nav-golem">
          <IconGolem style="color: var(--primary-color)" />
        </router-link>
      </div>
    </div>
    <div class="spacer"></div>

    <div class="user-options" v-if="authStore.isAuthenticated">
      <router-link to="/pong" class="nav-link">
        {{ $t('navbar.pong') }}
      </router-link>
      <router-link to="/catch" class="nav-link">
        {{ $t('navbar.catch') }}
      </router-link>
      <router-link :to="`/${authStore.user.id}/profil`" class="nav-link">
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

.user-options {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-right: 32px;
}

.nav-link {
  color: var(--text-color);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: var(--primary-color);
  color: var(--text-color);
}

.logo-border .nav-golem {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
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
  background-color: var(--primary-color);
  color: var(--text-color);
}
</style>
