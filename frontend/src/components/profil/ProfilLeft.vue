<script setup>
import { useAuthStore } from '../../stores/authStore'
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import eventBus from '../../utils/eventBus'

const authStore = useAuthStore()
const { t } = useI18n()
const userHistory = ref([])
const loading = ref(true)

// Statistiques globales
const stats = computed(() => {
  const victories = userHistory.value.filter(
    (match) => match.user_score > match.guest_score
  ).length
  const defeats = userHistory.value.filter(
    (match) => match.user_score < match.guest_score
  ).length
  const draws = userHistory.value.filter(
    (match) => match.user_score === match.guest_score
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

// Récupérer l'historique pour les stats
const fetchHistory = async () => {
  try {
    loading.value = true
    const response = await axios.get(
      `/users/histories/user/${authStore.user.id}`,
      { withCredentials: true }
    )
    userHistory.value = response.data
  } catch (err) {
    console.error('Erreur lors de la récupération des stats:', err)
  } finally {
    loading.value = false
  }
}

// Mettre à jour l'historique quand un événement est reçu
const updateHistory = (newHistory) => {
  userHistory.value = newHistory
}

onMounted(() => {
  fetchHistory()
  // S'abonner à l'événement de mise à jour
  eventBus.on('history-updated', updateHistory)
})

onUnmounted(() => {
  // Se désabonner de l'événement
  eventBus.off('history-updated', updateHistory)
})

const profilePhotoUrl = computed(
  () => `${import.meta.env.VITE_API_BASE_URL}${authStore.user.profile_picture}`
)
</script>

<template>
  <div class="profile-container">
    <div class="profile-card">
      <h2 class="profile-name">
        {{ authStore.user?.username || 'Utilisateur' }}
      </h2>
      <img
        :src="profilePhotoUrl"
        :alt="authStore.user?.username || 'Profile Picture'"
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
      <p class="profile-stats" v-if="authStore.user?.stats">
        W: {{ authStore.user.stats.wins || 0 }} | L:
        {{ authStore.user.stats.losses || 0 }}
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
  width: 100px;
  height: 100px;
  border-radius: 50%;
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
</style>
