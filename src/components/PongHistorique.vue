<script setup>
// Props pour passer l'historique des parties comme un tableau
import { useGamesHistoryStore } from '../stores/gamesHistory'

const store = useGamesHistoryStore()

setTimeout(() => {
  store.addMatch({
    id: 1,
    win: true,
    score: '3-2',
    opponent: 'Roger',
    date: '2024-10-20',
  })
}, 5000)
</script>

<template>
  <div class="history-container">
    <h2>{{ $t('history.title') }}</h2>
    <div class="match-list">
      <div
        v-for="match in store.matches"
        :key="match.id"
        class="match-card"
        :class="{
          'win-card': match.win === true,
          'loose-card': match.win === false,
        }"
      >
        <p class="match-result">
          {{ match.win ? $t('history.win') : $t('history.loose') }} :
          {{ match.score }}
        </p>
        <p class="match-opponent">{{ match.opponent }}</p>
        <p class="match-date">{{ match.date }}</p>
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
