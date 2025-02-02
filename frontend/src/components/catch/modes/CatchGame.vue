<template>
  <div class="game-container" tabindex="0" ref="gameContainer" @keydown="handleKeyPress" @keyup="handleKeyUp">
    <div class="game-wrapper">
      <!-- Colonne joueur 1 -->
      <div class="player-column">
        <div class="player-name">{{ playerUsername }}</div>
        <div v-if="gameStarted || gameOver" class="player-score">
          {{ $t('catch.score') }}: {{ mouseScore }}
        </div>
      </div>
      
      <div class="game-board" :class="{ blurred: !gameStarted || gameOver }" :style="{ width: boardWidth + 'px', height: boardHeight + 'px' }">
        <!-- Traînées des personnages -->
        <div v-for="(pos, index) in mouseTrail" :key="'mouse-trail-' + index" 
             class="trail-dot mouse-trail-dot" 
             :style="{
               left: pos.x + 'px',
               top: pos.y + 'px',
               opacity: (1 - index / mouseTrail.length) * 0.7,
               transform: `scale(${1 - index / mouseTrail.length})`,
               filter: `blur(${index * 0.15}px)`
             }">
          <div class="trail-inner"></div>
        </div>
        <div v-for="(pos, index) in catTrail" :key="'cat-trail-' + index" 
             class="trail-dot cat-trail-dot" 
             :style="{
               left: pos.x + 'px',
               top: pos.y + 'px',
               opacity: (1 - index / catTrail.length) * 0.7,
               transform: `scale(${1 - index / catTrail.length})`,
               filter: `blur(${index * 0.15}px)`
             }">
          <div class="trail-inner"></div>
        </div>
        
        <img :src="jerryImage" class="mouse" :style="mouseStyle" />
        <img :src="tomImage" class="cat" :style="catStyle" />
        <div v-if="cheesePos" class="cheese" :style="cheeseStyle">🧀</div>
        <div class="wall vertical" :style="{ left: '240px', top: '150px', height: '240px', width: '8px' }"></div>
        <div class="wall vertical" :style="{ left: '720px', top: '150px', height: '240px', width: '8px' }"></div>
        <div v-if="isPaused" class="pause-message">
          {{ $t('catch.capture') }} 🎯
        </div>
        <div v-if="isOvertime && showOvertimeMessage" class="pause-message center-message">
          {{ $t('catch.overtime') }} 🔥
        </div>
        <div v-if="countdown > 0" class="countdown">{{ countdown }}</div>
      </div>
  
      <!-- Déplacé en dehors du game-board -->
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
  
      <!-- Colonne joueur 2 -->
      <div class="player-column">
        <div class="player-name">{{ guestUsername }}</div>
        <div v-if="gameStarted || gameOver" class="player-score">
          {{ $t('catch.score') }}: {{ catScore }}
        </div>
      </div>
    </div>
    
    <div v-if="gameStarted" class="timer-container">
      <div class="timer">
        {{ gameOver ? $t('catch.timeElapsed') : $t('catch.timeRemaining', { time: timeLeft }) }}
      </div>
    </div>
  </div>
</template>

<script>
import jerry from '@/assets/jerry.png'
import tom from '@/assets/tom.png'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

