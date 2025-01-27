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
    const response = await axios.get(
      `http://localhost:8000/users/histories/user/${authStore.user.id}`,
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

const createTestMatch = async () => {
  try {
    const testMatch = {
      user: authStore.user.id,
      guest_name: 'Bot_' + Math.floor(Math.random() * 1000),
      user_score: Math.floor(Math.random() * 10),
      guest_score: Math.floor(Math.random() * 10),
      played_at: new Date().toISOString(),
      game_name: route.params.game?.toLowerCase() || 'pong',
    }

    await axios.post('http://localhost:8000/users/histories/add', testMatch, {
      withCredentials: true,
    })

    await fetchHistory()
  } catch (err) {
    error.value = 'Erreur lors de la création du match test'
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
      <button @click="createTestMatch" class="test-button">
        {{ t('history.addTest') }}
      </button>
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
          <span class="score-text">: {{ match.user_score }} - {{ match.guest_score }}</span>
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
  padding: 16px;
  background-color: var(--background-color);
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  min-height: 60vh;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.test-button {
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.test-button:hover {
  background-color: var(--primary-color-dark);
}

h2 {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  color: var(--text-color);
}

.loading,
.error,
.no-history {
  text-align: center;
  padding: 20px;
  color: var(--text-color);
}

.error {
  color: #ff4444;
}

.match-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  padding-right: 8px;
}

.match-card {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  background-color: var(--background-color);
  transition: transform 0.2s;
}

.match-card:hover {
  transform: translateX(4px);
}

.win-card {
  background-color: #e6ffed;
  border-color: #33a852;
  color: #33a852;
}

.loose-card {
  background-color: #ffe6e6;
  border-color: #ff4d4d;
  color: #ff4d4d;
}

.draw-card {
  background-color: #f0f0f0;
  border-color: #666666;
  color: #666666;
}

.match-opponent {
  font-size: 14px;
  font-weight: bold;
  padding-right: 16px;
}

.match-result {
  font-size: 16px;
  text-align: center;
}

.match-date {
  font-size: 12px;
  color: var(--text-secondary-color);
  text-align: right;
  white-space: nowrap;
}

.result-text {
  font-weight: bold;
}

.score-text {
  font-weight: normal;
}

/* Style de la scrollbar */
.match-list::-webkit-scrollbar {
  width: 8px;
}

.match-list::-webkit-scrollbar-track {
  background: var(--background-color-light);
  border-radius: 4px;
}

.match-list::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 4px;
}

.match-list::-webkit-scrollbar-thumb:hover {
  background: var(--primary-color-dark);
}
</style>
