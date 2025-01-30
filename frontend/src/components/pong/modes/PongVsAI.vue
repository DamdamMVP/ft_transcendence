<template>
  <div class="pong-mode">
    <h2>{{ $t('pong.ai.title') }}</h2>

    <div class="game-container">
      <canvas
        ref="gameCanvas"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>

      <!-- Scoreboard -->
      <div class="score-board">
        <div class="player">
          <h3>{{ username || $t('pong.game.player1') }}</h3>
          <p class="score">{{ playerScore }}</p>
          <p class="controls">{{ $t('pong.game.controls') }}: F / S</p>
        </div>
        <div class="player">
          <h3>{{ $t('pong.ai.title') }}</h3>
          <p class="score">{{ aiScore }}</p>
        </div>
      </div>

      <!-- Overlays -->
      <div v-if="gamePhase === 'menu'" class="game-overlay">
        <div class="overlay-content">
          <button @click="startCountdown" class="overlay-button">
            {{ $t('pong.game.startGame') }}
          </button>
        </div>
      </div>

      <div v-if="gamePhase === 'countdown'" class="game-overlay">
        <div class="overlay-content">
          <h2>{{ $t('pong.game.countdown') }} {{ countdownValue }}...</h2>
        </div>
      </div>

      <div v-if="gamePhase === 'over'" class="game-overlay">
        <div class="overlay-content">
          <h2>{{ winnerMessage }}</h2>
          <button @click="restartGame" class="overlay-button">
            {{ $t('pong.game.startGame') }}
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
const username = ref(authStore.user?.username || '')

/* ---------------------------------------------------------------------
   CONSTANTES
--------------------------------------------------------------------- */
const canvasWidth = 800
const canvasHeight = 400
const WINNING_SCORE = 5

// Balle
const INITIAL_BALL_SPEED = 4
const BALL_SPEED_INCREASE = 1.1
const MAX_BALL_SPEED = 10

// IA
const AI_UPDATE_INTERVAL = 1000 // vision 1 fois/s

// Bonus
const BONUS_SPAWN_INTERVAL = 4000 // toutes les 4s
const BONUS_COLORS = ['red', 'green', 'blue']
const BONUS_BAR_WIDTH = 10
const BONUS_BAR_HEIGHT = 60

const INITIAL_PADDLE_HEIGHT = 80 // Hauteur initiale des raquettes

/* ---------------------------------------------------------------------
   ÉTATS
--------------------------------------------------------------------- */
const gameCanvas = ref(null)
const playerScore = ref(0)
const aiScore = ref(0)

// Phases : 'menu' | 'countdown' | 'playing' | 'over'
const gamePhase = ref('menu')
const countdownValue = ref(3)
const winnerMessage = ref('')

// Quel joueur a touché la balle en dernier ?
let lastPaddleTouched = null

// Compte à rebours de début de manche
const roundStartCountdown = ref(0)

/**
 * État principal
 */
const gameState = ref({
  player: {
    x: 20,
    y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
    width: 10,
    height: INITIAL_PADDLE_HEIGHT,
    speed: 3,
    upPressed: false,
    downPressed: false,
  },
  ai: {
    x: canvasWidth - 30,
    y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
    width: 10,
    height: INITIAL_PADDLE_HEIGHT,
    baseSpeed: 2,
    lastUpdateTime: 0,
    upPressed: false,
    downPressed: false,
    targetY: canvasHeight / 2,
  },
  ball: {
    x: canvasWidth / 2,
    y: canvasHeight / 2,
    radius: 8,
    speedX: 0,
    speedY: 0,
  },
  bonusBars: [], // <-- Liste de barres multiples
  lastBonusSpawnTime: Date.now(), // Pour gérer le spawn toutes les 4s
})

/* ---------------------------------------------------------------------
   FONCTIONS UTILITAIRES
--------------------------------------------------------------------- */

