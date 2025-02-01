<template>
  <div
    class="game-container"
    tabindex="0"
    ref="gameContainer"
    @keydown="handleKeyPress"
    @keyup="handleKeyUp"
  >
    <div class="game-wrapper">
      <div class="left-container">
        <div class="player-name">{{ playerUsername }}</div>
        <div class="scores-container">
          <div class="player-score">
            Exam {{ formatScore(mouseScore) }}
          </div>
          <div class="player-score">
            Pace {{(catScore) }}
          </div>
        </div>
      </div>
      <div
        class="game-board"
        :class="{ blurred: !gameStarted || gameOver }"
        :style="{ width: boardWidth + 'px', height: boardHeight + 'px' }"
      >
        <img :src="playerIconImage" class="mouse" :style="mouseStyle" />
        <img src="@/assets/blackhole.png" class="cat" :style="catStyle" />
        <img src="@/assets/succes.png" class="cheese" :style="cheeseStyle" />
        <div v-if="isPaused" class="pause-message">
          {{ $t('catch.capture') }} 🎯
        </div>
        <div v-if="!gameStarted || gameOver" class="overlay"></div>
        <div v-if="!gameStarted || gameOver" class="start-message">
          <div v-if="gameOver">
            <div class="game-over-text">{{ $t('catch.gameOver') }}</div>
            <div class="game-over-text">{{ winner }}</div>
          </div>
          <button @click="startCountdown" class="start-btn">
            {{ $t('catch.newGame') }}
          </button>
          <div v-if="!gameStarted && !gameOver" class="controls-info">
            <p>{{ $t('catch.mouseControls') }}: WSAD</p>
            <p>{{ $t('catch.catControls') }}: {{ $t('catch.numpad') }} 8456</p>
          </div>
        </div>
        <div v-if="countdown > 0" class="countdown">{{ countdown }}</div>
      </div>
      <div class="player-info">
        <div class="player-name">{{ guestUsername }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import jerry from '../../assets/jerry.png'
import gamian from '../../assets/gamian.png'
import thomian from '../../assets/thomian.png'
import damian from '../../assets/damian.png'
import { useRoute } from 'vue-router'
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import eventBus from '../../utils/eventBus'

export default {
  setup() {
    const authStore = useAuthStore()
    const { t } = useI18n()
    return { authStore, t }
  },
  name: 'CatAndMouseGame',
  props: {
    playerUsername: {
      type: String,
      default: 'Joueur',
    },
    guestUsername: {
      type: String,
      required: true,
    },
    playerIcon: {
      type: String,
      default: 'gamian'
    },
    mode: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      jerryImage: jerry,
      boardWidth: 960,
      boardHeight: 560,
      mousePos: { x: 40, y: 40 },
      catPos: { x: 900, y: 500 },
      cheesePos: null,
      mouseScore: 2,
      catScore: 8,
      gameOver: false,
      gameStarted: false,
      gameLoop: null,
      mouseSpeed: 12,
      catSpeed: 1,
      catchDistance: 30,
      timer: null,
      winner: '',
      pressedKeys: new Set(),
      isPaused: false,
      countdown: 0,
      isOvertime: false,
      walls: [
        { x: 240, y: 150, width: 8, height: 240 },
        { x: 720, y: 150, width: 8, height: 240 },
      ],
    }
  },
  computed: {
    playerIconImage() {
      const iconMap = {
        gamian,
        thomian,
        damian
      }
      return iconMap[this.playerIcon] || jerry
    },
    mouseStyle() {
      return {
        left: this.mousePos.x + 'px',
        top: this.mousePos.y + 'px',
      }
    },
    catStyle() {
      return {
        left: this.catPos.x + 'px',
        top: this.catPos.y + 'px',
      }
    },
    cheeseStyle() {
      if (!this.cheesePos) return {}
      return {
        left: this.cheesePos.x + 'px',
        top: this.cheesePos.y + 'px',
      }
    },
  },
  methods: {
    formatScore(score) {
      return score < 10 ? `0${score}` : score
    },
    handleKeyPress(event) {
      this.pressedKeys.add(event.key.toLowerCase())
    },
    handleKeyUp(event) {
      this.pressedKeys.delete(event.key.toLowerCase())
    },
    checkWallCollision(pos) {
      return false
    },
    updatePositions() {
      if (
        this.gameOver ||
        this.isPaused ||
        !this.gameStarted ||
        this.countdown != null
      )
        return

      let newMouseX = this.mousePos.x
      let newMouseY = this.mousePos.y
      const spriteSize = 15
      let mouseMove = { x: 0, y: 0 }

      if (this.pressedKeys.has('w')) {
        newMouseY = Math.max(spriteSize, this.mousePos.y - this.mouseSpeed)
        mouseMove.y = -this.mouseSpeed
      }
      if (this.pressedKeys.has('s')) {
        newMouseY = Math.min(
          this.boardHeight - spriteSize,
          this.mousePos.y + this.mouseSpeed
        )
        mouseMove.y = this.mouseSpeed
      }
      if (this.pressedKeys.has('a')) {
        newMouseX = Math.max(spriteSize, this.mousePos.x - this.mouseSpeed)
        mouseMove.x = -this.mouseSpeed
      }
      if (this.pressedKeys.has('d')) {
        newMouseX = Math.min(
          this.boardWidth - spriteSize,
          this.mousePos.x + this.mouseSpeed
        )
        mouseMove.x = this.mouseSpeed
      }

      let newCatX = this.catPos.x
      let newCatY = this.catPos.y
      let catMove = { x: 0, y: 0 }

      if (this.pressedKeys.has('8')) {
        newCatY = Math.max(spriteSize, this.catPos.y - this.catSpeed)
        catMove.y = -this.catSpeed
      }
      if (this.pressedKeys.has('5')) {
        newCatY = Math.min(
          this.boardHeight - spriteSize,
          this.catPos.y + this.catSpeed
        )
        catMove.y = this.catSpeed
      }
      if (this.pressedKeys.has('4')) {
        newCatX = Math.max(spriteSize, this.catPos.x - this.catSpeed)
        catMove.x = -this.catSpeed
      }
      if (this.pressedKeys.has('6')) {
        newCatX = Math.min(
          this.boardWidth - spriteSize,
          this.catPos.x + this.catSpeed
        )
        catMove.x = this.catSpeed
      }

      if (!this.checkWallCollision({ x: newMouseX, y: newMouseY })) {
        this.mousePos = { x: newMouseX, y: newMouseY }
      } else {
        this.mousePos = {
          x: Math.max(
            spriteSize,
            Math.min(
              this.mousePos.x - mouseMove.x * 3.5,
              this.boardWidth - spriteSize
            )
          ),
          y: Math.max(
            spriteSize,
            Math.min(
              this.mousePos.y - mouseMove.y * 3.5,
              this.boardHeight - spriteSize
            )
          ),
        }
      }

      if (!this.checkWallCollision({ x: newCatX, y: newCatY })) {
        this.catPos = { x: newCatX, y: newCatY }
      } else {
        this.catPos = {
          x: Math.max(
            spriteSize,
            Math.min(
              this.catPos.x - catMove.x * 3.5,
              this.boardWidth - spriteSize
            )
          ),
          y: Math.max(
            spriteSize,
            Math.min(
              this.catPos.y - catMove.y * 3.5,
              this.boardHeight - spriteSize
            )
          ),
        }
      }

      this.checkCheeseCollection()

      const dx = this.mousePos.x - this.catPos.x
      const dy = this.mousePos.y - this.catPos.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < this.catchDistance) {
        this.catScore+=8
        if (this.isOvertime) {
          this.endGame('cat')
          return
        }
        this.isPaused = true
        this.resetPositions()
        this.spawnCheese()
        setTimeout(() => {
          this.isPaused = false
        }, 3000)
      }
    },
    spawnCheese() {
      const margin = 30;
      let newPos;
      do {
        newPos = {
          x: margin + Math.random() * (this.boardWidth - 2 * margin),
          y: margin + Math.random() * (this.boardHeight - 2 * margin),
        };
      } while (this.checkWallCollision(newPos));

      this.cheesePos = newPos;
    },
    checkCheeseCollection() {
      if (!this.cheesePos) return;

      const dx = this.mousePos.x - this.cheesePos.x;
      const dy = this.mousePos.y - this.cheesePos.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 30) {
        this.mouseScore++;
        if (this.mouseScore >= 7) {
          this.mouseScore = 6;
          this.endGame('mouse');
          return;
        }
        this.cheesePos = null;
        this.spawnCheese();
      }
    },
    resetPositions() {
      this.mousePos = { x: 40, y: 40 }
      this.catPos = { x: 900, y: 500 }
    },
    async saveGameHistory() {
      try {
        const historyData = {
          user: this.authStore.user.id,
          guest_name: this.guestUsername,
          user_score: this.mouseScore,
          guest_score: this.catScore,
          played_at: new Date().toISOString(),
          game_name: 'catch',
        }

        await axios.post('/users/histories/add', historyData, {
          withCredentials: true,
        })
        console.log('history saved')
      } catch (error) {
        console.error('Error saving game history:', error)
      }
    },
    startGame() {
      this.spawnCheese()
      this.gameLoop = setInterval(this.updatePositions, 20)
      this.$refs.gameContainer.focus()
    },
    endGame(winner) {
      this.gameStarted = false
      this.gameOver = true
      if (this.gameLoop) {
        clearInterval(this.gameLoop)
        this.gameLoop = null
      }

      if (winner === 'cat') {
        this.winner = `${this.guestUsername} gagne!`
      } else {
        this.winner = 'Félicitations, vous avez terminé le tronc commun !'
      }

      this.saveGameHistory()
    },
    startNewGame() {
      this.gameStarted = true
      this.mousePos = { x: 40, y: 40 }
      this.catPos = { x: 900, y: 500 }
      this.mouseScore = 2
      this.catScore = 8
      this.gameOver = false
      this.winner = ''
      this.pressedKeys.clear()
      this.isOvertime = false
      this.startGame()
    },
    startCountdown() {
      this.startNewGame()
      this.countdown = 3
      const countInterval = setInterval(() => {
        this.countdown--
        if (this.countdown === 0) {
          clearInterval(countInterval)
          setTimeout(() => {
            this.countdown = null
          })
        }
      }, 1000)
    },
  },
  mounted() {},
  beforeDestroy() {
    if (this.gameLoop) {
      clearInterval(this.gameLoop)
    }
    window.removeEventListener('keydown', this.handleKeyPress)
    window.removeEventListener('keyup', this.handleKeyUp)
  },
}
</script>

