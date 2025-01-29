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
          <p class="controls">Contrôles: F / S</p>
        </div>
        <div class="player">
          <h3>IA</h3>
          <p class="score">{{ aiScore }}</p>
        </div>
      </div>

      <div v-if="!isPlaying" class="game-overlay">
        <div class="start-menu">
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
import { useTheme } from '../../../composables/useTheme'

const { currentTheme } = useTheme()
const gameCanvas = ref(null)
const canvasWidth = 800
const canvasHeight = 400
const playerScore = ref(0)
const aiScore = ref(0)
const isPlaying = ref(false)

const WINNING_SCORE = 5
const SPEED_INCREASE = 0.2
const INITIAL_BALL_SPEED = 5
const BALL_SPEED_INCREASE = 1.1 // 10% plus rapide à chaque rebond
const MAX_BALL_SPEED = 10 // Vitesse maximale de la balle

const gameState = ref({
  player: {
    x: 20,
    y: canvasHeight / 2 - 40,
    width: 10,
    height: 80,
    speed: 6,
    upPressed: false,
    downPressed: false,
  },
  ai: {
    x: canvasWidth - 30,
    y: canvasHeight / 2 - 40,
    width: 10,
    height: 80,
    baseSpeed: 2,
    targetY: canvasHeight / 2,
    upPressed: false,
    downPressed: false,
    lastUpdateTime: 0,
    updateInterval: 1000, // 1 seconde entre chaque mise à jour
    predictedBallY: canvasHeight / 2,
  },
  ball: {
    x: canvasWidth / 2,
    y: canvasHeight / 2,
    radius: 8,
    speedX: INITIAL_BALL_SPEED,
    speedY: INITIAL_BALL_SPEED,
  },
})

const paddleBounce = (who) => {
  const state = gameState.value

  // Augmente la vitesse de la balle
  let currentSpeed = Math.sqrt(
    state.ball.speedX * state.ball.speedX +
      state.ball.speedY * state.ball.speedY
  )

  // Applique l'augmentation de vitesse avec une limite
  currentSpeed = Math.min(currentSpeed * BALL_SPEED_INCREASE, MAX_BALL_SPEED)

  let paddle
  if (who === 'player') {
    paddle = state.player
  } else {
    paddle = state.ai
  }

  const paddleCenter = paddle.y + paddle.height / 2
  const distFromCenter = (state.ball.y - paddleCenter) / (paddle.height / 2)
  const maxBounceAngle = 60 * (Math.PI / 180)
  const bounceAngle = distFromCenter * maxBounceAngle

  if (who === 'player') {
    state.ball.speedX = Math.abs(currentSpeed * Math.cos(bounceAngle))
    state.ball.speedY = currentSpeed * Math.sin(bounceAngle)
  } else {
    state.ball.speedX = -Math.abs(currentSpeed * Math.cos(bounceAngle))
    state.ball.speedY = currentSpeed * Math.sin(bounceAngle)
  }
}

const predictBallPosition = () => {
  const state = gameState.value
  
  // Si la balle s'éloigne de l'IA, rester au centre
  if (state.ball.speedX <= 0) {
    return canvasHeight / 2
  }
  
  let futureX = state.ball.x
  let futureY = state.ball.y
  let speedX = state.ball.speedX
  let speedY = state.ball.speedY
  
  // Prédire la trajectoire jusqu'à la raquette de l'IA
  while (futureX < state.ai.x) {
    futureX += speedX
    futureY += speedY
    
    // Rebonds sur les murs
    if (futureY < 0 || futureY > canvasHeight) {
      speedY = -speedY
    }
  }
  
  return futureY
}

const updateAI = () => {
  const state = gameState.value
  const currentTime = Date.now()
  
  // Ne mettre à jour que toutes les secondes
  if (currentTime - state.ai.lastUpdateTime >= state.ai.updateInterval) {
    state.ai.lastUpdateTime = currentTime
    
    // Prédire où la balle va arriver
    state.ai.predictedBallY = predictBallPosition()
    
    // Simuler des entrées clavier basées sur la prédiction
    const paddleCenter = state.ai.y + state.ai.height / 2
    const moveThreshold = 20 // Zone de tolérance
    
    if (paddleCenter < state.ai.predictedBallY - moveThreshold) {
      state.ai.upPressed = false
      state.ai.downPressed = true
    } else if (paddleCenter > state.ai.predictedBallY + moveThreshold) {
      state.ai.upPressed = true
      state.ai.downPressed = false
    } else {
      state.ai.upPressed = false
      state.ai.downPressed = false
    }
  }
}

