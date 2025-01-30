<template>
  <div class="pong-mode">
    <h2>{{ $t('pong.local.title') }}</h2>

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
          <p class="score">{{ player1Score }}</p>
          <p class="controls">{{ $t('pong.game.controls') }}: F / S</p>
        </div>
        <div class="player">
          <h3>{{ player2Name || $t('pong.game.player2') }}</h3>
          <p class="score">{{ player2Score }}</p>
          <p class="controls">{{ $t('pong.game.controls') }}: ↑ / ↓</p>
        </div>
      </div>

      <!-- Overlays -->
      <div v-if="gamePhase === 'menu'" class="game-overlay">
        <div class="overlay-content">
          <h3>{{ $t('pong.game.enterName') }}</h3>
          <input
            v-model="player2Name"
            type="text"
            class="player-input"
            :placeholder="$t('pong.game.enterName')"
            @keyup.enter="startCountdown"
          />
          <button
            @click="startCountdown"
            class="overlay-button"
            :disabled="!player2Name.trim()"
          >
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
import axios from 'axios'

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

// Bonus
const BONUS_SPAWN_INTERVAL = 4000 // toutes les 4s
const BONUS_COLORS = ['red', 'green', 'blue']
const BONUS_BAR_WIDTH = 10
const BONUS_BAR_HEIGHT = 60

// Raquettes
const INITIAL_PADDLE_HEIGHT = 80

/* ---------------------------------------------------------------------
   ÉTATS
--------------------------------------------------------------------- */
const gameCanvas = ref(null)
const player1Score = ref(0)
const player2Score = ref(0)
const player2Name = ref('')

// Phases : 'menu' | 'countdown' | 'playing' | 'over'
const gamePhase = ref('menu')
const countdownValue = ref(3)
const winnerMessage = ref('')

// Mémorise qui a touché la balle en dernier : 'player1' ou 'player2'
let lastPaddleTouched = null

// Compte à rebours de début de manche
const roundStartCountdown = ref(0)

/**
 * État principal
 */
const gameState = ref({
  // Joueur 1
  player1: {
    x: 20,
    y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
    width: 10,
    height: INITIAL_PADDLE_HEIGHT,
    speed: 3,
    upPressed: false,
    downPressed: false,
  },
  // Joueur 2
  player2: {
    x: canvasWidth - 30,
    y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
    width: 10,
    height: INITIAL_PADDLE_HEIGHT,
    speed: 3,
    upPressed: false,
    downPressed: false,
  },
  // Balle
  ball: {
    x: canvasWidth / 2,
    y: canvasHeight / 2,
    radius: 8,
    speedX: 0,
    speedY: 0,
  },
  // Liste de barres bonus
  bonusBars: [],
  lastBonusSpawnTime: Date.now(),
})

/* ---------------------------------------------------------------------
   FONCTIONS UTILES
--------------------------------------------------------------------- */
/**
 * y aléatoire pour la barre, en évitant la zone trop proche du centre
 */
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
 * Fait apparaître un nouveau bonus (barre verticale)
 * sans chevauchement avec les autres
 */
function spawnBonusBar() {
  const state = gameState.value

  // Limite à 4 bonus simultanés
  if (state.bonusBars.length >= 4) return

  // On tente 10 fois de placer un nouveau bonus
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

    // Vérifie le chevauchement
    let hasOverlap = false
    for (const existingBar of state.bonusBars) {
      if (doBarsOverlap(newBar, existingBar)) {
        hasOverlap = true
        break
      }
    }

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
      // (même si personne n'a touché, on inverse la balle)
      state.ball.speedX = -state.ball.speedX
      state.ball.speedY = -state.ball.speedY
      break
  }
}

/* ---------------------------------------------------------------------
   GESTION DES RAQUETTES
--------------------------------------------------------------------- */
function resetPaddles() {
  const state = gameState.value
  // Centre les deux raquettes
  state.player1.y = canvasHeight / 2 - state.player1.height / 2
  state.player2.y = canvasHeight / 2 - state.player2.height / 2
}

function resetPaddleSizes() {
  const state = gameState.value
  // Remet les raquettes à leur taille initiale
  state.player1.height = INITIAL_PADDLE_HEIGHT
  state.player2.height = INITIAL_PADDLE_HEIGHT
}

