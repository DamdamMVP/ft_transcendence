<script setup>
import { defineProps } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const props = defineProps({
  items: {
    type: Array,
    default: () => ['Pong', 'Catch'],
  },
})

const { t } = useI18n()
const route = useRoute()
</script>

<template>
  <nav class="navbar-profil">
    <ul class="navbar-list">
      <li v-for="(item, index) in items" :key="index" class="navbar-item">
        <router-link
          :to="`/${route.params.id_user}/profil/${item.toLowerCase().replace(/ /g, '-')}`"
          class="navbar-link"
          active-class="navbar-link-selected"
        >
          {{ t(`navbarProfil.${item}`) }}
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.navbar-profil {
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--background-secondary-color);
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  padding: 1rem 3.7rem;
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.6s ease;
}

/* Effet de fond subtil */
.navbar-profil::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at top right,
    var(--primary-shadow-color) 0%,
    transparent 70%
  );
  opacity: 0.1;
  pointer-events: none;
}

.navbar-list {
  display: flex;
  gap: 1.5rem;
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
  z-index: 1;
}

.navbar-item {
  font-size: 1rem;
  font-weight: 600;
  position: relative;
}

.navbar-link {
  text-decoration: none;
  color: var(--text-color);
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  display: inline-block;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.navbar-link::before {
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

.navbar-link:hover {
  color: white;
  transform: translateY(-2px);
}

.navbar-link:hover::before {
  opacity: 1;
  transform: translateY(0);
}

.navbar-link-selected {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover-color));
  color: white;
  box-shadow: 0 4px 15px var(--primary-shadow-color);
}

.navbar-link-selected:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px var(--primary-shadow-color);
}

/* Animation d'entrée */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Effet de brillance */
.navbar-link::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 0%,
    rgba(255, 255, 255, 0.1) 50%,
    transparent 100%
  );
  transform: rotate(45deg);
  transition: all 0.3s ease;
  opacity: 0;
}

.navbar-link:hover::after {
  animation: shine 1.5s ease;
}

@keyframes shine {
  0% {
    transform: translateX(-100%) rotate(45deg);
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    transform: translateX(100%) rotate(45deg);
    opacity: 0;
  }
}

/* Media Queries */
@media (max-width: 768px) {
  .navbar-profil {
    padding: 0.8rem 1rem;
  }

  .navbar-list {
    gap: 1rem;
  }

  .navbar-link {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
}
</style>