<template>
  <div class="pong-mode">
    <h2>Mode VS IA</h2>
    <div class="game-container">
      <canvas
        ref="gameCanvas"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>
      
      <div class="score-board">
        <div class="player">
          <h3>Joueur</h3>
          <p class="score">{{ playerScore }}</p>
          <p class="controls">Contrôles: Z / S</p>
        </div>
        <div class="player">
          <h3>IA</h3>
          <p class="score">{{ aiScore }}</p>
          <p class="controls">Difficulté: {{ difficulty }}</p>
        </div>
      </div>

      <div v-if="!isPlaying" class="game-overlay">
        <div class="start-menu">
          <div class="difficulty-select">
            <h3>Sélectionnez la difficulté</h3>
            <div class="difficulty-buttons">
              <button 
                @click="setDifficulty('Facile')" 
                :class="['difficulty-button', { active: difficulty === 'Facile' }]"
              >
                Facile
              </button>
              <button 
                @click="setDifficulty('Moyen')" 
                :class="['difficulty-button', { active: difficulty === 'Moyen' }]"
              >
                Moyen
              </button>
              <button 
                @click="setDifficulty('Difficile')" 
                :class="['difficulty-button', { active: difficulty === 'Difficile' }]"
              >
                Difficile
              </button>
            </div>
          </div>
          <button @click="startGame" class="start-button">
            Commencer la partie
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../../stores/authStore'

const authStore = useAuthStore()
const gameCanvas = ref(null)
const canvasWidth = 800
const canvasHeight = 400
const playerScore = ref(0)
const aiScore = ref(0)
const isPlaying = ref(false)
const difficulty = ref('Moyen')

const gameState = ref({
  player: {
    y: canvasHeight / 2,
    height: 60,
    width: 10,
    speed: 5,
    upPressed: false,
    downPressed: false
  },
  ai: {
    y: canvasHeight / 2,
    height: 60,
    width: 10,
    speed: 5
  },
  ball: {
    x: canvasWidth / 2,
    y: canvasHeight / 2,
    radius: 5,
    speed: 5,
    dx: 5,
    dy: 0
  }
})

const setDifficulty = (level) => {
  difficulty.value = level
  const state = gameState.value
  switch(level) {
    case 'Facile':
      state.ai.speed = 3
      state.ball.speed = 4
      break
    case 'Moyen':
      state.ai.speed = 5
      state.ball.speed = 5
      break
    case 'Difficile':
      state.ai.speed = 7
      state.ball.speed = 6
      break
  }
}

const handleKeyDown = (e) => {
  const key = e.key.toLowerCase()
  if (key === 'z') gameState.value.player.upPressed = true
  if (key === 's') gameState.value.player.downPressed = true
}

const handleKeyUp = (e) => {
  const key = e.key.toLowerCase()
  if (key === 'z') gameState.value.player.upPressed = false
  if (key === 's') gameState.value.player.downPressed = false
}

const startGame = () => {
  isPlaying.value = true
  resetBall()
  gameLoop()
}

const resetBall = () => {
  const state = gameState.value
  state.ball.x = canvasWidth / 2
  state.ball.y = canvasHeight / 2
  state.ball.dx = state.ball.speed * (Math.random() > 0.5 ? 1 : -1)
  state.ball.dy = state.ball.speed * (Math.random() * 2 - 1)
}

const updateAI = () => {
  const state = gameState.value
  const ballY = state.ball.y
  const aiY = state.ai.y + state.ai.height / 2
  const diffY = ballY - aiY
  
  // Add some prediction based on ball direction
  const predictedY = ballY + state.ball.dy * 
    (state.ball.dx > 0 ? (canvasWidth - state.ball.x) / state.ball.dx : 0)
  
  // Add some randomness based on difficulty
  const randomFactor = difficulty.value === 'Facile' ? 0.3 : 
                      difficulty.value === 'Moyen' ? 0.15 : 0.05
  
  const targetY = predictedY + (Math.random() - 0.5) * canvasHeight * randomFactor
  
  if (Math.abs(targetY - aiY) > state.ai.speed) {
    if (targetY < aiY) {
      state.ai.y -= state.ai.speed
    } else {
      state.ai.y += state.ai.speed
    }
  }
  
  // Keep AI paddle within bounds
  if (state.ai.y < 0) state.ai.y = 0
  if (state.ai.y + state.ai.height > canvasHeight) {
    state.ai.y = canvasHeight - state.ai.height
  }
}