function resetBonuses() {
  const state = gameState.value
  // Vide la liste des bonus
  state.bonusBars = []
  // Réinitialise le timer
  state.lastBonusSpawnTime = Date.now()
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

  if (who === 'player1') {
    state.ball.speedX = Math.abs(currentSpeed * Math.cos(bounceAngle))
  } else {
    state.ball.speedX = -Math.abs(currentSpeed * Math.cos(bounceAngle))
  }
  state.ball.speedY = currentSpeed * Math.sin(bounceAngle)
}

/**
 * Reset de la balle et raquettes après un point
 */
function resetBall() {
  const state = gameState.value
  // Centre la balle
  state.ball.x = canvasWidth / 2
  state.ball.y = canvasHeight / 2

  // Centre les raquettes et remets leur taille
  resetPaddles()
  resetPaddleSizes()

  // Reset bonus
  resetBonuses()

  // Immobilise la balle pendant 1 seconde
  state.ball.speedX = 0
  state.ball.speedY = 0

  // Après 1 seconde, on lance la balle
  roundStartCountdown.value = 1
  setTimeout(() => {
    const goingRight = Math.random() > 0.5
    state.ball.speedX = INITIAL_BALL_SPEED * (goingRight ? 1 : -1)
    state.ball.speedY = INITIAL_BALL_SPEED * (Math.random() * 2 - 1)
    lastPaddleTouched = goingRight ? 'player1' : 'player2'
    roundStartCountdown.value = 0
  }, 1000)
}

/* ---------------------------------------------------------------------
   BOUCLE DE MISE À JOUR
--------------------------------------------------------------------- */
function updateGame() {
  const state = gameState.value

  // Vérif victoire
  if (
    player1Score.value >= WINNING_SCORE ||
    player2Score.value >= WINNING_SCORE
  ) {
    endGame()
    return
  }

  // Mouvements Joueur 1
  if (state.player1.upPressed && state.player1.y > 0) {
    state.player1.y -= state.player1.speed
  }
  if (
    state.player1.downPressed &&
    state.player1.y + state.player1.height < canvasHeight
  ) {
    state.player1.y += state.player1.speed
  }

  // Mouvements Joueur 2
  if (state.player2.upPressed && state.player2.y > 0) {
    state.player2.y -= state.player2.speed
  }
  if (
    state.player2.downPressed &&
    state.player2.y + state.player2.height < canvasHeight
  ) {
    state.player2.y += state.player2.speed
  }

  // BONUS : spawn toutes les 4s
  const now = Date.now()
  if (now - state.lastBonusSpawnTime > BONUS_SPAWN_INTERVAL) {
    spawnBonusBar()
    state.lastBonusSpawnTime = now
  }

  // Collision balle / bonus
  for (let i = state.bonusBars.length - 1; i >= 0; i--) {
    const bar = state.bonusBars[i]
    if (
      state.ball.x + state.ball.radius >= bar.x &&
      state.ball.x - state.ball.radius <= bar.x + bar.width
    ) {
      if (
        state.ball.y + state.ball.radius >= bar.y &&
        state.ball.y - state.ball.radius <= bar.y + bar.height
      ) {
        // Applique l'effet
        applyBonusEffect(bar.color)
        // Retire le bonus
        state.bonusBars.splice(i, 1)
      }
    }
  }

  // Mise à jour de la balle
  let nextX = state.ball.x + state.ball.speedX
  let nextY = state.ball.y + state.ball.speedY

  // Collision raquette gauche (player1)
  if (
    nextX - state.ball.radius <= state.player1.x + state.player1.width &&
    nextX - state.ball.radius >= state.player1.x &&
    state.ball.y >= state.player1.y &&
    state.ball.y <= state.player1.y + state.player1.height &&
    state.ball.speedX < 0
  ) {
    paddleBounce('player1')
    nextX = state.ball.x + state.ball.speedX
    nextY = state.ball.y + state.ball.speedY
  }

  // Collision raquette droite (player2)
  if (
    nextX + state.ball.radius >= state.player2.x &&
    nextX + state.ball.radius <= state.player2.x + state.player2.width &&
    state.ball.y >= state.player2.y &&
    state.ball.y <= state.player2.y + state.player2.height &&
    state.ball.speedX > 0
  ) {
    paddleBounce('player2')
    nextX = state.ball.x + state.ball.speedX
    nextY = state.ball.y + state.ball.speedY
  }

  // Applique la nouvelle position
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

  // Sortie à gauche => point Joueur 2
  if (state.ball.x - state.ball.radius < 0) {
    player2Score.value++
    if (player2Score.value < WINNING_SCORE) {
      resetBall()
    }
  }

  // Sortie à droite => point Joueur 1
  if (state.ball.x + state.ball.radius > canvasWidth) {
    player1Score.value++
    if (player1Score.value < WINNING_SCORE) {
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

  // Raquette Joueur 1
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--primary-color'
  )
  ctx.fillRect(
    state.player1.x,
    state.player1.y,
    state.player1.width,
    state.player1.height
  )

  // Raquette Joueur 2
  ctx.fillRect(
    state.player2.x,
    state.player2.y,
    state.player2.width,
    state.player2.height
  )

  // Balle
  ctx.beginPath()
  ctx.arc(state.ball.x, state.ball.y, state.ball.radius, 0, Math.PI * 2)
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--accent-color'
  )
  ctx.fill()
  ctx.closePath()

  // Dessine tous les bonus
  state.bonusBars.forEach((bar) => {
    ctx.fillStyle = bar.color
    ctx.fillRect(bar.x, bar.y, bar.width, bar.height)
  })

  // Affiche un compte à rebours de 1 seconde si roundStartCountdown > 0
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
  if (!player2Name.value.trim()) return
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
  player1Score.value = 0
  player2Score.value = 0
  resetGameState()
  resetPaddles()
  resetBall()
  gamePhase.value = 'playing'
  gameLoop()
}