export default {
  setup() {
    const authStore = useAuthStore()
    const { t } = useI18n()
    return { authStore, t }
  },
  name: 'CatchGame',
  props: {
    playerUsername: {
      type: String,
      default: 'Joueur',
    },
    guestUsername: {
      type: String,
      default: 'Invité',
    },
  },
  data() {
    return {
      jerryImage: jerry,
      tomImage: tom,
      boardWidth: 960,
      boardHeight: 560,
      mousePos: { x: 40, y: 40 },
      catPos: { x: 900, y: 500 },
      mouseTrail: [],
      catTrail: [],
      trailLength: 12,
      lastMouseMove: Date.now(),
      lastCatMove: Date.now(),
      cheesePos: null,
      mouseScore: 0,
      catScore: 0,
      gameOver: false,
      gameStarted: false,
      gameLoop: null,
      mouseSpeed: 12,
      catSpeed: 12,
      catchDistance: 30,
      timeLeft: 40,
      timer: null,
      winner: '',
      pressedKeys: new Set(),
      isPaused: false,
      countdown: 0,
      isOvertime: false,
      showOvertimeMessage: false,
      walls: [
        { x: 240, y: 150, width: 8, height: 240 },
        { x: 720, y: 150, width: 8, height: 240 },
      ],
    }
  },
  computed: {
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
    handleKeyPress(event) {
      this.pressedKeys.add(event.key.toLowerCase())
    },
    handleKeyUp(event) {
      this.pressedKeys.delete(event.key.toLowerCase())
    },
    checkWallCollision(pos) {
      const playerSize = 25
      const collisionMargin = 5

      // Vérifier les collisions avec les murs verticaux (avec effet de glissade)
      for (const wall of this.walls) {
        const wallBox = {
          left: wall.x - collisionMargin,
          right: wall.x + wall.width + collisionMargin,
          top: wall.y,
          bottom: wall.y + wall.height
        }

        const playerBox = {
          left: pos.x,
          right: pos.x + playerSize,
          top: pos.y,
          bottom: pos.y + playerSize
        }

        if (playerBox.right > wallBox.left && 
            playerBox.left < wallBox.right && 
            playerBox.bottom > wallBox.top && 
            playerBox.top < wallBox.bottom) {
          // Déterminer de quel côté du mur on est
          const fromLeft = Math.abs(playerBox.right - wallBox.left) < Math.abs(playerBox.left - wallBox.right)
          return { type: 'wall', fromLeft }
        }
      }

      // Vérifier les collisions avec les bords du plateau (sans effet de glissade)
      if (pos.x < 0 || pos.x + playerSize > this.boardWidth || 
          pos.y < 0 || pos.y + playerSize > this.boardHeight) {
        return { type: 'border' }
      }

      return false
    },
    updatePositions() {
      if (this.isPaused || this.showOvertimeMessage) return
      if (this.gameOver || !this.gameStarted || this.countdown != null) return

      const now = Date.now()
      
      // Nettoyer les traînées si les personnages sont immobiles depuis un moment
      if (now - this.lastMouseMove > 50 && this.mouseTrail.length > 0) {
        this.mouseTrail.pop()
      }
      if (now - this.lastCatMove > 50 && this.catTrail.length > 0) {
        this.catTrail.pop()
      }

      let newMouseX = this.mousePos.x
      let newMouseY = this.mousePos.y
      const spriteSize = 15
      let mouseMove = { x: 0, y: 0 }

      if (this.pressedKeys.has('w')) {
        newMouseY = Math.max(spriteSize, this.mousePos.y - this.mouseSpeed)
        mouseMove.y = -this.mouseSpeed
      }
      if (this.pressedKeys.has('s')) {
        newMouseY = Math.min(this.boardHeight - spriteSize, this.mousePos.y + this.mouseSpeed)
        mouseMove.y = this.mouseSpeed
      }
      if (this.pressedKeys.has('a')) {
        newMouseX = Math.max(spriteSize, this.mousePos.x - this.mouseSpeed)
        mouseMove.x = -this.mouseSpeed
      }
      if (this.pressedKeys.has('d')) {
        newMouseX = Math.min(this.boardWidth - spriteSize, this.mousePos.x + this.mouseSpeed)
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
        newCatY = Math.min(this.boardHeight - spriteSize, this.catPos.y + this.catSpeed)
        catMove.y = this.catSpeed
      }
      if (this.pressedKeys.has('4')) {
        newCatX = Math.max(spriteSize, this.catPos.x - this.catSpeed)
        catMove.x = -this.catSpeed
      }
      if (this.pressedKeys.has('6')) {
        newCatX = Math.min(this.boardWidth - spriteSize, this.catPos.x + this.catSpeed)
        catMove.x = this.catSpeed
      }

      // Mise à jour de la position de la souris
      const mouseCollision = this.checkWallCollision({ x: newMouseX, y: newMouseY })
      if (!mouseCollision) {
        if (this.mousePos.x !== newMouseX || this.mousePos.y !== newMouseY) {
          this.lastMouseMove = now
          this.mouseTrail.unshift({
            x: this.mousePos.x + 12,
            y: this.mousePos.y + 12,
            speed: Math.sqrt(Math.pow(mouseMove.x, 2) + Math.pow(mouseMove.y, 2))
          })
          if (this.mouseTrail.length > this.trailLength) {
            this.mouseTrail.pop()
          }
        }
        this.mousePos = { x: newMouseX, y: newMouseY }
      } else if (mouseCollision.type === 'wall') {
        this.mousePos = {
          x: mouseCollision.fromLeft ? this.mousePos.x : this.mousePos.x,
          y: newMouseY
        }
      }

      // Mise à jour de la position du chat
      const catCollision = this.checkWallCollision({ x: newCatX, y: newCatY })
      if (!catCollision) {
        if (this.catPos.x !== newCatX || this.catPos.y !== newCatY) {
          this.lastCatMove = now
          this.catTrail.unshift({
            x: this.catPos.x + 12,
            y: this.catPos.y + 12,
            speed: Math.sqrt(Math.pow(catMove.x, 2) + Math.pow(catMove.y, 2))
          })
          if (this.catTrail.length > this.trailLength) {
            this.catTrail.pop()
          }
        }
        this.catPos = { x: newCatX, y: newCatY }
      } else if (catCollision.type === 'wall') {
        this.catPos = {
          x: catCollision.fromLeft ? this.catPos.x : this.catPos.x,
          y: newCatY
        }
      }

      this.checkCheeseCollection()

      const dx = this.mousePos.x - this.catPos.x
      const dy = this.mousePos.y - this.catPos.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < this.catchDistance) {
        this.catScore++
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
      const margin = 30
      const minDistanceFromMouse = 300
      const minDistanceFromCat = 200
      const minDistanceFromWalls = 80
      // Position des murs verticaux
      const leftWallX = 240
      const rightWallX = 720
      
      let newPos
      let distanceFromMouse
      let distanceFromCat
      let distanceFromLeftWall
      let distanceFromRightWall
      
      do {
        newPos = {
          x: margin + Math.random() * (this.boardWidth - 2 * margin),
          y: margin + Math.random() * (this.boardHeight - 2 * margin),
        }
        
        // Calculate distances from mouse and cat
        distanceFromMouse = Math.sqrt(
          Math.pow(newPos.x - this.mousePos.x, 2) + 
          Math.pow(newPos.y - this.mousePos.y, 2)
        )
        
        distanceFromCat = Math.sqrt(
          Math.pow(newPos.x - this.catPos.x, 2) + 
          Math.pow(newPos.y - this.catPos.y, 2)
        )

        // Calculate distances from middle walls
        distanceFromLeftWall = Math.abs(newPos.x - leftWallX)
        distanceFromRightWall = Math.abs(newPos.x - rightWallX)

      } while (
        this.checkWallCollision(newPos) || 
        distanceFromMouse < minDistanceFromMouse ||
        distanceFromCat < minDistanceFromCat ||
        distanceFromLeftWall < minDistanceFromWalls ||
        distanceFromRightWall < minDistanceFromWalls
      )

      this.cheesePos = newPos
    },
    checkCheeseCollection() {
      if (!this.cheesePos) return

      const dx = this.mousePos.x - this.cheesePos.x
      const dy = this.mousePos.y - this.cheesePos.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < 30) {
        this.mouseScore++
        if (this.isOvertime) {
          this.endGame('mouse')
          return
        }
        this.cheesePos = null
        setTimeout(() => {
          this.spawnCheese()
        }, 1500)
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
      this.timer = setInterval(this.updateTimer, 1000)
      this.$refs.gameContainer.focus()
    },
    updateTimer() {
      if (this.timeLeft > 0 && !this.isPaused && this.gameStarted) {
        this.timeLeft--
      } else if (this.timeLeft <= 0 && !this.isPaused && this.gameStarted) {
        if (this.mouseScore === this.catScore) {
          this.isOvertime = true
          this.showOvertimeMessage = true
          setTimeout(() => {
            this.showOvertimeMessage = false
          }, 3000) // Le message disparaît après 3 secondes
        } else {
          this.endGame(this.mouseScore > this.catScore ? 'mouse' : 'cat')
        }
      }
    },
    endGame(winner) {
      this.gameStarted = false
      this.gameOver = true
      if (this.gameLoop) {
        clearInterval(this.gameLoop)
        this.gameLoop = null
      }
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }

      if (winner === 'cat') {
        this.winner = `${this.guestUsername} ${this.$t('catch.victory')}`
      } else {
        this.winner = `${this.playerUsername} ${this.$t('catch.victory')}`
      }

      this.saveGameHistory()
    },
    startNewGame() {
      this.gameStarted = true
      this.mousePos = { x: 40, y: 40 }
      this.catPos = { x: 900, y: 500 }
      this.mouseScore = 0
      this.catScore = 0
      this.timeLeft = 40
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
    if (this.timer) {
      clearInterval(this.timer)
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
  animation: fadeIn 0.6s ease;
}

.game-wrapper {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: center;
  gap: 20px;
}

.player-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  animation: slideIn 0.6s ease;
}

.player-name {
  font-size: 24px;
  font-weight: 800;
  color: var(--primary-color);
  padding: 15px;
  background: var(--surface-color);
  border: 2px solid var(--primary-color);
  border-radius: 12px;
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  min-width: 150px;
  text-align: center;
  transition: transform 0.3s ease;
}

.player-name:hover {
  transform: translateY(-2px);
}

.player-score {
  font-size: 20px;
  color: var(--text-color);
  font-weight: bold;
  padding: 12px 20px;
  background: var(--surface-color);
  border: 2px solid var(--primary-color);
  border-radius: 10px;
  box-shadow: 0 5px 15px var(--primary-shadow-color);
  transition: all 0.3s ease;
}

.game-board {
  position: relative;
  background: linear-gradient(
    135deg,
    var(--background-color) 0%,
    var(--background-secondary-color) 100%
  );
  border: 3px solid var(--primary-color);
  border-radius: 15px;
  box-shadow: 0 10px 30px var(--primary-shadow-color);
  overflow: hidden;
  transition: all 0.3s ease;
}

.game-board.blurred {
  filter: blur(5px);
  transform: scale(0.98);
}

.mouse, .cat {
  position: absolute;
  width: 35px;
  height: 35px;
  transform: translate(-50%, -50%);
  transition: all 0.05s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.cheese {
  position: absolute;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  user-select: none;
  transition: all 0.3s ease;
  animation: float 3s ease-in-out infinite;
}

.wall.vertical {
  position: absolute;
  background: linear-gradient(
    to right,
    var(--primary-color),
    var(--primary-hover-color)
  );
  box-shadow: 
    0 0 15px var(--primary-shadow-color),
    inset 0 0 5px rgba(255, 255, 255, 0.3);
  border-radius: 8px;
}

.start-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  width: 20%;
  z-index: 2;
  animation: fadeIn 0.6s ease;
}

.start-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover-color));
  color: white;
  border: none;
  padding: 15px 35px;
  border-radius: 12px;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px var(--primary-shadow-color);
  position: relative;
  overflow: hidden;
}