<style scoped>
.game-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px;
  position: relative;
}

.game-wrapper {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: center;
  gap: 20px;
}

.left-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-right: 20px;
  align-items: center;
}

.player-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.player-name {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-width: 150px;
  text-align: center;
}

.scores-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.player-score {
  font-size: 20px;
  color: #2c3e50;
  font-weight: bold;
  padding: 8px 6px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 120px;
  text-align: center;
}

.game-info {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-top: 20px;
}

.game-board {
  position: relative;
  background-color: #f2ddc3;
  background-image: linear-gradient(
      90deg,
      rgba(139, 69, 19, 0.02) 50%,
      transparent 50%
    ),
    linear-gradient(90deg, rgba(139, 69, 19, 0.03) 50%, transparent 50%),
    linear-gradient(90deg, transparent 50%, rgba(139, 69, 19, 0.04) 50%),
    linear-gradient(90deg, transparent 50%, rgba(139, 69, 19, 0.05) 50%);
  background-size: 13px, 29px, 37px, 53px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(101, 67, 33, 0.1);
  overflow: hidden;
}

.game-board.blurred .mouse,
.game-board.blurred .cat,
.game-board.blurred .cheese {
  filter: blur(5px);
}

.mouse,
.cat {
  position: absolute;
  width: 30px;
  height: 30px;
  transform: translate(-50%, -50%);
  transition: all 0.05s linear;
  object-fit: contain;
}