/** y aléatoire évitant la zone centrale */
function getRandomYNotCenter(barHeight) {
  const forbiddenMargin = 60
  const forbiddenMin = canvasHeight / 2 - forbiddenMargin
  const forbiddenMax = canvasHeight / 2 + forbiddenMargin

  let y = 0
  do {
    y = Math.random() * (canvasHeight - barHeight)
  } while (y >= forbiddenMin && y + barHeight <= forbiddenMax)

  return y
}

/** Calcule la position finale Y de la balle pour l'IA */
function predictBallPositionMultiBounceNoError() {
  const state = gameState.value
  const aiX = state.ai.x
  const { x, y, speedX, speedY, radius } = state.ball

  if (speedX <= 0) {
    return canvasHeight / 2
  }

  let futureX = x
  let futureY = y
  let vx = speedX
  let vy = speedY
  while (futureX + radius < aiX) {
    futureX += vx
    futureY += vy
    if (futureY - radius < 0) {
      futureY = radius
      vy = -vy
    }
    if (futureY + radius > canvasHeight) {
      futureY = canvasHeight - radius
      vy = -vy
    }
  }
  return futureY
}

/* ---------------------------------------------------------------------
   GESTION BONUS MULTIPLES
--------------------------------------------------------------------- */
/**
 * Vérifie si deux barres se chevauchent
 */
function doBarsOverlap(bar1, bar2) {
  return !(
    bar1.x + bar1.width < bar2.x ||
    bar2.x + bar2.width < bar1.x ||
    bar1.y + bar1.height < bar2.y ||
    bar2.y + bar2.height < bar1.y
  )
}

/**
 * Créé une nouvelle barre dans la liste bonusBars
 */
function spawnBonusBar() {
  const state = gameState.value

  // Limite le nombre maximum de bonus à 3 sur l'écran
  if (state.bonusBars.length >= 4) return

  // Essaie de placer un nouveau bonus jusqu'à 10 tentatives
  for (let attempts = 0; attempts < 10; attempts++) {
    const colorIndex = Math.floor(Math.random() * BONUS_COLORS.length)
    const color = BONUS_COLORS[colorIndex]

    const newBar = {
      color,
      width: BONUS_BAR_WIDTH,
      height: BONUS_BAR_HEIGHT,
      x: canvasWidth / 2 - BONUS_BAR_WIDTH / 2,
      y: getRandomYNotCenter(BONUS_BAR_HEIGHT),
    }

    // Vérifie s'il y a chevauchement avec les barres existantes
    let hasOverlap = false
    for (const existingBar of state.bonusBars) {
      if (doBarsOverlap(newBar, existingBar)) {
        hasOverlap = true
        break
      }
    }

    // Si pas de chevauchement, on ajoute la nouvelle barre
    if (!hasOverlap) {
      state.bonusBars.push(newBar)
      return
    }
  }
}

/**
 * Applique l'effet du bonus sur le dernier joueur ayant touché la balle
 */
function applyBonusEffect(color) {
  const state = gameState.value

  switch (color) {
    case 'red':
      // Rétrécit la raquette
      if (lastPaddleTouched) {
        state[lastPaddleTouched].height -= 15
        if (state[lastPaddleTouched].height < 40) {
          state[lastPaddleTouched].height = 40
        }
      }
      break
    case 'green':
      // Agrandit la raquette
      if (lastPaddleTouched) {
        state[lastPaddleTouched].height += 15
        if (state[lastPaddleTouched].height > 120) {
          state[lastPaddleTouched].height = 120
        }
      }
      break
    case 'blue':
      // Inverse la direction de la balle
      // Si personne n'a touché la balle, on inverse quand même
      state.ball.speedX = -state.ball.speedX
      state.ball.speedY = -state.ball.speedY
      break
  }
}

