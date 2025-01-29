<template>
  <div class="pong-mode">
    <h2>Mode Local 1v1</h2>
    <div class="game-container">
      <canvas
        ref="gameCanvas"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousemove="handleMouseMove"
      ></canvas>
      
      <div class="score-board">
        <div class="player">
          <h3>Joueur 1</h3>
          <p class="score">{{ player1Score }}</p>
          <p class="controls">Contrôles: Z / S</p>
        </div>
        <div class="player">
          <h3>Joueur 2</h3>
          <p class="score">{{ player2Score }}</p>
          <p class="controls">Contrôles: ↑ / ↓</p>
        </div>
      </div>

      <div v-if="!isPlaying" class="game-overlay">
        <button @click="startGame" class="start-button">
          Commencer la partie
        </button>
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
const player1Score = ref(0)
const player2Score = ref(0)
const isPlaying = ref(false)

const gameState = ref({
  player1: {
    y: canvasHeight / 2,
    height: 60,
    width: 10,
    speed: 5,
    score: 0,
    upPressed: false,
    downPressed: false
  },
  player2: {
    y: canvasHeight / 2,
    height: 60,
    width: 10,
    speed: 5,
    score: 0,
    upPressed: false,
    downPressed: false
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

const handleKeyDown = (e) => {
  const key = e.key.toLowerCase()
  if (key === 'z') gameState.value.player1.upPressed = true
  if (key === 's') gameState.value.player1.downPressed = true
  if (key === 'arrowup') gameState.value.player2.upPressed = true
  if (key === 'arrowdown') gameState.value.player2.downPressed = true
}

const handleKeyUp = (e) => {
  const key = e.key.toLowerCase()
  if (key === 'z') gameState.value.player1.upPressed = false
  if (key === 's') gameState.value.player1.downPressed = false
  if (key === 'arrowup') gameState.value.player2.upPressed = false
  if (key === 'arrowdown') gameState.value.player2.downPressed = false
}

const handleMouseMove = (e) => {
  // Optional: Implement mouse control if needed
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

const updateGame = () => {
  const state = gameState.value

  // Update paddles
  if (state.player1.upPressed && state.player1.y > 0) {
    state.player1.y -= state.player1.speed
  }
  if (state.player1.downPressed && state.player1.y < canvasHeight - state.player1.height) {
    state.player1.y += state.player1.speed
  }
  if (state.player2.upPressed && state.player2.y > 0) {
    state.player2.y -= state.player2.speed
  }
  if (state.player2.downPressed && state.player2.y < canvasHeight - state.player2.height) {
    state.player2.y += state.player2.speed
  }

  // Update ball
  state.ball.x += state.ball.dx
  state.ball.y += state.ball.dy

  // Ball collision with top and bottom
  if (state.ball.y + state.ball.radius > canvasHeight || state.ball.y - state.ball.radius < 0) {
    state.ball.dy = -state.ball.dy
  }

  // Ball collision with paddles
  if (state.ball.dx < 0) {
    // Player 1 paddle
    if (state.ball.y > state.player1.y && 
        state.ball.y < state.player1.y + state.player1.height &&
        state.ball.x - state.ball.radius < state.player1.width) {
      state.ball.dx = -state.ball.dx
    }
  } else {
    // Player 2 paddle
    if (state.ball.y > state.player2.y && 
        state.ball.y < state.player2.y + state.player2.height &&
        state.ball.x + state.ball.radius > canvasWidth - state.player2.width) {
      state.ball.dx = -state.ball.dx
    }
  }

  // Score points
  if (state.ball.x < 0) {
    state.player2.score++
    player2Score.value = state.player2.score
    resetBall()
  } else if (state.ball.x > canvasWidth) {
    state.player1.score++
    player1Score.value = state.player1.score
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
  
  // Player 1 paddle
  ctx.fillRect(0, state.player1.y, state.player1.width, state.player1.height)
  
  // Player 2 paddle
  ctx.fillRect(
    canvasWidth - state.player2.width,
    state.player2.y,
    state.player2.width,
    state.player2.height
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
