<script setup>
import { useRoute } from 'vue-router'
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import eventBus from '../../utils/eventBus'

const route = useRoute()
const authStore = useAuthStore()
const userHistory = ref([])
const loading = ref(true)
const error = ref(null)
const { t } = useI18n()

// Filtre l'historique par jeu et trie par date
const filteredAndSortedHistory = computed(() => {
  return [...userHistory.value]
    .filter(
      (match) =>
        match.game_name?.toLowerCase() === route.params.game?.toLowerCase()
    )
    .sort((a, b) => new Date(b.played_at) - new Date(a.played_at))
})

const fetchHistory = async () => {
  try {
    loading.value = true
    error.value = null
    const userId = route.params.id_user
    const response = await axios.get(
      `/users/histories/user/${userId}`,
      { withCredentials: true }
    )
    userHistory.value = response.data
    // Émettre l'événement de mise à jour
    eventBus.emit('history-updated', response.data)
  } catch (err) {
    error.value = "Erreur lors de la récupération de l'historique"
  } finally {
    loading.value = false
  }
}

// Recharger l'historique quand le jeu change
watch(
  () => route.params.game,
  () => {
    fetchHistory()
  }
)

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="history-container">
    <div class="header">
      <h2>{{ t('history.title') }} - {{ route.params.game }}</h2>
    </div>

    <div v-if="loading" class="loading">
      {{ t('history.loading') }}
    </div>

    <div v-else-if="error" class="error">
      {{ t('history.error') }}
    </div>

    <div v-else-if="filteredAndSortedHistory.length === 0" class="no-history">
      {{ t('history.noGames') }}
    </div>

    <div v-else class="match-list">
      <div
        v-for="match in filteredAndSortedHistory"
        :key="match.id"
        class="match-card"
        :class="{
          'win-card': match.user_score > match.guest_score,
          'loose-card': match.user_score < match.guest_score,
          'draw-card': match.user_score === match.guest_score,
        }"
      >
        <p class="match-opponent">{{ match.guest_name }}</p>
        <p class="match-result">
          <span class="result-text">{{
            match.user_score > match.guest_score
              ? t('history.win')
              : match.user_score < match.guest_score
                ? t('history.loose')
                : t('history.draw')
          }}</span>
          <span class="score-text"
            >: {{ match.user_score }} - {{ match.guest_score }}</span
          >
        </p>
        <p class="match-date">
          {{ new Date(match.played_at).toLocaleDateString() }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-container {
  flex: 0 0 60%;
  padding: 2rem;
  background: var(--background-secondary-color);
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  min-height: 60vh;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
  animation: fadeIn 0.6s ease;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h2 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary-color);
  text-shadow: 0 0 15px var(--primary-shadow-color);
  animation: float 3s ease-in-out infinite;
}

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

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.loading,
.error,
.no-history {
  text-align: center;
  padding: 2rem;
  color: var(--text-color);
  font-size: 1.2rem;
}

.error {
  color: #ff4444;
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
  padding-right: 1rem;
}

.match-card {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  align-items: center;
  /* padding: 1rem; */
  padding-left: 0.7rem;
  padding-right: 0.7rem;
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.win-card {
  background-color: rgba(51, 168, 82, 0.2);
  border: 2px solid #33a852;
}

.loose-card {
  background-color: rgba(255, 77, 77, 0.2);
  border: 2px solid #ff4d4d;
}

.draw-card {
  background-color: rgba(102, 102, 102, 0.2);
  border: 2px solid #666666;
}

.match-card:hover {
  transform: translateX(8px);
}

.match-opponent {
  font-size: 1.1rem;
  font-weight: bold;
  padding-right: 1rem;
  color: var(--text-color);
}

.match-result {
  font-size: 1.1rem;
  text-align: center;
  color: var(--text-color);
}

.match-date {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
  text-align: right;
}

.result-text {
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.score-text {
  font-weight: normal;
  margin-left: 0.5rem;
}

.match-list::-webkit-scrollbar {
  width: 8px;
}

.match-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.match-list::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 4px;
}

.match-list::-webkit-scrollbar-thumb:hover {
  background: var(--primary-hover-color);
}

@media (max-width: 768px) {
  .history-container {
    padding: 1rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  .match-card {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    text-align: center;
  }

  .match-opponent,
  .match-result,
  .match-date {
    padding: 0;
    text-align: center;
  }
}
</style>