/* ---------------------------------------------------------------------
   IA
--------------------------------------------------------------------- */
function updateAI() {
  const state = gameState.value
  const now = Date.now()

  if (now - state.ai.lastUpdateTime >= AI_UPDATE_INTERVAL) {
    state.ai.lastUpdateTime = now
    const predY = predictBallPositionMultiBounceNoError()
    state.ai.targetY = predY
  }

  const margin = 5
  const aiCenter = state.ai.y + state.ai.height / 2

  if (aiCenter < state.ai.targetY - margin) {
    state.ai.downPressed = true
    state.ai.upPressed = false
  } else if (aiCenter > state.ai.targetY + margin) {
    state.ai.downPressed = false
    state.ai.upPressed = true
  } else {
    state.ai.downPressed = false
    state.ai.upPressed = false
  }

  if (state.ai.upPressed && state.ai.y > 0) {
    state.ai.y -= state.ai.baseSpeed
  }
  if (state.ai.downPressed && state.ai.y + state.ai.height < canvasHeight) {
    state.ai.y += state.ai.baseSpeed
  }

  if (state.ai.y < 0) {
    state.ai.y = 0
  }
  if (state.ai.y + state.ai.height > canvasHeight) {
    state.ai.y = canvasHeight - state.ai.height
  }
}

/* ---------------------------------------------------------------------
   BALLE & COLLISIONS
--------------------------------------------------------------------- */
function paddleBounce(who) {
  lastPaddleTouched = who
  const state = gameState.value
  const paddle = state[who]

  let currentSpeed = Math.sqrt(state.ball.speedX ** 2 + state.ball.speedY ** 2)
  currentSpeed = Math.min(currentSpeed * BALL_SPEED_INCREASE, MAX_BALL_SPEED)

  const paddleCenter = paddle.y + paddle.height / 2
  const distFromCenter = (state.ball.y - paddleCenter) / (paddle.height / 2)
  const maxBounceAngle = 60 * (Math.PI / 180)
  const bounceAngle = distFromCenter * maxBounceAngle

  if (who === 'player') {
    state.ball.speedX = Math.abs(currentSpeed * Math.cos(bounceAngle))
  } else {
    state.ball.speedX = -Math.abs(currentSpeed * Math.cos(bounceAngle))
  }
  state.ball.speedY = currentSpeed * Math.sin(bounceAngle)
}

function resetPaddles() {
  const state = gameState.value
  // Centre les deux raquettes
  state.player.y = canvasHeight / 2 - state.player.height / 2
  state.ai.y = canvasHeight / 2 - state.ai.height / 2
}

function resetPaddleSizes() {
  const state = gameState.value
  // Remet les raquettes à leur taille initiale
  state.player.height = INITIAL_PADDLE_HEIGHT
  state.ai.height = INITIAL_PADDLE_HEIGHT
}

function resetBonuses() {
  const state = gameState.value
  // Vide la liste des bonus
  state.bonusBars = []
  // Réinitialise le timer de spawn
  state.lastBonusSpawnTime = Date.now()
}

function resetBall() {
  const state = gameState.value

  // Reset positions
  state.ball.x = canvasWidth / 2
  state.ball.y = canvasHeight / 2
  resetPaddles()

  // Reset tailles et bonus
  resetPaddleSizes()
  resetBonuses()

  // Arrête la balle pendant le compte à rebours
  state.ball.speedX = 0
  state.ball.speedY = 0

  // Lance le compte à rebours de 1 seconde
  roundStartCountdown.value = 1
  setTimeout(() => {
    // Après 1 seconde, lance la balle dans une direction aléatoire
    const goingRight = Math.random() > 0.5
    state.ball.speedX = INITIAL_BALL_SPEED * (goingRight ? 1 : -1)
    state.ball.speedY = INITIAL_BALL_SPEED * (Math.random() * 2 - 1)
    lastPaddleTouched = goingRight ? 'player' : 'ai'
    roundStartCountdown.value = 0
  }, 1000)
}

