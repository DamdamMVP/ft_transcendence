<template>
  <div class="catch-game">
    <div v-if="!guestUsername" class="guest-form-container">
      <div class="guest-form">
        <h1>Attrape-moi si tu peux</h1>
        <h2>{{ $t('catch.enterGuestName') }}</h2>
        <input 
          v-model="guestInput" 
          @keyup.enter="setGuestUsername"
          :placeholder="$t('catch.player2Placeholder')"
          class="guest-input"
        />
        <div class="icon-selection">
          <h3>{{ $t('catch.selectPlayerIcon') }}</h3>
          <div class="icon-options">
            <div 
              v-for="icon in icons" 
              :key="icon"
              class="icon-option"
              :class="{ selected: selectedIcon === icon }"
              @click="selectIcon(icon)"
            >
              <img :src="getIconPath(icon)" :alt="icon" />
            </div>
          </div>
        </div>
        <button @click="setGuestUsername" class="submit-btn">{{ $t('catch.start') }}</button>
      </div>
    </div>
    <FortyTwoCatchGame 
      v-else
      :player-username="authStore.user?.username || $t('catch.player1Default')"
      :guest-username="guestUsername"
      :player-icon="selectedIcon"
      mode="fortytwo"
    />
  </div>
</template>

<script>
import FortyTwoCatchGame from '../42CatchGame.vue'
import { useAuthStore } from '@/stores/authStore'
import { ref } from 'vue'
import gamian from '@/assets/gamian.png'
import thomian from '@/assets/thomian.png'
import damian from '@/assets/damian.png'

export default {
  name: 'CatchFortyTwo',
  components: {
    FortyTwoCatchGame
  },
  setup() {
    const authStore = useAuthStore()
    const guestUsername = ref(null)
    const guestInput = ref('')
    const selectedIcon = ref('gamian')
    const icons = ['gamian', 'thomian', 'damian']

    const setGuestUsername = () => {
      if (guestInput.value.trim()) {
        guestUsername.value = guestInput.value.trim()
      }
    }

    const selectIcon = (icon) => {
      selectedIcon.value = icon
    }

    const getIconPath = (icon) => {
      const iconPaths = {
        gamian,
        thomian,
        damian
      }
      return iconPaths[icon]
    }

    return {
      authStore,
      guestUsername,
      guestInput,
      setGuestUsername,
      selectedIcon,
      icons,
      selectIcon,
      getIconPath
    }
  }
}
</script>

<style scoped>
.catch-game {
  width: 100%;
  position: absolute;
  top: var(--navbar-height, 60px);
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent; /* Changé pour éviter les conflits */
  overflow: auto;
}

.guest-form-container {
  position: fixed; /* Changé pour fixed pour couvrir tout l'écran */
  top: var(--navbar-height, 100px);
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  background: linear-gradient(135deg,
    var(--background-color) 0%,
    var(--background-secondary-color) 100%
  );
  backdrop-filter: blur(5px);
}

.guest-form {
  background: var(--surface-color);
  padding: 3rem;
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  text-align: center;
  width: 400px;
  max-width: 90%;
  animation: scaleIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  z-index: 1001;
}


h1 {
  color: var(--primary-color);
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  text-shadow: 0 0 15px var(--primary-shadow-color);
  animation: float 3s ease-in-out infinite;
}

h2, h3 {
  color: var(--text-color);
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  opacity: 0.9;
}

.guest-input {
  width: 80%;
  padding: 1rem;
  margin: 1.5rem 0;
  border: 2px solid var(--primary-color);
  border-radius: 12px;
  font-size: 1rem;
  background: var(--surface-color);
  color: var(--text-color);
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px var(--primary-shadow-color);
}

.guest-input:focus {
  outline: none;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

.icon-selection {
  margin: 2rem 0;
}

.icon-options {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1rem;
}

.icon-option {
  cursor: pointer;
  padding: 0.8rem;
  border: 2px solid transparent;
  border-radius: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.icon-option img {
  width: 60px;
  height: 60px;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.icon-option.selected {
  border-color: var(--primary-color);
  background: var(--background-secondary-color);
  transform: scale(1.1);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

.icon-option:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

.icon-option:hover img {
  transform: scale(1.1);
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover-color));
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  margin-top: 2rem;
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  background: linear-gradient(135deg, var(--primary-hover-color), var(--primary-color));
}

.submit-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.submit-btn:hover::after {
  opacity: 1;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Media Queries */
@media (max-width: 768px) {
  .guest-form {
    padding: 2rem;
    width: 90%;
  }

  h1 {
    font-size: 1.6rem;
  }

  .icon-options {
    gap: 1rem;
  }

  .icon-option img {
    width: 50px;
    height: 50px;
  }

  .submit-btn {
    padding: 0.8rem;
    font-size: 1rem;
  }
}
</style>