const updateGame = () => {
  const state = gameState.value

  // Update player paddle
  if (state.player.upPressed && state.player.y > 0) {
    state.player.y -= state.player.speed
  }
  if (state.player.downPressed && state.player.y < canvasHeight - state.player.height) {
    state.player.y += state.player.speed
  }

  // Update AI
  updateAI()

  // Update ball
  state.ball.x += state.ball.dx
  state.ball.y += state.ball.dy

  // Ball collision with top and bottom
  if (state.ball.y + state.ball.radius > canvasHeight || state.ball.y - state.ball.radius < 0) {
    state.ball.dy = -state.ball.dy
  }

  // Ball collision with paddles
  if (state.ball.dx < 0) {
    // Player paddle
    if (state.ball.y > state.player.y && 
        state.ball.y < state.player.y + state.player.height &&
        state.ball.x - state.ball.radius < state.player.width) {
      state.ball.dx = -state.ball.dx
    }
  } else {
    // AI paddle
    if (state.ball.y > state.ai.y && 
        state.ball.y < state.ai.y + state.ai.height &&
        state.ball.x + state.ball.radius > canvasWidth - state.ai.width) {
      state.ball.dx = -state.ball.dx
    }
  }

  // Score points
  if (state.ball.x < 0) {
    aiScore.value++
    resetBall()
  } else if (state.ball.x > canvasWidth) {
    playerScore.value++
    resetBall()
  }
}

const drawGame = () => {
  const ctx = gameCanvas.value.getContext('2d')
  
  // Clear canvas
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)
  
  // Draw paddles
  ctx.fillStyle = '#FFFFFF'
  const state = gameState.value
  
  // Player paddle
  ctx.fillRect(0, state.player.y, state.player.width, state.player.height)
  
  // AI paddle
  ctx.fillRect(
    canvasWidth - state.ai.width,
    state.ai.y,
    state.ai.width,
    state.ai.height
  )
  
  // Draw ball
  ctx.beginPath()
  ctx.arc(state.ball.x, state.ball.y, state.ball.radius, 0, Math.PI * 2)
  ctx.fill()
  ctx.closePath()
}

const gameLoop = () => {
  if (!isPlaying.value) return
  
  updateGame()
  drawGame()
  requestAnimationFrame(gameLoop)
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
  isPlaying.value = false
})
</script>

<style scoped>
.pong-mode {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #1a1a1a;
  min-height: 100vh;
  color: white;
}

.game-container {
  position: relative;
  margin-top: 20px;
}

canvas {
  border: 2px solid #4CAF50;
  background: #000;
}

.score-board {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 20px;
}

.player {
  text-align: center;
  padding: 10px;
  background: #2a2a2a;
  border-radius: 8px;
  min-width: 150px;
}

.score {
  font-size: 24px;
  font-weight: bold;
  color: #4CAF50;
}

.controls {
  font-size: 14px;
  opacity: 0.8;
}

.game-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.7);
}

.start-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.difficulty-select {
  text-align: center;
  margin-bottom: 20px;
}

.difficulty-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.difficulty-button {
  padding: 10px 20px;
  background: #2a2a2a;
  border: 2px solid #4CAF50;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.difficulty-button:hover {
  background: #3a3a3a;
}

.difficulty-button.active {
  background: #4CAF50;
}

.start-button {
  padding: 15px 30px;
  font-size: 18px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-button:hover {
  background: #45a049;
  transform: translateY(-2px);
}
</style>
