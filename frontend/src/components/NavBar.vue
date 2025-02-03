<script setup>
import IconGolem from './icons/IconGolem.vue'
import { useAuthStore } from '../stores/authStore'
import IconSettings from './icons/IconSettings.vue'

const authStore = useAuthStore()
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
  padding: 1.5rem 0;
  background: var(--background-color);
  border-bottom: 2px solid rgba(52, 152, 219, 0.2);
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 24px;
  box-sizing: border-box;
  position: relative;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
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
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
}

.logo-border::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: var(--primary-color);
  border-radius: 12px;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.3s ease;
  z-index: -1;
}

.logo-border:hover::after {
  opacity: 0.2;
  transform: scale(1.1);
}

.logo-border .nav-golem {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s ease;
}

.logo-border:hover .nav-golem {
  transform: scale(1.1);
}

.spacer {
  flex: 1;
}

.user-options {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-right: 32px;
}

.nav-link {
  color: var(--text-color);
  text-decoration: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--primary-color);
  opacity: 0;
  transform: translateY(100%);
  transition: all 0.3s ease;
  z-index: -1;
  border-radius: 8px;
}

.nav-link:hover {
  color: white;
  transform: translateY(-2px);
}

.nav-link:hover::before {
  opacity: 1;
  transform: translateY(0);
}

.settings-link {
  color: var(--text-color);
  text-decoration: none;
  padding: 0.8rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  background: transparent;
}

.settings-link:hover {
  background: var(--primary-color);
  color: white;
  transform: rotate(90deg);
  box-shadow: 0 4px 15px var(--primary-shadow-color);
}

@keyframes linkHover {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
  100% {
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .header {
    padding: 1rem 0;
  }

  .logo-container {
    padding-left: 16px;
  }

  .user-options {
    padding-right: 16px;
    gap: 8px;
  }

  .nav-link {
    padding: 0.6rem 1rem;
    font-size: 1rem;
  }

  .settings-link {
    padding: 0.6rem;
  }
}
</style>