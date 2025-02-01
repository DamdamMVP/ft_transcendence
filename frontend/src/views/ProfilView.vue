<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import ProfilLeft from '../components/profil/ProfilLeft.vue'

const route = useRoute()
const router = useRouter()
const userExists = ref(false)

// Vérifier si l'utilisateur existe
const checkUserExists = async () => {
  try {
    await axios.get(`/users/read/${route.params.id_user}`, {
      withCredentials: true,
    })
    userExists.value = true
  } catch (err) {
    // Si l'utilisateur n'existe pas (404) ou autre erreur, rediriger vers la page 404
    router.push('/404')
  }
}

onMounted(async () => {
  await checkUserExists()
})
</script>

<template>
  <main v-if="userExists" class="profil-view">
    <div class="profil-content">
      <ProfilLeft />
      <router-view />
    </div>
  </main>
</template>

<style scoped>
.profil-view {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  min-height: 80vh;
  margin: 0;
  padding: 2.5rem;
  background: var(--background-color);
  position: relative;
  animation: fadeIn 0.6s ease;
  overflow: hidden;
}

.profil-content {
  width: 100%;
  max-width: 1400px;
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  margin-top: 2rem;
  position: relative;
  animation: slideUp 0.8s ease;
  z-index: 1;
}

/* Effets de fond améliorés */
.profil-view::before,
.profil-view::after {
  content: '';
  position: absolute;
  pointer-events: none;
}

.profil-view::before {
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    circle at top right,
    var(--primary-shadow-color) 0%,
    transparent 70%
  );
  opacity: 0.15;
}

.profil-view::after {
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    var(--primary-color) 0%,
    transparent 100%
  );
  opacity: 0.05;
  backdrop-filter: blur(100px);
}

/* Style pour les composants enfants */
:deep(.profil-card),
:deep(.profil-stats),
:deep(.profil-achievements) {
  background: var(--background-secondary-color);
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

:deep(.profil-card:hover),
:deep(.profil-stats:hover),
:deep(.profil-achievements:hover) {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px var(--primary-shadow-color);
}

/* Animations améliorées */
@keyframes fadeIn {
  0% {
    opacity: 0;
    transform: scale(0.98);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translateY(30px) scale(0.98);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Effet de brillance */
:deep(.shine-effect) {
  position: relative;
  overflow: hidden;
}

:deep(.shine-effect::before) {
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
  animation: shine 3s infinite;
}

@keyframes shine {
  0% {
    transform: translateX(-100%) rotate(45deg);
  }
  100% {
    transform: translateX(100%) rotate(45deg);
  }
}

/* Media Queries améliorés */
@media (max-width: 1400px) {
  .profil-content {
    max-width: 95%;
    gap: 2rem;
  }
}

@media (max-width: 1200px) {
  .profil-content {
    max-width: 90%;
    gap: 1.5rem;
  }
}

@media (max-width: 968px) {
  .profil-view {
    padding: 1.5rem;
  }
  
  .profil-content {
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .profil-view {
    padding: 1rem;
  }

  .profil-content {
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  :deep(.profil-card),
  :deep(.profil-stats),
  :deep(.profil-achievements) {
    width: 100%;
  }
}

/* Support du mode sombre */
@media (prefers-color-scheme: dark) {
  .profil-view::after {
    opacity: 0.07;
  }
}
</style>