/* ---------------------------------------------------------------------
   BOUCLE DE MISE À JOUR
--------------------------------------------------------------------- */
function updateGame() {
  const state = gameState.value

  // Vérif victoire
  if (playerScore.value >= WINNING_SCORE || aiScore.value >= WINNING_SCORE) {
    endGame()
    return
  }

  // Joueur
  if (state.player.upPressed && state.player.y > 0) {
    state.player.y -= state.player.speed
  }
  if (
    state.player.downPressed &&
    state.player.y + state.player.height < canvasHeight
  ) {
    state.player.y += state.player.speed
  }

  // IA
  updateAI()

  // BONUS : spawn toutes les 4s (même si d'autres sont encore présentes)
  const now = Date.now()
  if (now - state.lastBonusSpawnTime > BONUS_SPAWN_INTERVAL) {
    spawnBonusBar()
    state.lastBonusSpawnTime = now
  }

  // Vérifier collisions balle / bonusBars
  // (On parcourt le tableau à l'envers pour pouvoir splice)
  for (let i = state.bonusBars.length - 1; i >= 0; i--) {
    const bar = state.bonusBars[i]
    // Collision en X ?
    if (
      state.ball.x + state.ball.radius >= bar.x &&
      state.ball.x - state.ball.radius <= bar.x + bar.width
    ) {
      // Collision en Y ?
      if (
        state.ball.y + state.ball.radius >= bar.y &&
        state.ball.y - state.ball.radius <= bar.y + bar.height
      ) {
        // Appliquer effet
        applyBonusEffect(bar.color)
        // Retirer la barre
        state.bonusBars.splice(i, 1)
      }
    }
  }

  // Mise à jour de la balle
  let nextX = state.ball.x + state.ball.speedX
  let nextY = state.ball.y + state.ball.speedY

  // Collision raquette gauche (player)
  if (
    nextX - state.ball.radius <= state.player.x + state.player.width &&
    nextX - state.ball.radius >= state.player.x &&
    state.ball.y >= state.player.y &&
    state.ball.y <= state.player.y + state.player.height &&
    state.ball.speedX < 0
  ) {
    paddleBounce('player')
    nextX = state.ball.x + state.ball.speedX
    nextY = state.ball.y + state.ball.speedY
  }

  // Collision raquette droite (IA)
  if (
    nextX + state.ball.radius >= state.ai.x &&
    nextX + state.ball.radius <= state.ai.x + state.ai.width &&
    state.ball.y >= state.ai.y &&
    state.ball.y <= state.ai.y + state.ai.height &&
    state.ball.speedX > 0
  ) {
    paddleBounce('ai')
    nextX = state.ball.x + state.ball.speedX
    nextY = state.ball.y + state.ball.speedY
  }

  // Position
  state.ball.x = nextX
  state.ball.y = nextY

  // Rebonds haut/bas
  if (state.ball.y - state.ball.radius < 0) {
    state.ball.y = state.ball.radius
    state.ball.speedY = -state.ball.speedY
  } else if (state.ball.y + state.ball.radius > canvasHeight) {
    state.ball.y = canvasHeight - state.ball.radius
    state.ball.speedY = -state.ball.speedY
  }

  // Sortie à gauche => IA marque
  if (state.ball.x - state.ball.radius < 0) {
    aiScore.value++
    if (aiScore.value < WINNING_SCORE) {
      resetBall()
    }
  }

  // Sortie à droite => Joueur marque
  if (state.ball.x + state.ball.radius > canvasWidth) {
    playerScore.value++
    if (playerScore.value < WINNING_SCORE) {
      resetBall()
    }
  }
}

