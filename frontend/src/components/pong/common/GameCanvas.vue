<template>
  <div class="game-canvas-container">
    <canvas
      ref="canvas"
      class="game-canvas"
      :width="canvasWidth"
      :height="canvasHeight"
    ></canvas>

    <!-- Scoreboard -->
    <div class="score-board">
      <div class="player">
        <h3 class="name">{{ player1Name }}</h3>
        <p class="score">{{ player1Score }}</p>
        <p class="controls">{{ t('pong.game.controls') }}: W / S</p>
      </div>
      <div class="player">
        <h3 class="name">{{ player2Name }}</h3>
        <p class="score">{{ player2Score }}</p>
        <p class="controls">{{ t('pong.game.controls') }}: ↑ / ↓</p>
      </div>
    </div>

    <!-- Menu overlay -->
    <div v-if="gamePhase === 'menu'" class="overlay">
      <slot name="menu-overlay">
        <div class="menu-content">
          <h3>{{ t('pong.game.ready') }}</h3>
          <button @click="$emit('start-game')" class="start-button">
            {{ t('pong.game.startGame') }}
          </button>
        </div>
      </slot>
    </div>

    <!-- Countdown overlay -->
    <div v-if="gamePhase === 'countdown'" class="overlay">
      <div class="countdown">{{ countdownValue }}</div>
    </div>

    <!-- Game over overlay -->
    <div v-if="gamePhase === 'over'" class="overlay">
      <div class="game-over">
        <h3 class="winner">{{ t('pong.game.winner') }} {{ winner }}</h3>
        <p class="score">
          {{ t('catch.score') }} : {{ player1Score }} - {{ player2Score }}
        </p>
        <button @click="$emit('close-match')" class="close-button">
          {{ t('pong.game.close') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  canvasWidth: {
    type: Number,
    default: 800,
  },
  canvasHeight: {
    type: Number,
    default: 450,
  },
  gamePhase: {
    type: String,
    required: true,
  },
  countdownValue: {
    type: Number,
    required: true,
  },
  winner: {
    type: String,
    default: '',
  },
  player1Name: {
    type: String,
    required: true,
  },
  player2Name: {
    type: String,
    required: true,
  },
  player1Score: {
    type: Number,
    required: true,
  },
  player2Score: {
    type: Number,
    required: true,
  },
})

defineEmits(['start-game', 'close-match'])

const canvas = ref(null)

onMounted(() => {
  if (canvas.value) {
    canvas.value.focus()
  }
  const ctx = canvas.value.getContext('2d')
  ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue(
    '--background-color'
  )
  ctx.fillRect(0, 0, props.canvasWidth, props.canvasHeight)
})

defineExpose({
  canvas,
})
</script>

<style scoped>
.game-canvas-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  aspect-ratio: 16 / 9;
  animation: fadeInUp 0.6s ease;
}

.game-canvas {
  width: 100%;
  height: 100%;
  background: var(--background-color);
  border: 2px solid var(--primary-color);
  border-radius: 10px;
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.game-canvas:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px var(--primary-shadow-color);
}

.score-board {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  animation: fadeInUp 0.6s ease backwards;
}

.player {
  text-align: center;
  width: 150px;
  background: var(--background-secondary-color);
  padding: 10px;
  border-radius: 10px;
  border: 1px solid var(--primary-color);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
  transition: transform 0.3s ease;
}

.player:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

.score {
  font-size: 24px;
  color: var(--success-color);
}

.controls {
  font-size: 14px;
  color: var(--text-color);
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 10px;
  animation: fadeIn 0.6s ease;
}

.menu-content,
.game-over {
  background: var(--background-secondary-color);
  padding: 2rem;
  border-radius: 10px;
  border: 2px solid var(--primary-color);
  text-align: center;
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

.countdown {
  font-size: 6rem;
  font-weight: bold;
  color: var(--primary-color);
  text-shadow: 0 0 15px var(--primary-color);
}

.start-button,
.close-button {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: var(--text-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.start-button:hover,
.close-button:hover {
  transform: translateY(-5px);
  background: var(--background-hover-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

.name {
  color: var(--primary-color);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.winner {
  color: var(--success-color);
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.score {
  color: var(--text-color);
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
