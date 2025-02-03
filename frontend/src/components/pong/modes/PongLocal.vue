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
  min-height: 65vh;
  position: relative;
  overflow: hidden;
  background: var(--background-color);
  isolation: isolate; /* Ajout pour créer un nouveau contexte d'empilement */
}

/* Ajout des pseudo-éléments pour le fond */
.local-mode::before {
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

.local-mode::after {
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

/* Titre */
h2 {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 2rem;
  color: var(--primary-color);
  text-shadow: 0 0 15px var(--primary-color);
  animation: float 3s ease-in-out infinite;
}

/* Container du jeu */
.game-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  animation: fadeInUp 0.6s ease backwards;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  border: 2px solid var(--primary-color);
  backdrop-filter: blur(10px);
}

/* Overlay de configuration des joueurs */
.player-setup-overlay {
  background: var(--background-secondary-color);
  padding: 3rem;
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  text-align: center;
  color: var(--text-color);
  animation: fadeIn 0.4s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 25px var(--primary-shadow-color);
}

.player-setup-overlay h3 {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 2rem;
  text-shadow: 0 0 10px var(--primary-color);
}

.player-input {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1.5rem 0;
}

.player-input label {
  font-size: 1.2rem;
  color: var(--text-color);
  font-weight: 600;
}

.name-input {
  padding: 1rem 0rem;
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 1.1rem;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
}

.name-input:focus {
  outline: none;
  box-shadow: 0 0 15px var(--primary-shadow-color);
  transform: translateY(-2px);
}

.start-button {
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: 600;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  margin-top: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.start-button:not(:disabled)::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.start-button:hover:not(:disabled) {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px var(--primary-shadow-color);
}

.start-button:hover:not(:disabled)::before {
  opacity: 1;
}

.start-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--text-secondary-color);
}

/* Animations */
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

/* Media Queries */
@media (max-width: 768px) {
  h2 {
    font-size: 2.5rem;
  }

  .player-setup-overlay {
    padding: 2rem;
  }

  .player-setup-overlay h3 {
    font-size: 1.5rem;
  }

  .start-button {
    padding: 0.8rem 2rem;
    font-size: 1rem;
  }
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
</style>
