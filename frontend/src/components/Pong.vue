<template>
	<div class="flex flex-col items-center justify-center h-screen bg-black">
	  <canvas 
		ref="canvas" 
		:width="width" 
		:height="height" 
		class="border-2 border-white"
	  />
	  <div class="button-container">
		<button 
		  v-if="!gameStarted && !gameWinner"
		  @click="startGame"
		  class="game-button start-button"
		>
		  Jouer
		</button>
		<button 
		  v-if="gameWinner"
		  @click="resetGame"
		  class="game-button replay-button"
		>
		  Rejouer
		</button>
	  </div>
	</div>
  </template>
  
  <script>
  export default {
	name: 'Pong',
	data() {
	  return {
		// Paramètres du jeu
		width: 800,
		height: 400,
		paddleWidth: 10,
		paddleHeight: 100,
		ballSize: 10,
		winningScore: 3,
  
		// États du jeu
		playerY: 0,
		computerY: 0,
		ballX: 0,
		ballY: 0,
		ballSpeedX: 5,
		ballSpeedY: 5,
		playerScore: 0,
		computerScore: 0,
		gameWinner: null,
		gameStarted: false,
  
		// Touches pressées
		keysPressed: {
		  w: false,
		  s: false,
		  ArrowUp: false,
		  ArrowDown: false
		},
  
		gameInterval: null
	  }
	},
	mounted() {
	  // Initialisation des positions
	  this.playerY = this.height / 2 - this.paddleHeight / 2
	  this.computerY = this.height / 2 - this.paddleHeight / 2
	  this.ballX = this.width / 2
	  this.ballY = this.height / 2
  
	  // Gestion des touches
	  window.addEventListener('keydown', this.handleKeyDown)
	  window.addEventListener('keyup', this.handleKeyUp)
  
	  // On dessine le terrain initial sans démarrer le jeu
	  this.drawInitialState()
	},
	beforeUnmount() {
	  clearInterval(this.gameInterval)
	  window.removeEventListener('keydown', this.handleKeyDown)
	  window.removeEventListener('keyup', this.handleKeyUp)
	},
	methods: {
	  handleKeyDown(e) {
		// Empêcher le défilement de la page pour les touches de jeu
		if (['ArrowUp', 'ArrowDown', 'w', 's', 'W', 'S'].includes(e.key)) {
		  e.preventDefault()
		}
		const key = e.key.toLowerCase()
		this.keysPressed[key] = true
	  },
	  handleKeyUp(e) {
		const key = e.key.toLowerCase()
		this.keysPressed[key] = false
	  },
	  startGame() {
		this.gameStarted = true
		this.gameInterval = setInterval(this.gameLoop, 1000 / 60)
	  },
	  resetGame() {
		this.playerScore = 0
		this.computerScore = 0
		this.gameWinner = null
		this.gameStarted = false
		this.ballX = this.width / 2
		this.ballY = this.height / 2
		this.ballSpeedX = 5 * (Math.random() > 0.5 ? 1 : -1) // Direction aléatoire
		this.ballSpeedY = 5 * (Math.random() > 0.5 ? 1 : -1)
		this.playerY = this.height / 2 - this.paddleHeight / 2
		this.computerY = this.height / 2 - this.paddleHeight / 2
		clearInterval(this.gameInterval)
		this.drawInitialState()
	  },
	  gameLoop() {
		if (!this.gameStarted || this.gameWinner) return
  
		// Mouvement des raquettes
		if (this.keysPressed.w) {
		  this.playerY = Math.max(0, this.playerY - 5)
		}
		if (this.keysPressed.s) {
		  this.playerY = Math.min(this.height - this.paddleHeight, this.playerY + 5)
		}
		if (this.keysPressed.arrowup) {
		  this.computerY = Math.max(0, this.computerY - 5)
		}
		if (this.keysPressed.arrowdown) {
		  this.computerY = Math.min(this.height - this.paddleHeight, this.computerY + 5)
		}
  
		// Mouvement de la balle
		let newBallX = this.ballX + this.ballSpeedX
		let newBallY = this.ballY + this.ballSpeedY
  
		// Rebond sur les murs du haut et du bas
		if (newBallY <= 0 || newBallY >= this.height - this.ballSize) {
		  this.ballSpeedY = -this.ballSpeedY
		  newBallY = newBallY <= 0 ? 0 : this.height - this.ballSize
		}
  
		// Collision avec les raquettes
		const isCollidingWithPlayer = 
		  newBallX <= this.paddleWidth &&
		  newBallY + this.ballSize >= this.playerY &&
		  newBallY <= this.playerY + this.paddleHeight
  
		const isCollidingWithComputer = 
		  newBallX >= this.width - this.paddleWidth - this.ballSize &&
		  newBallY + this.ballSize >= this.computerY &&
		  newBallY <= this.computerY + this.paddleHeight
  
		if (isCollidingWithPlayer || isCollidingWithComputer) {
		  this.ballSpeedX = -this.ballSpeedX * 1.1 // Augmente légèrement la vitesse
		  this.ballSpeedY = this.ballSpeedY * 1.1
		  
		  // Ajuste l'angle selon où la balle frappe la raquette
		  const paddleY = isCollidingWithPlayer ? this.playerY : this.computerY
		  const relativeIntersectY = (paddleY + (this.paddleHeight / 2)) - newBallY
		  const normalizedIntersectY = relativeIntersectY / (this.paddleHeight / 2)
		  this.ballSpeedY = -normalizedIntersectY * Math.abs(this.ballSpeedX)
		}
  
		// Gestion des points
		if (newBallX <= 0) {
		  this.computerScore++
		  if (this.computerScore >= this.winningScore) {
			this.gameWinner = 'Joueur de droite'
			clearInterval(this.gameInterval)
		  } else {
			this.resetBall()
		  }
		} else if (newBallX >= this.width) {
		  this.playerScore++
		  if (this.playerScore >= this.winningScore) {
			this.gameWinner = 'Joueur de gauche'
			clearInterval(this.gameInterval)
		  } else {
			this.resetBall()
		  }
		} else {
		  this.ballX = newBallX
		  this.ballY = newBallY
		}
  
		this.draw()
	  },
	  resetBall() {
		this.ballX = this.width / 2
		this.ballY = this.height / 2
		this.ballSpeedX = 5 * (Math.random() > 0.5 ? 1 : -1)
		this.ballSpeedY = 5 * (Math.random() > 0.5 ? 1 : -1)
	  },
	  draw() {
		const ctx = this.$refs.canvas.getContext('2d')
		ctx.clearRect(0, 0, this.width, this.height)
		
		// Dessin des raquettes
		ctx.fillStyle = 'white'
		ctx.fillRect(0, this.playerY, this.paddleWidth, this.paddleHeight)
		ctx.fillRect(this.width - this.paddleWidth, this.computerY, this.paddleWidth, this.paddleHeight)
		
		// Dessin de la balle
		ctx.fillRect(this.ballX, this.ballY, this.ballSize, this.ballSize)
  
		// Ligne centrale pointillée
		ctx.setLineDash([5, 15])
		ctx.beginPath()
		ctx.moveTo(this.width / 2, 0)
		ctx.lineTo(this.width / 2, this.height)
		ctx.strokeStyle = 'white'
		ctx.stroke()
		
		// Affichage du score
		ctx.font = '48px Arial'
		ctx.textAlign = 'center'
		ctx.fillText(this.playerScore, this.width / 4, 60)
		ctx.fillText(this.computerScore, (this.width / 4) * 3, 60)
  
		// Affichage du gagnant
		if (this.gameWinner) {
		  ctx.font = '32px Arial'
		  ctx.fillText(`${this.gameWinner} gagne !`, this.width / 2, this.height / 2)
		}
	  },
	  drawInitialState() {
		const ctx = this.$refs.canvas.getContext('2d')
		ctx.clearRect(0, 0, this.width, this.height)
		
		// Dessin des raquettes
		ctx.fillStyle = 'white'
		ctx.fillRect(0, this.playerY, this.paddleWidth, this.paddleHeight)
		ctx.fillRect(this.width - this.paddleWidth, this.computerY, this.paddleWidth, this.paddleHeight)
		
		// Ligne centrale pointillée
		ctx.setLineDash([5, 15])
		ctx.beginPath()
		ctx.moveTo(this.width / 2, 0)
		ctx.lineTo(this.width / 2, this.height)
		ctx.strokeStyle = 'white'
		ctx.stroke()
		
		// Affichage du score initial
		ctx.font = '48px Arial'
		ctx.textAlign = 'center'
		ctx.fillText('0', this.width / 4, 60)
		ctx.fillText('0', (this.width / 4) * 3, 60)
  
		// Message de démarrage
		if (!this.gameStarted && !this.gameWinner) {
		  ctx.font = '20px Arial'
		  ctx.fillText('Appuyez sur "Jouer" pour commencer', this.width / 2, this.height / 2 + 50)
		}
	  }
	}
  }
  </script>
  
  <style scoped>
  .button-container {
	margin-top: 2rem;
	display: flex;
	gap: 1rem;
  }
  
  .game-button {
	padding: 0.8rem 2rem;
	font-size: 1.2rem;
	border: none;
	border-radius: 0.5rem;
	cursor: pointer;
	text-transform: uppercase;
	font-weight: bold;
	transition: all 0.3s ease;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .start-button {
	background: linear-gradient(135deg, #4CAF50, #45a049);
	color: white;
  }
  
  .start-button:hover {
	background: linear-gradient(135deg, #45a049, #3d8b40);
	transform: translateY(-2px);
	box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
  }
  
  .replay-button {
	background: linear-gradient(135deg, #2196F3, #1976D2);
	color: white;
  }
  
  .replay-button:hover {
	background: linear-gradient(135deg, #1976D2, #1565C0);
	transform: translateY(-2px);
	box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
  }
  
  .game-button:active {
	transform: translateY(1px);
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  </style>