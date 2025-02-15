<template>
  <div class="tournament-mode">
    <div class="controls-center">
      <div v-if="tournamentWinner" class="winner-announcement">
        <h3>{{ tournamentWinner }} {{ t('pong.tournament.wins') }}</h3>
      </div>
      <div v-else-if="gamePhase === 'tournament-tree'" class="next-match-info">
        <h3>{{ t('pong.tournament.nextMatch') }}</h3>
        <p>{{ currentMatch.player1 }} vs {{ currentMatch.player2 }}</p>
      </div>
      <div v-if="gamePhase === 'menu'" class="bonus-option">
        <label>
          <input
            type="checkbox"
            v-model="bonusModeEnabled"
          />
          {{ t('pong.game.enableBonus') }}
        </label>
      </div>
      <button
        v-if="
          gamePhase === 'menu' ||
          (gamePhase === 'tournament-tree' && !tournamentWinner)
        "
        @click="gamePhase === 'menu' ? startTournament() : startNextMatch()"
        :disabled="gamePhase === 'menu' && !canStart"
        class="next-button"
      >
        {{
          gamePhase === 'menu'
            ? t('pong.game.startGame')
            : t('pong.tournament.nextMatch')
        }}
      </button>
    </div>

    <div v-if="gamePhase === 'menu' || gamePhase === 'tournament-tree'">
      <div class="tournament-bracket">
        <div class="match-box" v-for="(player, index) in players" :key="index">
          <input
            v-if="gamePhase === 'menu'"
            v-model="players[index]"
            :placeholder="t('pong.tournament.enterName')"
          />
          <span v-else>{{ getPlayerName(index) }}</span>
        </div>
        <div class="match-box">{{ winners[0] || '?' }}</div>
        <div class="match-box">{{ winners[1] || '?' }}</div>
        <div class="match-box">{{ tournamentWinner || '?' }}</div>
      </div>
    </div>

    <!-- Game zone -->
    <div v-else class="game-container">
      <GameCanvas
        ref="gameCanvasRef"
        :player1-name="currentMatch.player1"
        :player2-name="currentMatch.player2"
        :player1-score="player1Score"
        :player2-score="player2Score"
        :game-phase="canvasPhase"
        :countdown-value="countdownValue"
        :winner="matchWinner"
        @close-match="handleMatchEnd"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import GameCanvas from '../common/GameCanvas.vue'
import { GameEngine } from '../common/GameEngine'

const { t } = useI18n()
const authStore = useAuthStore()

// Tournament state
const gamePhase = ref('menu')
const canvasPhase = ref('ready')
const players = ref([
  authStore.user?.username || '',
  '',
  '',
  '',
])
const winners = ref(['', ''])
const tournamentWinner = ref('')
const currentMatchIndex = ref(0)
const currentMatch = ref({ player1: '', player2: '', round: 'semi' })
const bonusModeEnabled = ref(false)

// Game state
const gameCanvasRef = ref(null)
const gameEngine = ref(null)
const countdownValue = ref(3)
const player1Score = ref(0)
const player2Score = ref(0)
const matchWinner = ref('')
let scoreTimeout = null

let animationId = null

// Check only players 2 to 4
const canStart = computed(() => {
  return players.value.slice(1).every((player) => player.trim() !== '')
})

function getPlayerName(index) {
  return players.value[index] || t('pong.game.player') + ' ' + (index + 1)
}

function startTournament() {
  if (!canStart.value) return
  gamePhase.value = 'tournament-tree'
  setupNextMatch()
}

function setupNextMatch() {
  if (currentMatchIndex.value < 2) {
    // Semifinals
    const matchIndex = currentMatchIndex.value
    currentMatch.value = {
      player1: getPlayerName(matchIndex * 2),
      player2: getPlayerName(matchIndex * 2 + 1),
      round: 'semi',
    }
  } else if (currentMatchIndex.value === 2) {
    // Final
    currentMatch.value = {
      player1: winners.value[0],
      player2: winners.value[1],
      round: 'final',
    }
  }
}

function startNextMatch() {
  gamePhase.value = 'playing'
  canvasPhase.value = 'ready'
  player1Score.value = 0
  player2Score.value = 0
  matchWinner.value = ''

  nextTick(() => {
    const canvas = gameCanvasRef.value?.canvas
    if (canvas) {
      gameEngine.value = new GameEngine(canvas.width, canvas.height, bonusModeEnabled.value)
      // Force a first frame to ensure everything is initialized
      const ctx = canvas.getContext('2d')
      gameEngine.value.drawGame(ctx)
      // Launch the game automatically
      launchGame()
    }
  })
}

function launchGame() {
  if (!gameEngine.value) return

  countdownValue.value = 3
  canvasPhase.value = 'countdown'

  const interval = setInterval(() => {
    countdownValue.value--
    if (countdownValue.value <= 0) {
      clearInterval(interval)
      canvasPhase.value = 'playing'
      gameEngine.value.launchBall()
      nextTick(() => {
        if (gameEngine.value) {
          gameLoop()
        }
      })
    }
  }, 1000)
}

