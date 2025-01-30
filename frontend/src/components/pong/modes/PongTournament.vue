<template>
  <div class="pong-mode">
    <h2>Mode Tournoi (4 joueurs)</h2>

    <div v-if="currentPhase === 'bracket'" class="tournament-bracket">
      <h3>Tournoi en cours</h3>
      <div class="bracket-round">
        <h4>Demi-finales</h4>
        <div class="match">
          <p>{{ matches[0].player1 }} vs {{ matches[0].player2 }}</p>
          <button v-if="!matches[0].winner" @click="startMatch(0)">Commencer le match</button>
          <p v-else>Vainqueur: {{ matches[0].winner }}</p>
        </div>
        <div class="match">
          <p>{{ matches[1].player1 }} vs {{ matches[1].player2 }}</p>
          <button v-if="!matches[1].winner" @click="startMatch(1)">Commencer le match</button>
          <p v-else>Vainqueur: {{ matches[1].winner }}</p>
        </div>
      </div>
      
      <div class="bracket-round" v-if="matches[0].winner && matches[1].winner">
        <h4>Finale</h4>
        <div class="match">
          <p>{{ matches[0].winner }} vs {{ matches[1].winner }}</p>
          <button @click="startFinal">Commencer la finale</button>
        </div>
      </div>
    </div>

    <div v-if="currentPhase === 'game'" class="game-container">
      <canvas
        ref="gameCanvas"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>

      <!-- Scoreboard -->
      <div class="score-board">
        <div class="player">
          <h3>{{ currentMatch.player1 }}</h3>
          <p class="score">{{ playerScore }}</p>
          <p class="controls">Contrôles: F / S</p>
        </div>
        <div class="player">
          <h3>{{ currentMatch.player2 }}</h3>
          <p class="score">{{ aiScore }}</p>
          <p class="controls">Contrôles: ↑ / ↓</p>
        </div>
      </div>

      <!-- Game Overlays -->
      <div v-if="gamePhase === 'menu'" class="game-overlay">
        <div class="overlay-content">
          <h3>{{ currentMatch.player1 }} vs {{ currentMatch.player2 }}</h3>
          <button @click="startCountdown" class="overlay-button">
            Commencer le match
          </button>
        </div>
      </div>

      <div v-if="gamePhase === 'countdown'" class="game-overlay">
        <div class="overlay-content">
          <h2>Début dans {{ countdownValue }}...</h2>
        </div>
      </div>

      <div v-if="gamePhase === 'over'" class="game-overlay">
        <div class="overlay-content">
          <h2>Match terminé</h2>
          <p>
            <strong>{{ winnerMessage }}</strong>
          </p>
          <button @click="returnToBracket" class="overlay-button">Retour au tournoi</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

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
const BONUS_SPAWN_INTERVAL = 4000
const BONUS_COLORS = ['red', 'green', 'blue']
const BONUS_BAR_WIDTH = 10
const BONUS_BAR_HEIGHT = 60

const INITIAL_PADDLE_HEIGHT = 80

/* ---------------------------------------------------------------------
   ÉTATS DU TOURNOI
--------------------------------------------------------------------- */
const currentPhase = ref('bracket') // 'bracket' ou 'game'
const matches = ref([
  { player1: 'Joueur 1', player2: 'Joueur 2', winner: null },
  { player1: 'Joueur 3', player2: 'Joueur 4', winner: null }
])
const currentMatch = ref(null)
const currentMatchIndex = ref(null)
const isFinal = ref(false)

/* ---------------------------------------------------------------------
   ÉTATS DU JEU
--------------------------------------------------------------------- */
const gameCanvas = ref(null)
const playerScore = ref(0)
const aiScore = ref(0)

const gamePhase = ref('menu')
const countdownValue = ref(3)
const winnerMessage = ref('')

let lastPaddleTouched = null
const roundStartCountdown = ref(0)

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
    speed: 3,
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
})