function drawGame() {
  const ctx = gameCanvas.value.getContext('2d')
  const state = gameState.value

  // Fond
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--background-color'
  )
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  // Bordure
  ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--primary-color'
  )
  ctx.lineWidth = 2
  ctx.strokeRect(0, 0, canvasWidth, canvasHeight)

  // Raquette Joueur
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--primary-color'
  )
  ctx.fillRect(
    state.player.x,
    state.player.y,
    state.player.width,
    state.player.height
  )

  // Raquette IA
  ctx.fillRect(state.ai.x, state.ai.y, state.ai.width, state.ai.height)

  // Balle
  ctx.beginPath()
  ctx.arc(state.ball.x, state.ball.y, state.ball.radius, 0, Math.PI * 2)
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--accent-color'
  )
  ctx.fill()
  ctx.closePath()

  // Dessin de TOUTES les barres bonus
  state.bonusBars.forEach((bar) => {
    ctx.fillStyle = bar.color
    ctx.fillRect(bar.x, bar.y, bar.width, bar.height)
  })

  // Affiche le compte à rebours de début de manche si actif
  if (roundStartCountdown.value > 0) {
    ctx.fillStyle = 'white'
    ctx.font = '48px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(
      roundStartCountdown.value.toString(),
      canvasWidth / 2,
      canvasHeight / 2
    )
  }
}

let animationId = null
function gameLoop() {
  if (gamePhase.value !== 'playing') return
  updateGame()
  drawGame()
  animationId = requestAnimationFrame(gameLoop)
}

/* ---------------------------------------------------------------------
   PHASES
--------------------------------------------------------------------- */
function startCountdown() {
  countdownValue.value = 3
  gamePhase.value = 'countdown'
  const interval = setInterval(() => {
    countdownValue.value--
    if (countdownValue.value <= 0) {
      clearInterval(interval)
      startGame()
    }
  }, 1000)
}

function startGame() {
  playerScore.value = 0
  aiScore.value = 0
  resetGameState()
  resetPaddles()
  resetBall()
  gamePhase.value = 'playing'
  gameLoop()
}

function endGame() {
  cancelAnimationFrame(animationId)
  if (playerScore.value >= WINNING_SCORE) {
    winnerMessage.value = (username.value || 'Player 1') + ' wins'
  } else {
    winnerMessage.value = 'AI wins'
  }
  gamePhase.value = 'over'
}

function restartGame() {
  gamePhase.value = 'menu'
}

/**
 * Reset l'état du jeu
 */
function resetGameState() {
  gameState.value = {
    player: {
      x: 20,
      y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
      width: 10,
      height: INITIAL_PADDLE_HEIGHT,
      speed: 3,
      upPressed: false,
      downPressed: false,
    },
    ai: {
      x: canvasWidth - 30,
      y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
      width: 10,
      height: INITIAL_PADDLE_HEIGHT,
      baseSpeed: 2,
      lastUpdateTime: 0,
      upPressed: false,
      downPressed: false,
      targetY: canvasHeight / 2,
    },
    ball: {
      x: canvasWidth / 2,
      y: canvasHeight / 2,
      radius: 8,
      speedX: 0,
      speedY: 0,
    },
    bonusBars: [],
    lastBonusSpawnTime: Date.now(),
  }
  lastPaddleTouched = null
}

/* ---------------------------------------------------------------------
   CONTRÔLES JOUEUR
--------------------------------------------------------------------- */
function handleKeyDown(e) {
  const key = e.key.toLowerCase()
  if (key === 'f') gameState.value.player.upPressed = true
  if (key === 's') gameState.value.player.downPressed = true
}

function handleKeyUp(e) {
  const key = e.key.toLowerCase()
  if (key === 'f') gameState.value.player.upPressed = false
  if (key === 's') gameState.value.player.downPressed = false
}

/* ---------------------------------------------------------------------
   LIFECYCLE
--------------------------------------------------------------------- */
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
  drawGame() // initial
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
  cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.pong-mode {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: var(--background-color);
  min-height: 65vh;
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
  gap: 20px;
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

/* Overlays (menu, countdown, over) */
.game-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay-content {
  background: var(--background-color);
  padding: 30px;
  border-radius: 8px;
  border: 2px solid var(--primary-color);
  text-align: center;
}

.overlay-button {
  padding: 15px 30px;
  font-size: 18px;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.overlay-button:hover {
  background: var(--primary-hover-color);
  transform: translateY(-2px);
}
</style>
