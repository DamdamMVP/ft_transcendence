<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import eventBus from '../../utils/eventBus'
import { useRoute } from 'vue-router'
import NavBarProfil from '../../components/profil/NavBarProfil.vue'

const { t } = useI18n()
const route = useRoute()
const userHistory = ref([]) // Initialiser comme un tableau vide
const loading = ref(true)
const profileUser = ref(null)
const error = ref(null)

// Récupérer les informations de l'utilisateur
const fetchUserProfile = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/users/read/${route.params.id_user}`, {
      withCredentials: true,
    })
    profileUser.value = response.data
  } catch (err) {
    console.error('Erreur lors de la récupération du profil:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Récupérer l'historique pour les stats
const fetchHistory = async () => {
  try {
    const response = await axios.get(
      `/users/histories/user/${route.params.id_user}`,
      {
        withCredentials: true,
      }
    )
    // S'assurer que la réponse est un tableau
    userHistory.value = Array.isArray(response.data) ? response.data : []
  } catch (err) {
    console.error('Erreur lors de la récupération des stats:', err)
    error.value = err.message
    userHistory.value = [] // Réinitialiser à un tableau vide en cas d'erreur
  }
}

// Recharger les données quand l'ID change
const reloadData = async () => {
  error.value = null
  await Promise.all([fetchUserProfile(), fetchHistory()])
}

// Observer les changements de route
watch(
  () => route.params.id_user,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      reloadData()
    }
  },
  { immediate: true }
)

// Statistiques globales
const stats = computed(() => {
  // Vérifier que userHistory.value est un tableau
  if (!Array.isArray(userHistory.value)) {
    return {
      victories: 0,
      defeats: 0,
      draws: 0,
      winRate: 0,
    }
  }

  const victories = userHistory.value.filter(
    (match) => match && match.user_score > match.guest_score
  ).length
  const defeats = userHistory.value.filter(
    (match) => match && match.user_score < match.guest_score
  ).length
  const draws = userHistory.value.filter(
    (match) => match && match.user_score === match.guest_score
  ).length
  const total = victories + defeats + draws
  const winRate = total > 0 ? Math.round((victories / total) * 100) : 0

  return {
    victories,
    defeats,
    draws,
    winRate,
  }
})

// URL de la photo de profil
const profilePhotoUrl = computed(() => {
  if (!profileUser.value?.profile_picture) {
    return '/default-avatar.png'
  }
  // S'assurer que l'URL est complète et à jour
  const baseUrl = import.meta.env.VITE_API_BASE_URL.endsWith('/')
    ? import.meta.env.VITE_API_BASE_URL.slice(0, -1)
    : import.meta.env.VITE_API_BASE_URL
  return `${baseUrl}${profileUser.value.profile_picture}`
})

// Mettre à jour l'historique quand un événement est reçu
const updateHistory = (newHistory) => {
  userHistory.value = Array.isArray(newHistory) ? newHistory : []
}

onMounted(async () => {
  try {
    await reloadData()
    // S'abonner à l'événement de mise à jour
    eventBus.on('history-updated', updateHistory)
  } catch (err) {
    console.error('Erreur lors du chargement initial:', err)
    error.value = err.message
  }
})

onUnmounted(() => {
  // Se désabonner de l'événement
  eventBus.off('history-updated', updateHistory)
})
</script>

<template>
	<div class="page-container">
		<NavBarProfil class="nav-section" />
  <div class="profile-container">
    <div v-if="loading" class="loading">Chargement...</div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="profile-card">
      <h2 class="profile-name">
        {{ profileUser.username || 'Utilisateur' }}
      </h2>
      <img
        :src="profilePhotoUrl"
        :alt="profileUser.username || 'Profile Picture'"
        class="profile-picture"
      />
      <div class="stats-container">
        <div class="stat-item">
          <span class="stat-label">{{ t('stats.victories') }}</span>
          <span class="stat-value victories">{{ stats.victories }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">{{ t('stats.defeats') }}</span>
          <span class="stat-value defeats">{{ stats.defeats }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">{{ t('stats.winRate') }}</span>
          <span class="stat-value">{{ stats.winRate }}%</span>
        </div>
      </div>
      <p class="profile-stats" v-if="profileUser?.stats">
        W: {{ profileUser.stats.wins || 0 }} | L:
        {{ profileUser.stats.losses || 0 }}
      </p>
    </div>
  </div>
</div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.nav-section {
  margin: 0 auto;
}

.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
  animation: fadeIn 0.6s ease;
}

.profile-card {
  width: 300px;
  padding: 2rem;
  background: var(--background-secondary-color);
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.profile-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px var(--primary-shadow-color);
}

/* Effet de fond subtil */
.profile-card::before {
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

.profile-picture {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  margin: 1rem auto;
  border: 3px solid var(--primary-color);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
  transition: all 0.3s ease;
}

.profile-card:hover .profile-picture {
  transform: scale(1.05);
  box-shadow: 0 8px 20px var(--primary-shadow-color);
}

.profile-name {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 1rem 0;
  color: var(--primary-color);
  text-shadow: 0 0 10px var(--primary-shadow-color);
}

.stats-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 2px solid var(--primary-color);
  position: relative;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateX(8px);
  background: rgba(0, 0, 0, 0.3);
}

.stat-label {
  color: var(--text-color);
  font-weight: 600;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--text-color);
}

.victories {
  color: var(--success-color);
  text-shadow: 0 0 10px rgba(46, 204, 113, 0.3);
}

.defeats {
  color: var(--error-color);
  text-shadow: 0 0 10px rgba(231, 76, 60, 0.3);
}

.profile-stats {
  font-size: 1.1rem;
  color: var(--text-color);
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: var(--text-color);
  animation: fadeIn 0.4s ease;
}

.error {
  color: var(--error-color);
}

/* Animations */
@keyframes fadeIn {
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
@media (max-width: 768px) {
  .profile-card {
    width: 90%;
    padding: 1.5rem;
  }

  .profile-name {
    font-size: 1.5rem;
  }

  .profile-picture {
    width: 100px;
    height: 100px;
  }

  .stat-label {
    font-size: 1rem;
  }

  .stat-value {
    font-size: 1.1rem;
  }
}
</style>