const updateGame = () => {
  const state = gameState.value

  if (playerScore.value >= WINNING_SCORE || aiScore.value >= WINNING_SCORE) {
    isPlaying.value = false
    return
  }

  // Update player
  if (state.player.upPressed && state.player.y > 0) {
    state.player.y -= state.player.speed
  }
  if (
    state.player.downPressed &&
    state.player.y + state.player.height < canvasHeight
  ) {
    state.player.y += state.player.speed
  }

  // Update AI
  updateAI()
  
  // Appliquer les mouvements de l'IA basés sur les touches simulées
  const aiCurrentSpeed = state.ai.baseSpeed * (1 + playerScore.value * SPEED_INCREASE)
  
  if (state.ai.upPressed && state.ai.y > 0) {
    state.ai.y -= aiCurrentSpeed
  }
  if (state.ai.downPressed && state.ai.y + state.ai.height < canvasHeight) {
    state.ai.y += aiCurrentSpeed
  }

  // Calculer la prochaine position de la balle
  const nextX = state.ball.x + state.ball.speedX
  const nextY = state.ball.y + state.ball.speedY

  // Vérifier les collisions avec les raquettes avant de déplacer la balle
  let collision = false

  // Collision avec la raquette du joueur
  if (
    nextX - state.ball.radius <= state.player.x + state.player.width &&
    nextX - state.ball.radius >= state.player.x &&
    state.ball.y >= state.player.y &&
    state.ball.y <= state.player.y + state.player.height &&
    state.ball.speedX < 0
  ) {
    paddleBounce('player')
    collision = true
  }

  // Collision avec la raquette de l'IA
  if (
    nextX + state.ball.radius >= state.ai.x &&
    nextX + state.ball.radius <= state.ai.x + state.ai.width &&
    state.ball.y >= state.ai.y &&
    state.ball.y <= state.ai.y + state.ai.height &&
    state.ball.speedX > 0
  ) {
    paddleBounce('ai')
    collision = true
  }

  // Si pas de collision, mettre à jour la position de la balle
  if (!collision) {
    state.ball.x = nextX
    state.ball.y = nextY

    // Collision avec les murs
    if (
      state.ball.y - state.ball.radius < 0 ||
      state.ball.y + state.ball.radius > canvasHeight
    ) {
      state.ball.speedY = -state.ball.speedY
    }

    // Score points
    if (state.ball.x - state.ball.radius < 0) {
      aiScore.value++
      if (aiScore.value < WINNING_SCORE) {
        resetBall()
      }
    } else if (state.ball.x + state.ball.radius > canvasWidth) {
      playerScore.value++
      if (playerScore.value < WINNING_SCORE) {
        resetBall()
      }
    }
  }
}

const drawGame = () => {
  const ctx = gameCanvas.value.getContext('2d')
  const state = gameState.value

  // Clear canvas
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--background-color'
  )
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  // Draw border
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--primary-color'
  )
  ctx.lineWidth = 2
  ctx.strokeRect(0, 0, canvasWidth, canvasHeight)

  // Draw paddles
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--primary-color'
  )

  // Player paddle
  ctx.fillRect(
    state.player.x,
    state.player.y,
    state.player.width,
    state.player.height
  )

  // AI paddle
  ctx.fillRect(state.ai.x, state.ai.y, state.ai.width, state.ai.height)

  // Draw ball
  ctx.beginPath()
  ctx.arc(state.ball.x, state.ball.y, state.ball.radius, 0, Math.PI * 2)
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--accent-color'
  )
  ctx.fill()
  ctx.closePath()
}

const gameLoop = () => {
  if (!isPlaying.value) return
  updateGame()
  drawGame()
  requestAnimationFrame(gameLoop)
}

const handleKeyDown = (e) => {
  const key = e.key.toLowerCase()
  if (key === 'f') gameState.value.player.upPressed = true
  if (key === 's') gameState.value.player.downPressed = true
}

const handleKeyUp = (e) => {
  const key = e.key.toLowerCase()
  if (key === 'f') gameState.value.player.upPressed = false
  if (key === 's') gameState.value.player.downPressed = false
}

const startGame = () => {
  playerScore.value = 0
  aiScore.value = 0
  isPlaying.value = true
  resetBall()
  gameLoop()
}

const resetBall = () => {
  const state = gameState.value
  state.ball.x = canvasWidth / 2
  state.ball.y = canvasHeight / 2
  // Reset la vitesse à la valeur initiale
  state.ball.speedX = INITIAL_BALL_SPEED * (Math.random() > 0.5 ? 1 : -1)
  state.ball.speedY = INITIAL_BALL_SPEED * (Math.random() * 2 - 1)
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
  background: var(--background-color);
  min-height: 100vh;
  color: var(--text-color);
}

.game-container {
  position: relative;
  margin-top: 20px;
}

canvas {
  border: 2px solid var(--primary-color);
  background: var(--background-color);
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
  background: var(--background-color);
  border: 1px solid var(--primary-color);
  border-radius: 8px;
  min-width: 150px;
}

.score {
  font-size: 24px;
  font-weight: bold;
  color: var(--success-color);
}

.controls {
  font-size: 14px;
  opacity: 0.8;
  color: var(--text-color);
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
  background: var(--background-color);
  padding: 20px;
  border-radius: 8px;
  border: 2px solid var(--primary-color);
}

.start-button {
  padding: 15px 30px;
  font-size: 18px;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-button:hover {
  background: var(--primary-hover-color);
  transform: translateY(-2px);
}
</style>
