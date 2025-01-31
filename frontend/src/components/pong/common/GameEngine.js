export class GameEngine {
  constructor(canvasWidth = 800, canvasHeight = 450) {
    this.canvasWidth = canvasWidth
    this.canvasHeight = canvasHeight
    this.WINNING_SCORE = 5
    this.INITIAL_BALL_SPEED = 4
    this.BALL_SPEED_INCREASE = 1.1
    this.MAX_BALL_SPEED = 10

    // Bonus constants
    this.BONUS_SPAWN_INTERVAL = 4000
    this.BONUS_COLORS = ['red', 'green', 'blue']
    this.BONUS_BAR_WIDTH = 10
    this.BONUS_BAR_HEIGHT = 60
    this.INITIAL_PADDLE_HEIGHT = this.canvasHeight * 0.15

    this.resetGameState()
  }

  resetGameState() {
    const paddleHeight = this.INITIAL_PADDLE_HEIGHT

    this.gameState = {
      player1: {
        x: 20,
        y: this.canvasHeight / 2 - paddleHeight / 2,
        width: 10,
        height: paddleHeight,
        speed: 4.5,
        upPressed: false,
        downPressed: false,
      },
      player2: {
        x: this.canvasWidth - 30,
        y: this.canvasHeight / 2 - paddleHeight / 2,
        width: 10,
        height: paddleHeight,
        speed: 4.5,
        upPressed: false,
        downPressed: false,
      },
      ball: {
        x: this.canvasWidth / 2,
        y: this.canvasHeight / 2,
        radius: 8,
        speedX: 0,
        speedY: 0,
      },
      bonusBars: [],
      lastBonusSpawnTime: Date.now(),
    }
    this.lastPaddleTouched = null
  }

  resetBall() {
    // Reset ball position
    this.gameState.ball.x = this.canvasWidth / 2
    this.gameState.ball.y = this.canvasHeight / 2
    this.gameState.ball.speedX = 0
    this.gameState.ball.speedY = 0

    // Reset paddle positions
    this.gameState.player1.y = this.canvasHeight / 2 - this.gameState.player1.height / 2
    this.gameState.player2.y = this.canvasHeight / 2 - this.gameState.player2.height / 2
  }

  getRandomYNotCenter(barHeight) {
    const forbiddenMargin = 60
    const forbiddenMin = this.canvasHeight / 2 - forbiddenMargin
    const forbiddenMax = this.canvasHeight / 2 + forbiddenMargin

    let y = 0
    do {
      y = Math.random() * (this.canvasHeight - barHeight)
    } while (y >= forbiddenMin && y + barHeight <= forbiddenMax)

    return y
  }

  doBarsOverlap(bar1, bar2) {
    return !(
      bar1.x + bar1.width < bar2.x ||
      bar2.x + bar2.width < bar1.x ||
      bar1.y + bar1.height < bar2.y ||
      bar2.y + bar2.height < bar1.y
    )
  }

  spawnBonusBar() {
    if (this.gameState.bonusBars.length >= 4) return

    for (let attempts = 0; attempts < 10; attempts++) {
      const colorIndex = Math.floor(Math.random() * this.BONUS_COLORS.length)
      const color = this.BONUS_COLORS[colorIndex]

      const newBar = {
        color,
        width: this.BONUS_BAR_WIDTH,
        height: this.BONUS_BAR_HEIGHT,
        x: this.canvasWidth / 2 - this.BONUS_BAR_WIDTH / 2,
        y: this.getRandomYNotCenter(this.BONUS_BAR_HEIGHT),
      }

      let hasOverlap = false
      for (const existingBar of this.gameState.bonusBars) {
        if (this.doBarsOverlap(newBar, existingBar)) {
          hasOverlap = true
          break
        }
      }

      if (!hasOverlap) {
        this.gameState.bonusBars.push(newBar)
        return
      }
    }
  }

  applyBonusEffect(color) {
    switch (color) {
      case 'red':
        if (this.lastPaddleTouched) {
          this.gameState[this.lastPaddleTouched].height -= 15
          if (this.gameState[this.lastPaddleTouched].height < 40) {
            this.gameState[this.lastPaddleTouched].height = 40
          }
        }
        break

      case 'green':
        if (this.lastPaddleTouched) {
          this.gameState[this.lastPaddleTouched].height += 15
          if (this.gameState[this.lastPaddleTouched].height > 120) {
            this.gameState[this.lastPaddleTouched].height = 120
          }
        }
        break

      case 'blue':
        this.gameState.ball.speedX = -this.gameState.ball.speedX
        this.gameState.ball.speedY = -this.gameState.ball.speedY
        break
    }
  }

  launchBall() {
    this.gameState.ball.x = this.canvasWidth / 2
    this.gameState.ball.y = this.canvasHeight / 2
    const goingRight = Math.random() > 0.5
    this.gameState.ball.speedX = this.INITIAL_BALL_SPEED * (goingRight ? 1 : -1)
    this.gameState.ball.speedY = this.INITIAL_BALL_SPEED * (Math.random() * 2 - 1)
    this.lastPaddleTouched = goingRight ? 'player1' : 'player2'
  }

  paddleBounce(who) {
    this.lastPaddleTouched = who

    let currentSpeed = Math.sqrt(
      this.gameState.ball.speedX ** 2 + this.gameState.ball.speedY ** 2
    )
    currentSpeed = Math.min(currentSpeed * this.BALL_SPEED_INCREASE, this.MAX_BALL_SPEED)

    const paddle = this.gameState[who]
    const paddleCenter = paddle.y + paddle.height / 2
    const distFromCenter = (this.gameState.ball.y - paddleCenter) / (paddle.height / 2)
    const maxAngle = (60 * Math.PI) / 180
    const bounceAngle = distFromCenter * maxAngle

    if (who === 'player1') {
      this.gameState.ball.speedX = Math.abs(currentSpeed * Math.cos(bounceAngle))
    } else {
      this.gameState.ball.speedX = -Math.abs(currentSpeed * Math.cos(bounceAngle))
    }
    this.gameState.ball.speedY = currentSpeed * Math.sin(bounceAngle)
  }

  updateGame(player1Score, player2Score, onPoint) {
    // Move player1
    if (this.gameState.player1.upPressed && this.gameState.player1.y > 0) {
      this.gameState.player1.y -= this.gameState.player1.speed
    }
    if (
      this.gameState.player1.downPressed &&
      this.gameState.player1.y + this.gameState.player1.height < this.canvasHeight
    ) {
      this.gameState.player1.y += this.gameState.player1.speed
    }

    // Move player2
    if (this.gameState.player2.upPressed && this.gameState.player2.y > 0) {
      this.gameState.player2.y -= this.gameState.player2.speed
    }
    if (
      this.gameState.player2.downPressed &&
      this.gameState.player2.y + this.gameState.player2.height < this.canvasHeight
    ) {
      this.gameState.player2.y += this.gameState.player2.speed
    }

    // Spawn bonus
    const now = Date.now()
    if (now - this.gameState.lastBonusSpawnTime > this.BONUS_SPAWN_INTERVAL) {
      this.spawnBonusBar()
      this.gameState.lastBonusSpawnTime = now
    }

    // Check bonus collisions
    for (let i = this.gameState.bonusBars.length - 1; i >= 0; i--) {
      const bar = this.gameState.bonusBars[i]
      if (
        this.gameState.ball.x + this.gameState.ball.radius >= bar.x &&
        this.gameState.ball.x - this.gameState.ball.radius <= bar.x + bar.width &&
        this.gameState.ball.y + this.gameState.ball.radius >= bar.y &&
        this.gameState.ball.y - this.gameState.ball.radius <= bar.y + bar.height
      ) {
        this.applyBonusEffect(bar.color)
        this.gameState.bonusBars.splice(i, 1)
      }
    }

    // Move ball
    let nextX = this.gameState.ball.x + this.gameState.ball.speedX
    let nextY = this.gameState.ball.y + this.gameState.ball.speedY

    // Collisions with paddles
    // Player1
    if (
      nextX - this.gameState.ball.radius <=
        this.gameState.player1.x + this.gameState.player1.width &&
      nextX - this.gameState.ball.radius >= this.gameState.player1.x &&
      this.gameState.ball.y >= this.gameState.player1.y &&
      this.gameState.ball.y <= this.gameState.player1.y + this.gameState.player1.height &&
      this.gameState.ball.speedX < 0
    ) {
      this.paddleBounce('player1')
      nextX = this.gameState.ball.x + this.gameState.ball.speedX
      nextY = this.gameState.ball.y + this.gameState.ball.speedY
    }

    // Player2
    if (
      nextX + this.gameState.ball.radius >= this.gameState.player2.x &&
      nextX + this.gameState.ball.radius <=
        this.gameState.player2.x + this.gameState.player2.width &&
      this.gameState.ball.y >= this.gameState.player2.y &&
      this.gameState.ball.y <= this.gameState.player2.y + this.gameState.player2.height &&
      this.gameState.ball.speedX > 0
    ) {
      this.paddleBounce('player2')
      nextX = this.gameState.ball.x + this.gameState.ball.speedX
      nextY = this.gameState.ball.y + this.gameState.ball.speedY
    }

    // Apply next position
    this.gameState.ball.x = nextX
    this.gameState.ball.y = nextY

    // Top/bottom collisions
    if (this.gameState.ball.y - this.gameState.ball.radius < 0) {
      this.gameState.ball.y = this.gameState.ball.radius
      this.gameState.ball.speedY = -this.gameState.ball.speedY
    } else if (this.gameState.ball.y + this.gameState.ball.radius > this.canvasHeight) {
      this.gameState.ball.y = this.canvasHeight - this.gameState.ball.radius
      this.gameState.ball.speedY = -this.gameState.ball.speedY
    }

    // Score points
    if (this.gameState.ball.x - this.gameState.ball.radius < 0) {
      onPoint('player2')
      if (player2Score < this.WINNING_SCORE) {
        this.resetGameState()
        this.resetBall()
        this.launchBall()
      }
    }
    if (this.gameState.ball.x + this.gameState.ball.radius > this.canvasWidth) {
      onPoint('player1')
      if (player1Score < this.WINNING_SCORE) {
        this.resetGameState()
        this.resetBall()
        this.launchBall()
      }
    }

    return player1Score >= this.WINNING_SCORE || player2Score >= this.WINNING_SCORE
  }

  drawGame(ctx, gamePhase, player1Score, player2Score) {
    // Clear canvas
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--background-color')
    ctx.fillRect(0, 0, this.canvasWidth, this.canvasHeight)

    // Draw border
    ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--primary-color')
    ctx.lineWidth = 2
    ctx.strokeRect(0, 0, this.canvasWidth, this.canvasHeight)

    // Draw paddles
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--primary-color')
    ctx.fillRect(
      this.gameState.player1.x,
      this.gameState.player1.y,
      this.gameState.player1.width,
      this.gameState.player1.height
    )
    ctx.fillRect(
      this.gameState.player2.x,
      this.gameState.player2.y,
      this.gameState.player2.width,
      this.gameState.player2.height
    )

    // Draw bonus bars
    this.gameState.bonusBars.forEach((bar) => {
      ctx.fillStyle = bar.color
      ctx.fillRect(bar.x, bar.y, bar.width, bar.height)
    })

    // Draw ball
    ctx.beginPath()
    ctx.arc(this.gameState.ball.x, this.gameState.ball.y, this.gameState.ball.radius, 0, Math.PI * 2)
    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--accent-color')
    ctx.fill()
    ctx.closePath()

    // Si on est en phase de score, afficher le score au centre
    if (gamePhase === 'score') {
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--primary-color')
      ctx.font = 'bold 48px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(
        `${player1Score} - ${player2Score}`,
        this.canvasWidth / 2,
        this.canvasHeight / 2
      )
    }
  }

  handleKeyDown(e) {
    const key = e.key
    // player1
    if (key.toLowerCase() === 'f') this.gameState.player1.upPressed = true
    if (key.toLowerCase() === 's') this.gameState.player1.downPressed = true
    // player2
    if (key === 'ArrowUp') this.gameState.player2.upPressed = true
    if (key === 'ArrowDown') this.gameState.player2.downPressed = true
  }

  handleKeyUp(e) {
    const key = e.key
    // player1
    if (key.toLowerCase() === 'f') this.gameState.player1.upPressed = false
    if (key.toLowerCase() === 's') this.gameState.player1.downPressed = false
    // player2
    if (key === 'ArrowUp') this.gameState.player2.upPressed = false
    if (key === 'ArrowDown') this.gameState.player2.downPressed = false
  }

  getBallState() {
    return { ...this.gameState.ball }
  }

  getPlayer2State() {
    return { ...this.gameState.player2 }
  }

  setPlayer2Input(up, down) {
    this.gameState.player2.upPressed = up
    this.gameState.player2.downPressed = down
  }
}
