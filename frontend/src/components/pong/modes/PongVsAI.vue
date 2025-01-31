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
      />
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

// Player name
const playerName = ref(authStore.user?.username || '')

let animationId = null
let scoreTimeout = null

function startGame() {
  // Reset game state
  gameEngine.value = new GameEngine()
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
    gameEngine.value = new GameEngine()
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
  gameEngine.value.drawGame(ctx, gamePhase.value, playerScore.value, aiScore.value)
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
  gap: 2rem;
  padding: 2rem;
  width: 100%;
  color: var(--text-color);
}

.game-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: var(--text-color);
}
</style>
