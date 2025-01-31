<template>
  <div class="local-mode">
    <h2>{{ t('pong.local.title') }}</h2>

    <!-- Phase de saisie des noms -->
    <div v-if="gamePhase === 'menu'" class="player-setup">
      <div class="player-names">
        <div class="player-entry">
          <label>{{ t('pong.game.player') }} 1:</label>
          <input v-model="player1Name" :placeholder="t('pong.game.enterName')" />
        </div>
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
import GameCanvas from '../common/GameCanvas.vue'
import { GameEngine } from '../common/GameEngine'

// Game state
const gameCanvasRef = ref(null)
const gameEngine = ref(null)
const gamePhase = ref('menu')
const countdownValue = ref(3)
const player1Score = ref(0)
const player2Score = ref(0)
const winner = ref('')

// Player names
const player1Name = ref('')
const player2Name = ref('')

const canStart = computed(() => {
  return player1Name.value.trim() && player2Name.value.trim()
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

function endGame() {
  cancelAnimationFrame(animationId)
  if (player1Score.value >= gameEngine.value.WINNING_SCORE) {
    winner.value = player1Name.value
  } else {
    winner.value = player2Name.value
  }
  gamePhase.value = 'over'
}

function resetGame() {
  player1Score.value = 0
  player2Score.value = 0
  winner.value = ''
  gamePhase.value = 'menu'
  gameEngine.value = null
}

// Event listeners
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
  cancelAnimationFrame(animationId)
})

const { t } = useI18n()
</script>

<style scoped>
.local-mode {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.player-setup {
  margin: 20px 0;
}

.player-names {
  margin: 20px 0;
}

.player-entry {
  margin: 10px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.player-entry label {
  width: 80px;
}

.player-entry input {
  padding: 8px;
  width: 200px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.button {
  padding: 10px 20px;
  font-size: 16px;
  background: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.game-container {
  margin-top: 20px;
}
</style>
