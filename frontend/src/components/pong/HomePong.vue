<template>
	<div class="pong-home">
	  <h1 class="title">PONG</h1>
	  <div class="game-modes">
		<button @click="selectMode('tournament')" class="mode-button">
		  <div class="mode-icon">🏆</div>
		  <h2>{{ $t('pong.tournament.title') }}</h2>
		  <p>{{ $t('pong.tournament.description') }}</p>
		  <div class="button-glow"></div>
		</button>
		<button @click="selectMode('ai')" class="mode-button">
		  <div class="mode-icon">🤖</div>
		  <h2>{{ $t('pong.ai.title') }}</h2>
		  <p>{{ $t('pong.ai.description') }}</p>
		  <div class="button-glow"></div>
		</button>
		<button @click="selectMode('local')" class="mode-button">
		  <div class="mode-icon">👥</div>
		  <h2>{{ $t('pong.local.title') }}</h2>
		  <p>{{ $t('pong.local.description') }}</p>
		  <div class="button-glow"></div>
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
	min-height: 65vh;
	background: var(--background-color);
	color: var(--text-color);
	width: 100%;
	position: relative;
	overflow: hidden;
  }
  
  .title {
	font-size: 4.5rem;
	font-weight: 800;
	margin-bottom: 3rem;
	color: var(--primary-color);
	text-shadow: 0 0 15px var(--primary-color);
	position: relative;
	animation: float 3s ease-in-out infinite;
  }
  
  .game-modes {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
	gap: 2.5rem;
	width: 100%;
	max-width: 1200px;
	justify-items: center;
	padding: 0 2rem;
  }
  
  .mode-button {
	background: var(--background-secondary-color);
	border: 2px solid var(--primary-color);
	border-radius: 15px;
	padding: 2.5rem;
	color: var(--text-color);
	cursor: pointer;
	transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
	text-align: center;
	width: 100%;
	max-width: 350px;
	position: relative;
	overflow: hidden;
	backdrop-filter: blur(10px);
  }
  
  .mode-icon {
	font-size: 2.5rem;
	margin-bottom: 1rem;
	transition: transform 0.3s ease;
  }
  
  .mode-button:hover {
	transform: translateY(-8px) scale(1.02);
	background: var(--background-hover-color);
	box-shadow: 0 8px 25px var(--primary-shadow-color);
  }
  
  .mode-button:hover .mode-icon {
	transform: scale(1.2);
  }
  
  .mode-button h2 {
	margin: 0 0 1rem 0;
	color: var(--primary-color);
	font-size: 1.5rem;
	font-weight: 700;
  }
  
  .mode-button p {
	margin: 0;
	color: var(--text-color);
	opacity: 0.9;
	line-height: 1.5;
  }
  
  .button-glow {
	position: absolute;
	top: -50%;
	left: -50%;
	width: 200%;
	height: 200%;
	background: radial-gradient(
	  circle,
	  var(--primary-color) 0%,
	  transparent 70%
	);
	opacity: 0;
	transition: opacity 0.3s ease;
	pointer-events: none;
  }
  
  .mode-button:hover .button-glow {
	opacity: 0.1;
  }
  
  @keyframes float {
	0%, 100% {
	  transform: translateY(0);
	}
	50% {
	  transform: translateY(-10px);
	}
  }
  
  /* Animation pour l'apparition des boutons */
  .mode-button {
	animation: fadeInUp 0.6s ease backwards;
  }
  
  .mode-button:nth-child(1) { animation-delay: 0.2s; }
  .mode-button:nth-child(2) { animation-delay: 0.4s; }
  .mode-button:nth-child(3) { animation-delay: 0.6s; }
  
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
  </style>