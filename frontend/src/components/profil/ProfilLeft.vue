<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import eventBus from '../../utils/eventBus'
import { useRoute } from 'vue-router'

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
</template>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.profile-card {
  width: 250px;
  padding: 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  background-color: var(--background-color);
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.profile-picture {
  border-radius: 50%;
  width: 100px;
  height: 100px;
  object-fit: cover;
  margin-bottom: 16px;
}

.profile-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--text-color);
}

.profile-stats {
  font-size: 16px;
  color: var(--text-color);
}

.stats-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid #d9d9d9;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background-color: var(--background-color);
  border-radius: 4px;
}

.stat-label {
  color: var(--text-color);
  font-weight: 500;
}

.stat-value {
  font-weight: bold;
}

.victories {
  color: #33a852;
}

.defeats {
  color: #ff4d4d;
}

.loading,
.error {
  text-align: center;
  padding: 20px;
  font-size: 16px;
  color: var(--text-color);
}

.error {
  color: #ff4d4d;
}
</style>