/* ---------------------------------------------------------------------
   FONCTIONS DU TOURNOI
--------------------------------------------------------------------- */
function startMatch(matchIndex) {
  currentMatchIndex.value = matchIndex
  currentMatch.value = matches.value[matchIndex]
  currentPhase.value = 'game'
  gamePhase.value = 'menu'
  resetGame()
}

function startFinal() {
  isFinal.value = true
  currentMatch.value = {
    player1: matches.value[0].winner,
    player2: matches.value[1].winner
  }
  currentPhase.value = 'game'
  gamePhase.value = 'menu'
  resetGame()
}

function returnToBracket() {
  if (!isFinal.value) {
    matches.value[currentMatchIndex.value].winner = 
      playerScore.value >= WINNING_SCORE ? currentMatch.value.player1 : currentMatch.value.player2
  }
  currentPhase.value = 'bracket'
  currentMatch.value = null
  currentMatchIndex.value = null
}

/* ---------------------------------------------------------------------
   FONCTIONS UTILITAIRES
--------------------------------------------------------------------- */
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

/* ---------------------------------------------------------------------
   GESTION BONUS
--------------------------------------------------------------------- */
function doBarsOverlap(bar1, bar2) {
  return !(
    bar1.x + bar1.width < bar2.x ||
    bar2.x + bar2.width < bar1.x ||
    bar1.y + bar1.height < bar2.y ||
    bar2.y + bar2.height < bar1.y
  )
}

function spawnBonusBar() {
  const state = gameState.value

  if (state.bonusBars.length >= 4) return

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

function applyBonusEffect(color) {
  const state = gameState.value

  switch (color) {
    case 'red':
      if (lastPaddleTouched) {
        state[lastPaddleTouched].height -= 15
        if (state[lastPaddleTouched].height < 40) {
          state[lastPaddleTouched].height = 40
        }
      }
      break
    case 'green':
      if (lastPaddleTouched) {
        state[lastPaddleTouched].height += 15
        if (state[lastPaddleTouched].height > 120) {
          state[lastPaddleTouched].height = 120
        }
      }
      break
    case 'blue':
      state.ball.speedX = -state.ball.speedX
      state.ball.speedY = -state.ball.speedY
      break
  }
}

/* ---------------------------------------------------------------------
   COLLISIONS & RESET
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
  state.player.y = canvasHeight / 2 - state.player.height / 2
  state.ai.y = canvasHeight / 2 - state.ai.height / 2
}

function resetPaddleSizes() {
  const state = gameState.value
  state.player.height = INITIAL_PADDLE_HEIGHT
  state.ai.height = INITIAL_PADDLE_HEIGHT
}

function resetBonuses() {
  const state = gameState.value
  state.bonusBars = []
  state.lastBonusSpawnTime = Date.now()
}

function resetBall() {
  const state = gameState.value
  
  state.ball.x = canvasWidth / 2
  state.ball.y = canvasHeight / 2
  resetPaddles()
  
  resetPaddleSizes()
  resetBonuses()
  
  state.ball.speedX = 0
  state.ball.speedY = 0
  
  roundStartCountdown.value = 1
  setTimeout(() => {
    const goingRight = Math.random() > 0.5
    state.ball.speedX = INITIAL_BALL_SPEED * (goingRight ? 1 : -1)
    state.ball.speedY = INITIAL_BALL_SPEED * (Math.random() * 2 - 1)
    lastPaddleTouched = goingRight ? 'player' : 'ai'
    roundStartCountdown.value = 0
  }, 1000)
}

/* ---------------------------------------------------------------------
   BOUCLE DE JEU
--------------------------------------------------------------------- */
function updateGame() {
  const state = gameState.value

  if (playerScore.value >= WINNING_SCORE || aiScore.value >= WINNING_SCORE) {
    endGame()
    return
  }

  // Joueur 1
  if (state.player.upPressed && state.player.y > 0) {
    state.player.y -= state.player.speed
  }
  if (state.player.downPressed && state.player.y + state.player.height < canvasHeight) {
    state.player.y += state.player.speed
  }

  // Joueur 2
  updatePlayer2()

  // Spawn des bonus
  const now = Date.now()
  if (now - state.lastBonusSpawnTime > BONUS_SPAWN_INTERVAL) {
    spawnBonusBar()
    state.lastBonusSpawnTime = now
  }

  // Collisions avec les bonus
  for (let i = state.bonusBars.length - 1; i >= 0; i--) {
    const bar = state.bonusBars[i]
    if (
      state.ball.x + state.ball.radius >= bar.x &&
      state.ball.x - state.ball.radius <= bar.x + bar.width &&
      state.ball.y + state.ball.radius >= bar.y &&
      state.ball.y - state.ball.radius <= bar.y + bar.height
    ) {
      applyBonusEffect(bar.color)
      state.bonusBars.splice(i, 1)
    }
  }

  // Mise à jour de la balle
  let nextX = state.ball.x + state.ball.speedX
  let nextY = state.ball.y + state.ball.speedY

  // Collision raquette gauche
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

  // Collision raquette droite
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

  // Points
  if (state.ball.x - state.ball.radius < 0) {
    aiScore.value++
    if (aiScore.value < WINNING_SCORE) {
      resetBall()
    }
  }
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

  // Raquettes
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--primary-color'
  )
  ctx.fillRect(
    state.player.x,
    state.player.y,
    state.player.width,
    state.player.height
  )
  ctx.fillRect(state.ai.x, state.ai.y, state.ai.width, state.ai.height)

  // Balle
  ctx.beginPath()
  ctx.arc(state.ball.x, state.ball.y, state.ball.radius, 0, Math.PI * 2)
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--accent-color'
  )
  ctx.fill()
  ctx.closePath()

  // Bonus
  state.bonusBars.forEach((bar) => {
    ctx.fillStyle = bar.color
    ctx.fillRect(bar.x, bar.y, bar.width, bar.height)
  })

  // Compte à rebours
  if (roundStartCountdown.value > 0) {
    ctx.fillStyle = 'white'
    ctx.font = '48px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(roundStartCountdown.value.toString(), canvasWidth / 2, canvasHeight / 2)
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
   PHASES DE JEU
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
  const winner = playerScore.value >= WINNING_SCORE ? currentMatch.value.player1 : currentMatch.value.player2
  winnerMessage.value = `${winner} remporte le match !`
  gamePhase.value = 'over'
}

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
      speed: 3,
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
   LIFECYCLE