.start-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

.start-btn::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.start-btn:hover::after {
  opacity: 1;
}

.controls-info {
  font-size: 16px;
  color: var(--text-color);
  margin-top: 20px;
  background: var(--surface-color);
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.pause-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  color: var(--primary-color);
  font-weight: bold;
  text-shadow: 0 0 15px var(--primary-shadow-color);
  animation: bounce 0.5s ease infinite alternate;
}

.center-message {
  left: 480px;
  width: 440px;
  text-align: center;
  color: var(--primary-color);
  font-size: 36px;
}

.countdown {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 72px;
  color: var(--primary-color);
  font-weight: 800;
  text-shadow: 0 0 20px var(--primary-shadow-color);
  animation: popIn 0.5s ease-out;
}

.timer {
  font-size: 20px;
  color: var(--primary-color);
  font-weight: bold;
  padding: 12px 25px;
  background: var(--surface-color);
  border: 2px solid var(--primary-color);
  border-radius: 10px;
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

.game-over-text {
  font-size: 32px;
  font-weight: 800;
  color: var(--primary-color);
  margin-bottom: 20px;
  text-shadow: 0 0 15px var(--primary-shadow-color);
  animation: fadeInScale 0.6s ease;
  padding: 15px 30px;
  background: var(--surface-color);
  border: 2px solid var(--primary-color);
  border-radius: 12px;
  box-shadow: 0 8px 25px var(--primary-shadow-color);
}

.start-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  background: var(--background-color);
  padding: 30px;
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  z-index: 100;
  min-width: 300px;
  backdrop-filter: blur(0);
  -webkit-backdrop-filter: blur(0);
}

