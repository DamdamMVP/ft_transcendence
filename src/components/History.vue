<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { useGamesHistoryStore } from '../stores/gamesHistory'

const store = useGamesHistoryStore()
const route = useRoute() // Récupérer les paramètres de la route

// Filtrer les matchs en fonction du jeu sélectionné
const filteredMatches = computed(() =>
  store.matches
    .filter(
      (match) => match.game.toLowerCase() === route.params.game?.toLowerCase()
    )
    .sort((a, b) => b.date - a.date)
)

// Ajouter un match pour tester
setTimeout(() => {
  store.addMatch({
    id: 4,
    game: 'Pong',
    win: true,
    score: '3-1',
    opponent: 'Roger',
    date: Date.now(),
  })
}, 1000)

setTimeout(() => {
  store.addMatch({
    id: 5,
    game: 'Tic-Tac-Toe',
    win: true,
    score: '3-0',
    opponent: 'Albert',
    date: Date.now(),
  })
}, 1000)
</script>

<template>
  <div class="history-container">
    <h2>{{ $t('history.title') }}</h2>
    <div class="match-list">
      <div
        v-for="match in filteredMatches"
        :key="match.id"
        class="match-card"
        :class="{
          'win-card': match.win,
          'loose-card': !match.win,
        }"
      >
        <p class="match-result">
          {{ match.win ? $t('history.win') : $t('history.loose') }} :
          {{ match.score }}
        </p>
        <p class="match-opponent">{{ match.opponent }}</p>
        <p class="match-date">
          {{ new Date(match.date).toLocaleDateString() }}
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
}

h2 {
  margin-bottom: 16px;
  font-size: 20px;
  font-weight: bold;
  color: var(--text-color);
}

.match-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  overflow-y: scroll;
  max-height: 60vh;
}

.match-card {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  text-align: center;
  background-color: var(--background-color);
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

.match-result {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.match-opponent {
  font-size: 14px;
  color: #333;
}

.match-date {
  font-size: 14px;
  color: #333;
}

.match-stats {
  font-size: 12px;
  color: #333;
}
</style>
