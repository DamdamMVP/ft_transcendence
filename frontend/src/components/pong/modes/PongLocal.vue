<template>
  <div class="local-mode">
    <h2>{{ t('pong.local.title') }}</h2>

    <!-- Phase de saisie des noms -->
    <div v-if="gamePhase === 'menu'" class="player-setup">
      <div class="player-names">
        <div class="player-entry">
          <label>{{ t('pong.game.player') }} 2:</label>
          <input v-model="player2Name" :placeholder="t('pong.game.enterName')" />
        </div>
      </div>
      <button
        @click="startGame"
        :disabled="!canStart"
        class="button"
      >
        {{ t('pong.game.startGame') }}
      </button>
    </div>

    <!-- Le jeu -->
    <div v-else class="game-container">
      <GameCanvas
        ref="gameCanvasRef"
        :player1-name="player1Name"
        :player2-name="player2Name"
        :player1-score="player1Score"
        :player2-score="player2Score"
        :game-phase="gamePhase"
        :countdown-value="countdownValue"
        :winner="winner"
        @start-game="launchGame"
        @close-match="resetGame"
      />
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
const player1Score = ref(0)
const player2Score = ref(0)
const winner = ref('')

// Player names
const player1Name = ref(authStore.user?.username || '')
const player2Name = ref('')

const canStart = computed(() => {
  return player2Name.value.trim() !== ''
})

let animationId = null

function startGame() {
  if (!canStart.value) return
  
  gameEngine.value = new GameEngine()
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
  if (gamePhase.value !== 'playing') return

  const isGameOver = gameEngine.value.updateGame(
    player1Score.value,
    player2Score.value,
    (player) => {
      if (player === 'player1') player1Score.value++
      else player2Score.value++
    }
  )

  if (isGameOver) {
    endGame()
    return
  }

  const canvas = gameCanvasRef.value?.canvas
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  gameEngine.value.drawGame(ctx)
  animationId = requestAnimationFrame(gameLoop)
}

async function endGame() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  gamePhase.value = 'over'
  
  const winnerName = player1Score.value > player2Score.value ? player1Name.value : player2Name.value
  winner.value = winnerName

  // Sauvegarder le match dans l'historique
  try {
    const historyData = {
      user: authStore.user.id,
      guest_name: player2Name.value,
      user_score: player1Score.value,
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
  gamePhase.value = 'menu'
  player1Score.value = 0
  player2Score.value = 0
  winner.value = ''
  player2Name.value = ''
  gameEngine.value = null
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
})
</script>

<style scoped>
.local-mode {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  width: 100%;
}

.player-setup {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 600px;
}

.player-names {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.player-entry {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.player-entry input {
  padding: 0.5rem;
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  background: var(--background-color);
  color: var(--text-color);
}

.button {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.button:hover {
  background: var(--primary-hover-color);
}

.button:disabled {
  background: var(--disabled-color);
  cursor: not-allowed;
}

.game-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}
</style>
