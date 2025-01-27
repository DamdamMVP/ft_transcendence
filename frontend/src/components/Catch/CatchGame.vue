<template>
  <div class="game-container" tabindex="0" @keydown="handleKeyPress" @keyup="handleKeyUp" ref="gameContainer">
    <div class="game-board" 
         :style="{ width: boardWidth + 'px', height: boardHeight + 'px' }">
      <div class="mouse" :style="mouseStyle">🐭</div>
      <div class="cat" :style="catStyle">🐱</div>
      <div v-if="cheesePos" class="cheese" :style="cheeseStyle">🧀</div>
      <div class="wall vertical" :style="{ left: '240px', top: '150px', height: '240px', width: '8px' }"></div>
      <div class="wall vertical" :style="{ left: '720px', top: '150px', height: '240px', width: '8px' }"></div>
      <div v-if="isPaused" class="pause-message">Capture ! 🎯</div>
      <div v-if="!gameStarted || gameOver" class="start-message">
        <div v-if="gameOver">
          <div class="game-over-text">Partie terminée!</div>
          <div class="game-over-text">{{ winner }} gagne!</div>
        </div>
        <button @click="startCountdown" class="start-btn">Nouvelle Partie</button>
        <div v-if="!gameStarted && !gameOver" class="controls-info">
          <p>Souris: WSAD</p>
          <p>Chat: Pavé numérique 8456</p>
        </div>
      </div>
      <div v-if="countdown > 0" class="countdown">{{ countdown }}</div>
    </div>
    <div class="game-info">
      <div v-if="!gameOver && gameStarted" class="scores">
        <div class="player-score">Souris: {{ mouseScore }}</div>
        <div class="player-score">Chat: {{ catScore }}</div>
        <div class="timer">Temps: {{ timeLeft }}s</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CatAndMouseGame',
  data() {
    return {
      boardWidth: 960,
      boardHeight: 560,
      mousePos: { x: 40, y: 40 },
      catPos: { x: 900, y: 500 },
      cheesePos: null,
      mouseScore: 0,
      catScore: 0,
      gameOver: false,
      gameStarted: false,
      gameLoop: null,
      moveSpeed: 12,
      catchDistance: 30,
      timeLeft: 5,
      timer: null,
      winner: '',
      pressedKeys: new Set(),
      isPaused: false,
      countdown: 0,
      walls: [
        { x: 240, y: 150, width: 8, height: 240 },  // mur vertical gauche
        { x: 720, y: 150, width: 8, height: 240 }   // mur vertical droit
      ]
    }
  },
  computed: {
    mouseStyle() {
      return {
        left: this.mousePos.x + 'px',
        top: this.mousePos.y + 'px'
      }
    },
    catStyle() {
      return {
        left: this.catPos.x + 'px',
        top: this.catPos.y + 'px'
      }
    },
    cheeseStyle() {
      if (!this.cheesePos) return {}
      return {
        left: this.cheesePos.x + 'px',
        top: this.cheesePos.y + 'px'
      }
    }
  },
  methods: {
    handleKeyPress(event) {
      this.pressedKeys.add(event.key.toLowerCase())
    },
    handleKeyUp(event) {
      this.pressedKeys.delete(event.key.toLowerCase())
    },
    checkWallCollision(pos) {
      const playerSize = 20
      for (const wall of this.walls) {
        // Vérifier si le joueur touche le mur
        if (pos.x < wall.x + wall.width &&
            pos.x + playerSize > wall.x &&
            pos.y < wall.y + wall.height &&
            pos.y + playerSize > wall.y) {
          return true // Collision détectée
        }
      }
      return false
    },
    updatePositions() {
      if (this.gameOver || this.isPaused || !this.gameStarted || this.countdown != null) return

      // Mouvement de la souris (WSAD)
      const mouseMove = { x: 0, y: 0 }
      if (this.pressedKeys.has('w')) mouseMove.y -= (this.moveSpeed)
      if (this.pressedKeys.has('s')) mouseMove.y += (this.moveSpeed)
      if (this.pressedKeys.has('a')) mouseMove.x -= (this.moveSpeed)
      if (this.pressedKeys.has('d')) mouseMove.x += (this.moveSpeed)

      // Mouvement du chat (8456)
      const catMove = { x: 0, y: 0 }
      if (this.pressedKeys.has('8')) catMove.y -= this.moveSpeed
      if (this.pressedKeys.has('5')) catMove.y += this.moveSpeed
      if (this.pressedKeys.has('4')) catMove.x -= this.moveSpeed
      if (this.pressedKeys.has('6')) catMove.x += this.moveSpeed

      // Calculer les nouvelles positions
      const newMousePos = {
        x: Math.max(0, Math.min(this.mousePos.x + mouseMove.x, this.boardWidth - 30)),
        y: Math.max(0, Math.min(this.mousePos.y + mouseMove.y, this.boardHeight - 30))
      }

      const newCatPos = {
        x: Math.max(0, Math.min(this.catPos.x + catMove.x, this.boardWidth - 30)),
        y: Math.max(0, Math.min(this.catPos.y + catMove.y, this.boardHeight - 30))
      }

      // Appliquer les mouvements seulement s'il n'y a pas de collision avec les murs
      if (!this.checkWallCollision(newMousePos)) {
        this.mousePos = newMousePos
      }
      else{
        const newMousePos = {
        x: Math.max(0, Math.min(this.mousePos.x - mouseMove.x * 3.5, this.boardWidth - 30)),
        y: Math.max(0, Math.min(this.mousePos.y - mouseMove.y * 3.5, this.boardHeight - 30))
        }
        this.mousePos = newMousePos
      }

      if (!this.checkWallCollision(newCatPos)) {
        this.catPos = newCatPos
      }
      else{
        const newCatPos = {
        x: Math.max(0, Math.min(this.catPos.x - catMove.x * 3.5, this.boardWidth - 30)),
        y: Math.max(0, Math.min(this.catPos.y - catMove.y * 3.5, this.boardHeight - 30))
        }
        this.catPos = newCatPos
      }

      // Vérifier la collecte de fromage
      this.checkCheeseCollection()

      // Vérifier la capture
      const dx = this.mousePos.x - this.catPos.x
      const dy = this.mousePos.y - this.catPos.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance < this.catchDistance) {
        this.catScore++
        this.isPaused = true
        this.resetPositions()
        
        // Reprendre le jeu après 3 secondes
        this.spawnCheese()
        setTimeout(() => {
          this.isPaused = false
        }, 3000)
      }
    },
    spawnCheese() {
      // Générer une position aléatoire pour le fromage
      const margin = 30
      let newPos
      do {
        newPos = {
          x: margin + Math.random() * (this.boardWidth - 2 * margin),
          y: margin + Math.random() * (this.boardHeight - 2 * margin)
        }
      } while (this.checkWallCollision(newPos)) // Réessayer si le fromage apparaît dans un mur
      
      this.cheesePos = newPos
    },
    checkCheeseCollection() {
      if (!this.cheesePos) return

      // Calculer la distance entre la souris et le fromage
      const dx = this.mousePos.x - this.cheesePos.x
      const dy = this.mousePos.y - this.cheesePos.y
      const distance = Math.sqrt(dx * dx + dy * dy)

      // Si la souris est assez proche du fromage
      if (distance < 30) {
        this.mouseScore++ // Augmenter le score de la souris
        this.cheesePos = null // Faire disparaître le fromage immédiatement
        setTimeout(() => {
          this.spawnCheese() // Faire réapparaître un nouveau fromage après 1 seconde
        }, 1500)
      }
    },
    resetPositions() {
      this.mousePos = { x: 40, y: 40 }
      this.catPos = { x: 900, y: 500 }
    },
    startGame() {
      this.spawnCheese() // Faire apparaître le premier fromage
      this.gameLoop = setInterval(this.updatePositions, 20)
      this.timer = setInterval(this.updateTimer, 1000)
      this.$refs.gameContainer.focus()
    },
    updateTimer() {
      if (this.timeLeft > 0 && !this.isPaused && this.gameStarted && this.countdown == null) {
        this.timeLeft--
      } else if (this.timeLeft <= 0 && !this.isPaused && this.gameStarted){
        this.endGame()
      }
    },
    endGame() {
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
      
      if (this.catScore > this.mouseScore) {
        this.winner = 'Le Chat'
      } else if (this.mouseScore > this.catScore) {
        this.winner = 'La Souris'
      } else {
        this.winner = 'Personne ne '
      }
    },
    startNewGame() {
      this.gameStarted = true
      this.mousePos = { x: 40, y: 40 }
      this.catPos = { x: 900, y: 500 }
      this.mouseScore = 0
      this.catScore = 0
      this.timeLeft = 5
      this.gameOver = false
      this.winner = ''
      this.pressedKeys.clear()
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
    }
  },
  mounted() {
  },
  beforeDestroy() {
    if (this.gameLoop) {
      clearInterval(this.gameLoop)
    }
    if (this.timer) {
      clearInterval(this.timer)
    }
    window.removeEventListener('keydown', this.handleKeyPress)
    window.removeEventListener('keyup', this.handleKeyUp)
  }
}
</script>

<style scoped>
.game-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px;
  outline: none;
}

.game-board {
  position: relative;
  background-color: #f0f0f0;
  border: 2px solid #333;
  border-radius: 8px;
  overflow: hidden;
}

.mouse, .cat, .cheese {
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

.game-info {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
}

.scores {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 10px;
}

.player-score {
  color: #2c3e50;
}

.timer {
  color: #e67e22;
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
  background-color: #34495e;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.wall.horizontal {
  height: 10px;
}

.wall.vertical {
  width: 10px;
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
</style>
