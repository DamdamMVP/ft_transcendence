<template>
  <div class="local-mode">
    <h2>{{ t('pong.local.title') }}</h2>

    <!-- Le jeu -->
    <div class="game-container">
      <GameCanvas
        ref="gameCanvasRef"
        :player1-name="playerName"
        :player2-name="player2Name"
        :player1-score="playerScore"
        :player2-score="player2Score"
        :game-phase="gamePhase"
        :countdown-value="countdownValue"
        :winner="winner"
        @start-game="startGame"
        @close-match="resetGame"
      >
        <!-- Overlay personnalisé pour la saisie du pseudo -->
        <template #menu-overlay>
          <div class="player-setup-overlay">
            <h3>{{ t('pong.game.enterName') }}</h3>
            <div class="player-input">
              <label>{{ t('pong.game.player2') }}:</label>
              <input
                v-model="player2Name"
                :placeholder="t('pong.game.enterName')"
                class="name-input"
              />
            </div>
            <div class="bonus-option">
              <label>
                <input
                  type="checkbox"
                  v-model="bonusModeEnabled"
                />
                {{ t('pong.game.enableBonus') }}
              </label>
            </div>
            <button
              @click="startGame"
              :disabled="!canStart"
              class="start-button"
            >
              {{ t('pong.game.startGame') }}
            </button>
          </div>
        </template>
      </GameCanvas>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import GameCanvas from '../common/GameCanvas.vue'
import { GameEngine } from '../common/GameEngine'

const { t } = useI18n()
const authStore = useAuthStore()

// Game state
const gameCanvasRef = ref(null)
const gameEngine = ref(null)
const gamePhase = ref('menu')
const countdownValue = ref(3)
const playerScore = ref(0)
const player2Score = ref(0)
const winner = ref('')
const bonusModeEnabled = ref(false)

// Player names
const playerName = ref(authStore.user?.username || '')
const player2Name = ref('')

const canStart = computed(() => {
  return player2Name.value.trim() !== ''
})

let animationId = null
let scoreTimeout = null

function startGame() {
  if (!canStart.value) return

  gameEngine.value = new GameEngine(undefined, undefined, bonusModeEnabled.value)
  gamePhase.value = 'countdown'
  launchGame()
}

function launchGame() {
  countdownValue.value = 3
  gamePhase.value = 'countdown'

  const interval = setInterval(() => {
    countdownValue.value--
    if (countdownValue.value <= 0) {
      clearInterval(interval)
      gamePhase.value = 'playing'
      gameEngine.value.launchBall()
      nextTick(() => {
        gameLoop()
      })
    }
  }, 1000)
}

function gameLoop() {
  if (gamePhase.value !== 'playing' || !gameEngine.value) return

  const isGameOver = gameEngine.value.updateGame(
    playerScore.value,
    player2Score.value,
    async (player) => {
      if (player === 'player1') playerScore.value++
      else player2Score.value++

      // Pause pendant 1 seconde pour montrer le score
      gamePhase.value = 'score'
      if (scoreTimeout) clearTimeout(scoreTimeout)

      scoreTimeout = setTimeout(() => {
        if (!isGameOver && gameEngine.value) {
          gamePhase.value = 'playing'
          gameEngine.value.resetBall()
          gameEngine.value.launchBall()
          animationId = requestAnimationFrame(gameLoop)
        }
      }, 1000)
    }
  )

  if (isGameOver) {
    endGame()
    return
  }

  const canvas = gameCanvasRef.value?.canvas
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  gameEngine.value.drawGame(
    ctx,
    gamePhase.value,
    playerScore.value,
    player2Score.value
  )
  if (gamePhase.value === 'playing') {
    animationId = requestAnimationFrame(gameLoop)
  }
}

async function endGame() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  if (scoreTimeout) {
    clearTimeout(scoreTimeout)
    scoreTimeout = null
  }

  gamePhase.value = 'over'
  winner.value =
    playerScore.value > player2Score.value
      ? playerName.value
      : player2Name.value

  // Sauvegarder le match dans l'historique
  try {
    const historyData = {
      user: authStore.user.id,
      guest_name: player2Name.value,
      user_score: playerScore.value,
      guest_score: player2Score.value,
      played_at: new Date().toISOString(),
      game_name: 'pong',
    }

    await axios.post('/users/histories/add', historyData, {
      withCredentials: true,
    })
    console.log('history saved')
  } catch (error) {
    console.error('Error saving game history:', error)
  }
}

function resetGame() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  if (scoreTimeout) {
    clearTimeout(scoreTimeout)
    scoreTimeout = null
  }

  gamePhase.value = 'menu'
  playerScore.value = 0
  player2Score.value = 0
  winner.value = ''
  gameEngine.value = null
  player2Name.value = ''
}

function handleKeyDown(e) {
  if (gameEngine.value && gamePhase.value === 'playing') {
    gameEngine.value.handleKeyDown(e)
  }
}

function handleKeyUp(e) {
  if (gameEngine.value && gamePhase.value === 'playing') {
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
  if (scoreTimeout) {
    clearTimeout(scoreTimeout)
  }
})
</script>

<style scoped>
.local-mode {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  color: var(--text-color);
}

.game-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.player-setup-overlay {
  background: var(--background-color);
  padding: 2rem;
  border-radius: 8px;
  border: 2px solid var(--primary-color);
  text-align: center;
  color: var(--text-color);
}

.player-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 1rem 0;
}

.name-input {
  padding: 0.5rem;
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  background: var(--background-color);
  color: var(--text-color);
}

.start-button {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.start-button:hover:not(:disabled) {
  background: var(--primary-hover-color);
}

.start-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bonus-option {
  margin: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bonus-option label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.bonus-option input[type="checkbox"] {
  width: 1.2rem;
  height: 1.2rem;
  cursor: pointer;
}
</style>
