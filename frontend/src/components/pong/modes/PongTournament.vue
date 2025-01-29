<template>
  <div class="tournament-mode">
    <h2>Mode Tournoi</h2>
    
    <div v-if="!currentMatch" class="tournament-bracket">
      <div class="players-setup" v-if="!tournamentStarted">
        <h3>Configuration des joueurs</h3>
        <div class="players-list">
          <div v-for="(player, index) in players" :key="index" class="player-input">
            <input 
              v-model="players[index]" 
              :placeholder="'Joueur ' + (index + 1)"
              type="text"
            >
          </div>
        </div>
        <button 
          @click="startTournament" 
          :disabled="!allPlayersReady"
          class="start-button"
        >
          Commencer le tournoi
        </button>
      </div>

      <div v-else class="bracket-display">
        <div class="semi-finals">
          <div class="match" @click="startMatch(0, 1)">
            <div class="player">{{ players[0] }}</div>
            <div class="vs">VS</div>
            <div class="player">{{ players[1] }}</div>
          </div>
          <div class="match" @click="startMatch(2, 3)">
            <div class="player">{{ players[2] }}</div>
            <div class="vs">VS</div>
            <div class="player">{{ players[3] }}</div>
          </div>
        </div>

        <div class="finals" v-if="finalists.length === 2">
          <div class="match final-match" @click="startFinalMatch">
            <div class="player">{{ finalists[0] }}</div>
            <div class="vs">VS</div>
            <div class="player">{{ finalists[1] }}</div>
          </div>
        </div>

        <div v-if="winner" class="winner-display">
          <h3>🏆 Vainqueur du tournoi 🏆</h3>
          <div class="winner-name">{{ winner }}</div>
        </div>
      </div>
    </div>

    <div v-else class="game-container">
      <canvas
        ref="gameCanvas"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>
      
      <div class="match-info">
        <div class="player-info">
          <h3>{{ currentMatch.player1 }}</h3>
          <p class="score">{{ player1Score }}</p>
        </div>
        <div class="player-info">
          <h3>{{ currentMatch.player2 }}</h3>
          <p class="score">{{ player2Score }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../../../stores/authStore'

const authStore = useAuthStore()
const gameCanvas = ref(null)
const canvasWidth = 800
const canvasHeight = 400

const players = ref(['', '', '', ''])
const tournamentStarted = ref(false)
const currentMatch = ref(null)
const finalists = ref([])
const winner = ref(null)
const player1Score = ref(0)
const player2Score = ref(0)

const allPlayersReady = computed(() => {
  return players.value.every(player => player.trim() !== '')
})

const startTournament = () => {
  tournamentStarted.value = true
}

const startMatch = (player1Index, player2Index) => {
  currentMatch.value = {
    player1: players.value[player1Index],
    player2: players.value[player2Index],
    player1Index,
    player2Index,
    isFinal: false
  }
}

const startFinalMatch = () => {
  currentMatch.value = {
    player1: finalists.value[0],
    player2: finalists.value[1],
    isFinal: true
  }
}

const endMatch = (winnerName) => {
  if (currentMatch.value.isFinal) {
    winner.value = winnerName
  } else {
    finalists.value.push(winnerName)
  }
  currentMatch.value = null
}
</script>

<style scoped>
.tournament-mode {
  padding: 20px;
  background: #1a1a1a;
  min-height: 100vh;
  color: white;
}

h2 {
  text-align: center;
  color: #4CAF50;
  margin-bottom: 30px;
}

.players-setup {
  max-width: 600px;
  margin: 0 auto;
}

.players-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.player-input input {
  width: 100%;
  padding: 10px;
  background: #2a2a2a;
  border: 2px solid #4CAF50;
  border-radius: 5px;
  color: white;
}

.start-button {
  width: 100%;
  padding: 15px;
  background: #4CAF50;
  border: none;
  border-radius: 5px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-button:hover:not(:disabled) {
  background: #45a049;
  transform: translateY(-2px);
}

.start-button:disabled {
  background: #666;
  cursor: not-allowed;
}

.bracket-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.semi-finals {
  display: flex;
  gap: 60px;
}

.match {
  background: #2a2a2a;
  border: 2px solid #4CAF50;
  border-radius: 10px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}

.match:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
}

.final-match {
  border-color: #ffd700;
}

.vs {
  text-align: center;
  color: #4CAF50;
  margin: 10px 0;
  font-weight: bold;
}

.player {
  text-align: center;
  padding: 5px;
}

.winner-display {
  text-align: center;
  margin-top: 30px;
}

.winner-name {
  font-size: 24px;
  color: #ffd700;
  margin-top: 10px;
}

.game-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

canvas {
  border: 2px solid #4CAF50;
  background: #000;
  margin-bottom: 20px;
}

.match-info {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 800px;
}

.player-info {
  text-align: center;
  background: #2a2a2a;
  padding: 10px 20px;
  border-radius: 5px;
  min-width: 150px;
}

.score {
  font-size: 24px;
  color: #4CAF50;
  margin: 5px 0;
}
</style>
