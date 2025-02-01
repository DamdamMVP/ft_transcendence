<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import ProfilLeft from '../components/profil/ProfilLeft.vue'
import NavBarProfil from '../components/profil/NavBarProfil.vue'

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
    <NavBarProfil />
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
  width: 100%;
  margin: 0;
  padding: 2rem;
  background: var(--background-color);
  position: relative;
  animation: fadeIn 0.6s ease;
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
}

/* Effet de fond subtil */
.profil-view::before {
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

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Media Queries */
@media (max-width: 1200px) {
  .profil-content {
    max-width: 95%;
    gap: 2rem;
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
}
</style>