<template>
  <div class="ai-mode">
    <h2>{{ t('pong.ai.title') }}</h2>

    <!-- Le jeu -->
    <div class="game-container">
      <GameCanvas
        ref="gameCanvasRef"
        :player1-name="playerName"
        :player2-name="'AI'"
        :player1-score="playerScore"
        :player2-score="aiScore"
        :game-phase="gamePhase"
        :countdown-value="countdownValue"
        :winner="winner"
        @start-game="startGame"
        @close-match="resetGame"
      >
        <template #menu-overlay>
          <div class="player-setup-overlay">
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import GameCanvas from '../common/GameCanvas.vue'
import { GameEngine } from '../common/GameEngine'
import { AIController } from '../common/AIController'

const { t } = useI18n()
const authStore = useAuthStore()

// Game state
const gameCanvasRef = ref(null)
const gameEngine = ref(null)
const aiController = ref(null)
const gamePhase = ref('menu')
const countdownValue = ref(3)
const playerScore = ref(0)
const aiScore = ref(0)
const winner = ref('')
const bonusModeEnabled = ref(false)

// Player name
const playerName = ref(authStore.user?.username || '')

let animationId = null
let scoreTimeout = null

function startGame() {
  // Reset game state
  gameEngine.value = new GameEngine(undefined, undefined, bonusModeEnabled.value)
  aiController.value = new AIController()
  playerScore.value = 0
  aiScore.value = 0
  winner.value = ''

  // Start countdown
  gamePhase.value = 'countdown'
  launchGame()
}

function launchGame() {
  if (!gameEngine.value) {
    gameEngine.value = new GameEngine(undefined, undefined, bonusModeEnabled.value)
    aiController.value = new AIController()
  }

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

  // Mise à jour de l'IA
  if (aiController.value) {
    const aiMoves = aiController.value.update(
      gameEngine.value.getBallState(),
      gameEngine.value.getPlayer2State()
    )
    gameEngine.value.setPlayer2Input(aiMoves.up, aiMoves.down)
  }

  const isGameOver = gameEngine.value.updateGame(
    playerScore.value,
    aiScore.value,
    async (player) => {
      if (player === 'player1') playerScore.value++
      else aiScore.value++

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
    aiScore.value
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
  winner.value = playerScore.value > aiScore.value ? playerName.value : 'AI'

  // Sauvegarder le match dans l'historique
  try {
    const historyData = {
      user: authStore.user.id,
      guest_name: 'AI',
      user_score: playerScore.value,
      guest_score: aiScore.value,
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
  aiScore.value = 0
  winner.value = ''
  gameEngine.value = null
  aiController.value = null
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
.ai-mode {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 65vh;
  position: relative;
  overflow: hidden;
  padding: 2rem;
  background: var(--background-color);
  isolation: isolate; /* Ajout pour créer un nouveau contexte d'empilement */
}

/* Ajout des pseudo-éléments pour le fond */
.ai-mode::before {
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

.ai-mode::after {
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

/* Titre avec animation */
h2 {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 2rem;
  color: var(--primary-color);
  text-shadow: 0 0 15px var(--primary-color);
  animation: float 3s ease-in-out infinite;
  position: relative;
}

/* Container du jeu avec effets */
.game-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  animation: fadeInUp 0.6s ease backwards;
  border-radius: 15px;
  overflow: hidden;
  background: var(--background-secondary-color);
  border: 2px solid var(--primary-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.game-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px var(--primary-shadow-color);
}

/* Start button styles */
.start-button {
  margin-top: 2rem;
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease;
  backdrop-filter: blur(10px);
}

.start-button:hover {
  transform: translateY(-8px);
  background: var(--background-hover-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

/* Animation pour le titre flottant */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Animation d'apparition */
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

/* Effet de brillance */
.game-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    var(--primary-color) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  mix-blend-mode: overlay;
}

.game-container:hover::before {
  opacity: 0.1;
}

/* Style pour le canvas du jeu */
:deep(.game-canvas) {
  border-radius: 12px;
  transition: all 0.3s ease;
}

/* Styles pour les états de jeu */
:deep(.countdown-overlay),
:deep(.game-over-overlay) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--background-secondary-color);
  padding: 2rem;
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  text-align: center;
  color: var(--text-color);
  backdrop-filter: blur(10px);
  box-shadow: 0 0 25px var(--primary-shadow-color);
  animation: fadeIn 0.4s ease;
}

:deep(.countdown-value) {
  font-size: 4rem;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 15px var(--primary-color);
}

:deep(.winner-announcement) {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
  text-shadow: 0 0 10px var(--primary-color);
}

:deep(.game-button) {
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  margin-top: 1rem;
}

:deep(.game-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

/* Score display */
:deep(.score-display) {
  position: absolute;
  top: 2rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 10px var(--primary-shadow-color);
}

/* Media Queries */
@media (max-width: 768px) {
  h2 {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
  }

  .game-container {
    margin: 0 1rem;
  }

  :deep(.countdown-value) {
    font-size: 3rem;
  }

  :deep(.winner-announcement) {
    font-size: 1.5rem;
  }

  :deep(.game-button) {
    padding: 0.8rem 2rem;
    font-size: 1rem;
  }
}

/* Animation de fade in */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}


/* Animation d'apparition */
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

/* Effet de brillance */
.game-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    var(--primary-color) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  mix-blend-mode: overlay;
}

.game-container:hover::before {
  opacity: 0.1;
}

/* Style pour le canvas du jeu */
:deep(.game-canvas) {
  border-radius: 12px;
  transition: all 0.3s ease;
}

/* Styles pour les états de jeu */
:deep(.countdown-overlay),
:deep(.game-over-overlay) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--background-secondary-color);
  padding: 2rem;
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  text-align: center;
  color: var(--text-color);
  backdrop-filter: blur(10px);
  box-shadow: 0 0 25px var(--primary-shadow-color);
  animation: fadeIn 0.4s ease;
}

:deep(.countdown-value) {
  font-size: 4rem;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 15px var(--primary-color);
}

:deep(.winner-announcement) {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
  text-shadow: 0 0 10px var(--primary-color);
}

:deep(.game-button) {
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  margin-top: 1rem;
}

:deep(.game-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

/* Score display */
:deep(.score-display) {
  position: absolute;
  top: 2rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 10px var(--primary-shadow-color);
}

/* Media Queries */
@media (max-width: 768px) {
  h2 {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
  }

  .game-container {
    margin: 0 1rem;
  }

  :deep(.countdown-value) {
    font-size: 3rem;
  }

  :deep(.winner-announcement) {
    font-size: 1.5rem;
  }

  :deep(.game-button) {
    padding: 0.8rem 2rem;
    font-size: 1rem;
  }
}

/* Animation de fade in */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

</style>