function gameLoop() {
  if (!gameEngine.value || canvasPhase.value !== 'playing') return

  const canvas = gameCanvasRef.value?.canvas
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const isGameOver = gameEngine.value.updateGame(
    player1Score.value,
    player2Score.value,
    (player) => {
      if (player === 'player1') player1Score.value++
      else player2Score.value++

      // Pause for 1 second to show the score
      canvasPhase.value = 'score'
      if (scoreTimeout) clearTimeout(scoreTimeout)

      scoreTimeout = setTimeout(() => {
        if (!isGameOver && gameEngine.value) {
          canvasPhase.value = 'playing'
          gameEngine.value.launchBall()
          gameLoop()
        }
      }, 1000)
    }
  )

  if (isGameOver) {
    endMatch()
    return
  }

  gameEngine.value.drawGame(
    ctx,
    canvasPhase.value,
    player1Score.value,
    player2Score.value
  )

  if (canvasPhase.value === 'playing') {
    animationId = requestAnimationFrame(gameLoop)
  }
}

function endMatch() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }

  if (scoreTimeout) {
    clearTimeout(scoreTimeout)
    scoreTimeout = null
  }

  canvasPhase.value = 'over'
  const winner =
    player1Score.value > player2Score.value
      ? currentMatch.value.player1
      : currentMatch.value.player2
  matchWinner.value = winner

  // Update the tournament
  if (currentMatchIndex.value < 2) {
    winners.value[currentMatchIndex.value] = winner
  } else {
    tournamentWinner.value = winner
  }
}

function handleMatchEnd() {
  currentMatchIndex.value++

  // Reset scores
  player1Score.value = 0
  player2Score.value = 0
  matchWinner.value = ''

  if (currentMatchIndex.value < 3) {
    gamePhase.value = 'tournament-tree'
    canvasPhase.value = 'menu'
    setupNextMatch()
  } else {
    gamePhase.value = 'tournament-tree'
  }
}

function handleKeyDown(e) {
  if (gameEngine.value && canvasPhase.value === 'playing') {
    gameEngine.value.handleKeyDown(e)
  }
}

function handleKeyUp(e) {
  if (gameEngine.value && canvasPhase.value === 'playing') {
    gameEngine.value.handleKeyUp(e)
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.tournament-mode {
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
  padding: 2rem;
  position: relative;
  min-height: 80vh;
  background: var(--background-color);
  animation: fadeIn 0.6s ease;
  isolation: isolate;
}

.tournament-mode::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100vw;
  height: 100%;
  background: radial-gradient(
    circle at top right,
    var(--primary-shadow-color) 0%,
    transparent 70%
  );
  opacity: 0.15;
  z-index: -2;
  pointer-events: none;
}

.tournament-mode::after {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100vw;
  height: 100%;
  background: linear-gradient(
    135deg,
    var(--primary-color) 0%,
    transparent 100%
  );
  opacity: 0.05;
  backdrop-filter: blur(100px);
  z-index: -1;
  pointer-events: none;
}

.controls-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.winner-announcement {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--primary-color);
  text-shadow: 0 0 15px var(--primary-color);
  animation: float 3s ease-in-out infinite;
  text-align: center;
}

.next-match-info {
  text-align: center;
  animation: fadeInUp 0.6s ease;
}

.next-match-info h3 {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
  text-shadow: 0 0 10px var(--primary-color);
}

.next-match-info p {
  font-size: 1.5rem;
  color: var(--text-color);
}

.tournament-bracket {
  display: grid;
  grid-template-columns: repeat(5, auto);
  grid-template-rows: repeat(7, 1fr);
  gap: 1rem;
  padding: 2rem;
  margin: 0 auto;
}

.match-box {
  width: 200px;
  height: 40px;
  border: 2px solid var(--primary-color);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--background-color);
  color: var(--text-color);
  position: relative;
  animation: fadeInUp 0.6s ease;
}

.match-box:nth-child(1) {
  grid-area: 1 / 1 / 2 / 2;
}
.match-box:nth-child(2) {
  grid-area: 3 / 1 / 4 / 2;
}
.match-box:nth-child(3) {
  grid-area: 5 / 1 / 6 / 2;
}
.match-box:nth-child(4) {
  grid-area: 7 / 1 / 8 / 2;
}

.match-box:nth-child(5) {
  grid-area: 2 / 3 / 3 / 4;
}
.match-box:nth-child(6) {
  grid-area: 6 / 3 / 7 / 4;
}

.match-box:nth-child(7) {
  grid-area: 4 / 5 / 5 / 6;
}

.match-box:nth-child(1)::after,
.match-box:nth-child(2)::after,
.match-box:nth-child(3)::after,
.match-box:nth-child(4)::after,
.match-box:nth-child(5)::after,
.match-box:nth-child(6)::after {
  content: '';
  position: absolute;
  left: 100%;
  top: 50%;
  width: 2rem;
  height: 2px;
  background: var(--primary-color);
  transform: translateY(-50%);
}

.match-box input {
  width: 100%;
  height: 100%;
  background: transparent;
  border: none;
  text-align: center;
  color: var(--text-color);
  padding: 0 1rem;
}

.match-box input:focus {
  outline: none;
}

.next-button {
  margin-top: 2rem;
  padding: 0.75rem 2rem;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
  animation: fadeInUp 0.6s ease;
}

.next-button:hover:not(:disabled) {
  transform: translateY(-8px) scale(1.02);
  background: var(--background-hover-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

.bonus-option {
  display: flex;
  align-items: center;
  margin-top: 1rem;
  animation: fadeInUp 0.6s ease;
}

.bonus-option input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-right: 0.5rem;
  cursor: pointer;
}

.bonus-option label {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color);
  cursor: pointer;
}

.next-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.game-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