@keyframes fadeInScale {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Ajuster le style du bouton pour qu'il s'aligne bien avec le message */
.start-message .start-btn {
  margin-top: 20px;
  min-width: 200px;
}

/* Style pour le conteneur des textes de fin de partie */
.game-over-text + .game-over-text {
  margin-top: 10px;
  font-size: 28px;
  color: var(--text-color);
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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

@keyframes bounce {
  from { transform: translate(-50%, -50%) scale(1); }
  to { transform: translate(-50%, -50%) scale(1.1); }
}

@media (max-width: 768px) {
  .game-wrapper {
    flex-direction: column;
    align-items: center;
  }

  .player-column {
    flex-direction: row;
    gap: 10px;
  }

  .player-name, .player-score {
    font-size: 16px;
    padding: 8px 15px;
  }

  .countdown {
    font-size: 48px;
  }
}

.trail-dot {
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  pointer-events: none;
  transition: all 0.15s ease;
}

.trail-inner {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle at center, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 70%);
}

.mouse-trail-dot {
  background: radial-gradient(circle at center, #4a90e2 0%, rgba(74,144,226,0) 70%);
  box-shadow: 
    0 0 4px #4a90e2,
    0 0 6px rgba(74,144,226,0.6),
    inset 0 0 2px rgba(255,255,255,0.5);
}

.cat-trail-dot {
  background: radial-gradient(circle at center, #e25c4a 0%, rgba(226,92,74,0) 70%);
  box-shadow: 
    0 0 4px #e25c4a,
    0 0 6px rgba(226,92,74,0.6),
    inset 0 0 2px rgba(255,255,255,0.5);
}
</style>