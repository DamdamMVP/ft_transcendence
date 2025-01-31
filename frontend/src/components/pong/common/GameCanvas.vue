<template>
  <div class="game-container">
    <canvas
      ref="canvas"
      :width="canvasWidth"
      :height="canvasHeight"
    ></canvas>

    <!-- Scoreboard -->
    <div class="score-board">
      <div class="player">
        <h3>{{ player1Name }}</h3>
        <p class="score">{{ player1Score }}</p>
        <p class="controls">{{ t('pong.game.controls') }}: F / S</p>
      </div>
      <div class="player">
        <h3>{{ player2Name }}</h3>
        <p class="score">{{ player2Score }}</p>
        <p class="controls">{{ t('pong.game.controls') }}: ↑ / ↓</p>
      </div>
    </div>

    <!-- Overlays -->
    <div v-if="gamePhase === 'menu'" class="game-overlay">
      <div class="overlay-content">
        <h3>{{ t('pong.game.ready') }}</h3>
        <button @click="$emit('start-game')" class="overlay-button">
          {{ t('pong.game.startGame') }}
        </button>
      </div>
    </div>

    <div v-if="gamePhase === 'countdown'" class="game-overlay">
      <div class="overlay-content">
        <h2>{{ t('pong.game.countdown') }} {{ countdownValue }}...</h2>
      </div>
    </div>

    <div v-if="gamePhase === 'over'" class="game-overlay">
      <div class="overlay-content">
        <h2>{{ t('pong.game.matchOver') }}</h2>
        <p>{{ t('pong.game.winner') }}: {{ winner }}</p>
        <button @click="$emit('close-match')" class="overlay-button">
          {{ t('pong.game.close') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  canvasWidth: {
    type: Number,
    default: 800
  },
  canvasHeight: {
    type: Number,
    default: 400
  },
  player1Name: {
    type: String,
    required: true
  },
  player2Name: {
    type: String,
    required: true
  },
  player1Score: {
    type: Number,
    required: true
  },
  player2Score: {
    type: Number,
    required: true
  },
  gamePhase: {
    type: String,
    required: true
  },
  countdownValue: {
    type: Number,
    default: 3
  },
  winner: {
    type: String,
    default: ''
  }
})

defineEmits(['start-game', 'close-match'])

const canvas = ref(null)

onMounted(() => {
  // Initialisation du canvas si nécessaire
  const ctx = canvas.value.getContext('2d')
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--background-color')
  ctx.fillRect(0, 0, props.canvasWidth, props.canvasHeight)
})

defineExpose({
  canvas
})
</script>

<style scoped>
.game-container {
  position: relative;
}

canvas {
  border: 2px solid var(--primary-color);
  background: var(--background-color);
}

.score-board {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}

.player {
  text-align: center;
  width: 150px;
  background: var(--background-color);
  padding: 10px;
  border-radius: 6px;
  border: 1px solid var(--primary-color);
}

.score {
  font-size: 24px;
  color: var(--success-color);
}

.controls {
  font-size: 14px;
  color: var(--text-color);
}

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
  padding: 20px;
  border-radius: 6px;
  border: 1px solid var(--primary-color);
  color: var(--text-color);
  text-align: center;
}

.overlay-button {
  padding: 10px 20px;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

.overlay-button:hover {
  background: var(--primary-hover-color);
}
</style>