.mouse {
  z-index: 2;
}

.cat {
  z-index: 1;
}

.cheese {
  position: absolute;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  user-select: none;
  transition: all 0.05s linear;
}

.game-over-text {
  color: #e74c3c;
  font-size: 24px;
  margin-bottom: 10px;
  font-weight: bold;
}

.start-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  width: 100%;
  z-index: 2;
}

.start-btn {
  background-color: #2ecc71;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 5px;
  font-size: 20px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background-color 0.3s;
}

.start-btn:hover {
  background-color: #27ae60;
}

.controls-info {
  font-size: 16px;
  color: #7f8c8d;
  margin-top: 20px;
}

.controls-info p {
  margin: 5px 0;
}

.wall {
  position: absolute;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.wall.horizontal {
  height: 10px;
  background-color: #34495e;
  opacity: 0;
}

.wall.vertical {
  width: 15px;
  background-color: #c0392b;
  background-image: linear-gradient(
    0deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.2) 10%,
    rgba(255, 255, 255, 0.1) 20%,
    rgba(255, 255, 255, 0.05) 100%
  );
  box-shadow:
    2px 0 5px rgba(0, 0, 0, 0.1),
    inset -1px 0 3px rgba(0, 0, 0, 0.2);
}

.pause-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  color: #e74c3c;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  animation: bounce 0.5s ease infinite alternate;
}

@keyframes bounce {
  from {
    transform: translate(-50%, -50%) scale(1);
  }
  to {
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.countdown {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 72px;
  color: #e74c3c;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  animation: popIn 0.5s ease-out;
}

@keyframes popIn {
  0% {
    transform: translate(-50%, -50%) scale(0.5);
    opacity: 0;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  z-index: 1;
}

.timer-container {
  margin-top: 20px;
  text-align: center;
}

.timer {
  font-size: 20px;
  color: #e67e22;
  font-weight: bold;
  padding: 8px 20px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