function endGame() {
  cancelAnimationFrame(animationId)
  if (player1Score.value >= WINNING_SCORE) {
    winnerMessage.value = (username.value || $t('pong.game.player1')) + ' ' + ' wins'
  } else {
    winnerMessage.value = player2Name.value + ' wins'
  }
  gamePhase.value = 'over'
  saveGameHistory()
}
const guestUsername = ref(player2Name)
const saveGameHistory = async () =>{
	try {
		const gameHistory = {
			user: authStore.user.id,
			guest_name: guestUsername.value,
			user_score: player1Score.value,
			guest_score: player2Score.value,
			played_at: new Date().toISOString(),
			game_name: 'pong',
		}
		await axios.post('/users/histories/add', gameHistory, {
			withCredentials: true,
		})
		console.log('history saved')
	} catch (error) {
		console.error('Error saving game history:', error)
	}
}

function restartGame() {
  player2Name.value = ''
  gamePhase.value = 'menu'
}

/**
 * Reset l'état du jeu
 */
function resetGameState() {
  gameState.value = {
    player1: {
      x: 20,
      y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
      width: 10,
      height: INITIAL_PADDLE_HEIGHT,
      speed: 4.5,
      upPressed: false,
      downPressed: false,
    },
    player2: {
      x: canvasWidth - 30,
      y: canvasHeight / 2 - INITIAL_PADDLE_HEIGHT / 2,
      width: 10,
      height: INITIAL_PADDLE_HEIGHT,
      speed: 4.5,
      upPressed: false,
      downPressed: false,
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
   CONTRÔLES CLAVIER
--------------------------------------------------------------------- */
function handleKeyDown(e) {
  const key = e.key
  // Joueur 1
  if (key.toLowerCase() === 'f') gameState.value.player1.upPressed = true
  if (key.toLowerCase() === 's') gameState.value.player1.downPressed = true

  // Joueur 2
  if (key === 'ArrowUp') gameState.value.player2.upPressed = true
  if (key === 'ArrowDown') gameState.value.player2.downPressed = true
}

function handleKeyUp(e) {
  const key = e.key
  // Joueur 1
  if (key.toLowerCase() === 'f') gameState.value.player1.upPressed = false
  if (key.toLowerCase() === 's') gameState.value.player1.downPressed = false

  // Joueur 2
  if (key === 'ArrowUp') gameState.value.player2.upPressed = false
  if (key === 'ArrowDown') gameState.value.player2.downPressed = false
}

/* ---------------------------------------------------------------------
   LIFECYCLE
--------------------------------------------------------------------- */
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
  drawGame() // Dessin initial
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

.player-input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 2px solid var(--primary-color);
  border-radius: 5px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 16px;
}

.player-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.overlay-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style>
