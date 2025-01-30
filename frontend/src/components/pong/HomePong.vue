<template>
  <div class="pong-home">
    <h1>PONG</h1>
    <div class="game-modes">
      <button @click="selectMode('tournament')" class="mode-button">
        <h2>{{ $t('pong.tournament.title') }}</h2>
        <p>{{ $t('pong.tournament.description') }}</p>
      </button>

      <button @click="selectMode('ai')" class="mode-button">
        <h2>{{ $t('pong.ai.title') }}</h2>
        <p>{{ $t('pong.ai.description') }}</p>
      </button>

      <button @click="selectMode('local')" class="mode-button">
        <h2>{{ $t('pong.local.title') }}</h2>
        <p>{{ $t('pong.local.description') }}</p>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedMode = ref(null)

const selectMode = (mode) => {
  selectedMode.value = mode
  router.push(`/pong/${mode}`)
}
</script>

<style scoped>
.pong-home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 65vh;
  background: var(--background-color);
  color: white;
  width: 100%;
}

h1 {
  font-size: 3rem;
  margin-bottom: 2rem;
  color: #4caf50;
}

.game-modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
  justify-items: center;
}

.mode-button {
  background: #2a2a2a;
  border: 2px solid #4caf50;
  border-radius: 10px;
  padding: 2rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  width: 100%;
  max-width: 350px;
}

.mode-button:hover {
  transform: translateY(-5px);
  background: #3a3a3a;
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
}

.mode-button h2 {
  margin: 0 0 1rem 0;
  color: #4caf50;
}

.mode-button p {
  margin: 0;
  opacity: 0.8;
}
</style>
