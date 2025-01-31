<template>
  <div class="tournament-mode">
    <h2>{{ t('pong.tournament.title') }}</h2>

    <!-- Phase de saisie des noms -->
    <div v-if="gamePhase === 'menu'" class="player-setup">
      <div class="player-names">
        <div v-for="index in 3" :key="index" class="player-entry">
          <label>{{ t('pong.game.player') }} {{ index + 1 }}:</label>
          <input
            v-model="players[index]"
            :placeholder="t('pong.tournament.enterName')"
          />
        </div>
      </div>
      <button @click="startTournament" :disabled="!canStart" class="button">
        {{ t('pong.game.startGame') }}
      </button>
    </div>

    <!-- Arbre du tournoi -->
    <div
      v-if="gamePhase === 'menu' || gamePhase === 'tournament-tree'"
      class="tournament-tree"
    >
      <div class="round semi-finals">
        <div class="match">
          <div class="player">{{ getPlayerName(0) }}</div>
          <div class="vs">VS</div>
          <div class="player">{{ getPlayerName(1) }}</div>
        </div>
        <div class="match">
          <div class="player">{{ getPlayerName(2) }}</div>
          <div class="vs">VS</div>
          <div class="player">{{ getPlayerName(3) }}</div>
        </div>
      </div>
      <div class="round final">
        <div class="match">
          <div class="player">{{ winners[0] || '?' }}</div>
          <div class="vs">VS</div>
          <div class="player">{{ winners[1] || '?' }}</div>
        </div>
      </div>
      <div class="winner-display" v-if="tournamentWinner">
        <h3>{{ tournamentWinner }} {{ t('pong.game.wins') }}</h3>
      </div>
    </div>

    <!-- Bouton pour lancer le prochain match -->
    <div
      v-if="gamePhase === 'tournament-tree' && !tournamentWinner"
      class="next-match"
    >
      <button @click="startNextMatch" class="button">
        {{ t('pong.tournament.nextMatch') }}
      </button>
      <div class="next-match-info">
        {{ currentMatch.player1 }} vs {{ currentMatch.player2 }}
      </div>
    </div>

    <!-- Le jeu -->
    <div v-show="gamePhase === 'playing'" class="game-container">
      <GameCanvas
        ref="gameCanvasRef"
        :player1-name="currentMatch.player1"
        :player2-name="currentMatch.player2"
        :player1-score="player1Score"
        :player2-score="player2Score"
        :game-phase="canvasPhase"
        :countdown-value="countdownValue"
        :winner="matchWinner"
        @start-game="launchGame"
        @close-match="handleMatchEnd"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import GameCanvas from '../common/GameCanvas.vue'
import { GameEngine } from '../common/GameEngine'

const { t } = useI18n()
const authStore = useAuthStore()

// État du tournoi
const gamePhase = ref('menu')
const canvasPhase = ref('ready')
const players = ref([
  authStore.user?.username || '', // Utiliser le pseudo de l'utilisateur connecté
  '',
  '',
  '',
])
const winners = ref(['', ''])
const tournamentWinner = ref('')
const currentMatchIndex = ref(0)
const currentMatch = ref({ player1: '', player2: '', round: 'semi' })

// État du jeu
const gameCanvasRef = ref(null)
const gameEngine = ref(null)
const countdownValue = ref(3)
const player1Score = ref(0)
const player2Score = ref(0)
const matchWinner = ref('')

let animationId = null

// Vérifier uniquement les joueurs 2 à 4
const canStart = computed(() => {
  return players.value.slice(1).every((player) => player.trim() !== '')
})

function getPlayerName(index) {
  return players.value[index] || t('pong.game.player') + ' ' + (index + 1)
}

function startTournament() {
  if (!canStart.value) return
  gamePhase.value = 'tournament-tree'
  setupNextMatch()
}

function setupNextMatch() {
  if (currentMatchIndex.value < 2) {
    // Demi-finales
    const matchIndex = currentMatchIndex.value
    currentMatch.value = {
      player1: getPlayerName(matchIndex * 2),
      player2: getPlayerName(matchIndex * 2 + 1),
      round: 'semi',
    }
  } else if (currentMatchIndex.value === 2) {
    // Finale
    currentMatch.value = {
      player1: winners.value[0],
      player2: winners.value[1],
      round: 'final',
    }
  }
}

function startNextMatch() {
  gamePhase.value = 'playing'
  canvasPhase.value = 'ready'
  player1Score.value = 0
  player2Score.value = 0
  matchWinner.value = ''

  nextTick(() => {
    const canvas = gameCanvasRef.value?.canvas
    if (canvas) {
      gameEngine.value = new GameEngine(canvas.width, canvas.height)
      // Forcer une première frame pour s'assurer que tout est initialisé
      const ctx = canvas.getContext('2d')
      gameEngine.value.drawGame(ctx)
      // Lancer automatiquement le jeu
      launchGame()
    }
  })
}

function launchGame() {
  if (!gameEngine.value) return

  countdownValue.value = 3
  canvasPhase.value = 'countdown'

  const interval = setInterval(() => {
    countdownValue.value--
    if (countdownValue.value <= 0) {
      clearInterval(interval)
      canvasPhase.value = 'playing'
      gameEngine.value.launchBall()
      nextTick(() => {
        if (gameEngine.value) {
          gameLoop()
        }
      })
    }
  }, 1000)
}

function gameLoop() {
  if (!gameEngine.value || canvasPhase.value !== 'playing') return

  const canvas = gameCanvasRef.value?.canvas
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const isGameOver = gameEngine.value.updateGame(
    player1Score.value,
    player2Score.value,
    (player) => {
      if (player === 'player1') player1Score.value++
      else player2Score.value++
    }
  )

  if (isGameOver) {
    endMatch()
    return
  }

  gameEngine.value.drawGame(ctx)
  animationId = requestAnimationFrame(gameLoop)
}

function endMatch() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  canvasPhase.value = 'over'
  const winner =
    player1Score.value > player2Score.value
      ? currentMatch.value.player1
      : currentMatch.value.player2
  matchWinner.value = winner

  if (currentMatch.value.round === 'semi') {
    winners.value[currentMatchIndex.value] = winner
  } else {
    tournamentWinner.value = winner
  }
}

function handleMatchEnd() {
  currentMatchIndex.value++
  if (currentMatchIndex.value < 3) {
    gamePhase.value = 'tournament-tree'
    setupNextMatch()
  } else {
    gamePhase.value = 'tournament-tree'
  }
}

// Gestion des événements clavier
function handleKeyDown(e) {
  if (gameEngine.value && canvasPhase.value === 'playing') {
    gameEngine.value.handleKeyDown(e)
  }
}

function handleKeyUp(e) {
  if (gameEngine.value && canvasPhase.value === 'playing') {
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
.tournament-mode {
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

.tournament-tree {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 800px;
}

.round {
  display: flex;
  justify-content: center;
  gap: 2rem;
  width: 100%;
}

.match {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  background: var(--background-color);
  min-width: 200px;
}

.vs {
  color: var(--primary-color);
  font-weight: bold;
}

.winner-display {
  text-align: center;
  margin-top: 2rem;
  padding: 1rem;
  border: 2px solid var(--success-color);
  border-radius: 4px;
  background: var(--background-color);
}

.next-match {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0;
}

.next-match-info {
  font-size: 1.2rem;
  color: var(--primary-color);
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
