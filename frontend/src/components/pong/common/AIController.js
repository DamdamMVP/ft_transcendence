// Constantes IA
const AI_UPDATE_INTERVAL = 1000 
const IDLE_MOVEMENT_CHANCE = 0.05 
const IDLE_MOVEMENT_DURATION = 550 
const MAX_AI_SPEED = 5 
const MIN_AI_SPEED = 1

export class AIController {
  constructor() {
    this.lastUpdateTime = 0
    this.targetY = 0
    this.upPressed = false
    this.downPressed = false
    this.idleMovement = null
  }

  predictBallPosition(ball, aiX) {
    const { x, y, speedX, speedY, radius } = ball
    const canvasHeight = 500 

    if (speedX <= 0) {
      return canvasHeight / 2
    }

    let futureX = x
    let futureY = y
    let vx = speedX
    let vy = speedY

    while (futureX + radius < aiX) {
      futureX += vx
      futureY += vy
      if (futureY - radius < 0) {
        futureY = radius
        vy = -vy
      }
      if (futureY + radius > canvasHeight) {
        futureY = canvasHeight - radius
        vy = -vy
      }
    }
    return futureY
  }

  update(ball, aiPaddle) {
    const now = Date.now()

    if (!this.idleMovement && ball.speedX < 0 && Math.random() < IDLE_MOVEMENT_CHANCE) {
      this.idleMovement = {
        direction: Math.random() > 0.5 ? 'up' : 'down',
        duration: IDLE_MOVEMENT_DURATION + (Math.random() - 0.5) * 200,
        startTime: now
      }
    }

    if (now - this.lastUpdateTime >= AI_UPDATE_INTERVAL) {
      this.lastUpdateTime = now
      this.targetY = this.predictBallPosition(ball, aiPaddle.x)
    }

    if (this.idleMovement && ball.speedX < 0) {
      if (now - this.idleMovement.startTime > this.idleMovement.duration) {
        this.idleMovement = null
      } else {
        this.upPressed = this.idleMovement.direction === 'up'
        this.downPressed = this.idleMovement.direction === 'down'
        return { up: this.upPressed, down: this.downPressed }
      }
    }

    const margin = 5
    const aiCenter = aiPaddle.y + aiPaddle.height / 2
    const distance = Math.abs(aiCenter - this.targetY)
    const speed = Math.min(MAX_AI_SPEED, Math.max(MIN_AI_SPEED, distance / 10))

    if (aiCenter < this.targetY - margin) {
      this.upPressed = false
      this.downPressed = true
      aiPaddle.speed = speed
    } else if (aiCenter > this.targetY + margin) {
      this.upPressed = true
      this.downPressed = false
      aiPaddle.speed = speed
    } else {
      this.upPressed = false
      this.downPressed = false
    }

    return { up: this.upPressed, down: this.downPressed }
  }
}