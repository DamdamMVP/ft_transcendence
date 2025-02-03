<template>
	<div class="catch-view">
	  <router-view v-slot="{ Component }">
		<transition name="fade" mode="out-in">
		  <component :is="Component" />
		</transition>
	  </router-view>
	</div>
  </template>
  
  <style scoped>
  .catch-view {
	width: 100%;
	height: 85vh;
	display: flex;
	justify-content: center;
	align-items: center;
	position: relative;
	overflow: hidden;
	background: var(--background-color);
	animation: fadeIn 0.6s ease;
  }
  
  .catch-view::before {
	content: '';
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: radial-gradient(
	  circle at top right,
	  var(--primary-shadow-color) 0%,
	  transparent 70%
	);
	opacity: 0.1;
	pointer-events: none;
	z-index: 0;
  }
  
  .catch-view > * {
	position: relative;
	z-index: 1;
	width: 100%;
	height: 100%;
  }
  
  .fade-enter-active,
  .fade-leave-active {
	transition: opacity 0.3s ease, transform 0.3s ease;
  }
  
  .fade-enter-from,
  .fade-leave-to {
	opacity: 0;
	transform: translateY(10px);
  }
  
  @keyframes fadeIn {
	from {
	  opacity: 0;
	  transform: translateY(20px);
	}
	to {
	  opacity: 1;
	  transform: translateY(0);
	}
  }
  
  @media (max-width: 768px) {
	.catch-view {
	  height: calc(85vh - 60px);
	}
  }
  
  @media (prefers-color-scheme: dark) {
	.catch-view::before {
	  opacity: 0.15;
	}
  }
  </style>