--------------------------------------------------------------------- */
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
  drawGame()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
  cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.pong-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  gap: 20px;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 800px;
  padding: 0 20px;
}

.score {
  font-size: 2em;
  font-weight: bold;
  color: var(--primary-color);
}

.game-canvas {
  border: 2px solid var(--primary-color);
  background-color: var(--background-color);
}

.menu-screen,
.countdown-screen,
.game-over-screen {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.8);
  gap: 20px;
}

.menu-title {
  font-size: 3em;
  color: var(--primary-color);
  margin-bottom: 20px;
}

.countdown-value {
  font-size: 5em;
  color: var(--primary-color);
}

.winner-message {
  font-size: 2em;
  color: var(--primary-color);
  text-align: center;
  margin-bottom: 20px;
}

button {
  padding: 10px 20px;
  font-size: 1.2em;
  background-color: var(--primary-color);
  color: var(--background-color);
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: var(--accent-color);
}

.controls-info {
  text-align: center;
  color: var(--text-color);
  margin-top: 10px;
}

/* Styles spécifiques au tournoi */
.tournament-bracket {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 20px 0;
}

.tournament-round {
  display: flex;
  justify-content: space-around;
  width: 100%;
}

.tournament-match {
  background-color: var(--background-color);
  border: 2px solid var(--primary-color);
  padding: 10px;
  border-radius: 5px;
  text-align: center;
}

.tournament-match.active {
  border-color: var(--accent-color);
}

.tournament-player {
  padding: 5px;
  color: var(--text-color);
}

.tournament-player.winner {
  color: var(--accent-color);
  font-weight: bold;
}
</style>
