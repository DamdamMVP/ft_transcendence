// Constantes IA
const AI_UPDATE_INTERVAL = 1000 // vision 1 fois/s
const IDLE_MOVEMENT_CHANCE = 0.07 // Chance de démarrer un mouvement inutile
const IDLE_MOVEMENT_DURATION = 650 // Durée moyenne du mouvement en ms

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
    const canvasHeight = 400 // Hauteur standard du canvas

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

    // Gestion des mouvements d'attente
    if (!this.idleMovement && ball.speedX < 0 && Math.random() < IDLE_MOVEMENT_CHANCE) {
      this.idleMovement = {
        direction: Math.random() > 0.5 ? 'up' : 'down',
        duration: IDLE_MOVEMENT_DURATION + (Math.random() - 0.5) * 200,
        startTime: now
      }
    }

    // Mise à jour normale de l'IA
    if (now - this.lastUpdateTime >= AI_UPDATE_INTERVAL) {
      this.lastUpdateTime = now
      this.targetY = this.predictBallPosition(ball, aiPaddle.x)
    }

    // Gestion des mouvements
    if (this.idleMovement && ball.speedX < 0) {
      if (now - this.idleMovement.startTime > this.idleMovement.duration) {
        this.idleMovement = null
      } else {
        this.upPressed = this.idleMovement.direction === 'up'
        this.downPressed = this.idleMovement.direction === 'down'
        return { up: this.upPressed, down: this.downPressed }
      }
    }

    // Comportement normal
    const margin = 5
    const aiCenter = aiPaddle.y + aiPaddle.height / 2
    
    if (aiCenter < this.targetY - margin) {
      this.upPressed = false
      this.downPressed = true
    } else if (aiCenter > this.targetY + margin) {
      this.upPressed = true
      this.downPressed = false
    } else {
      this.upPressed = false
      this.downPressed = false
    }

    return { up: this.upPressed, down: this.downPressed }
  }
}
