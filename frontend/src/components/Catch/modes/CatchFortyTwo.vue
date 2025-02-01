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
  height: 100vh;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--background-color);
}

.guest-form-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  background-color: var(--background-color);
}

.guest-form {
  background-color: var(--surface-color);
  padding: 2.5rem;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  text-align: center;
  max-width: 90%;
  width: 400px;
}

h1 {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  font-size: 1.8rem;
}

h2 {
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  color: var(--text-color);
}

.guest-input {
  width: 100%;
  padding: 0.8rem;
  margin: 1.5rem 0;
  border: 2px solid var(--border-color);
  border-radius: 5px;
  font-size: 1rem;
  background-color: var(--input-background);
  color: var(--text-color);
  text-align: center;
  box-sizing: border-box;
}

.icon-selection {
  margin: 1.5rem 0;
  text-align: center;
}

.icon-selection h3 {
  margin-bottom: 1rem;
  color: var(--text-color);
  font-size: 1.2rem;
}

.icon-options {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.icon-option {
  cursor: pointer;
  padding: 0.5rem;
  border: 2px solid transparent;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.icon-option img {
  width: 50px;
  height: 50px;
  object-fit: contain;
}

.icon-option.selected {
  border-color: var(--primary-color);
  background-color: var(--surface-hover-color);
}

.icon-option:hover {
  background-color: var(--surface-hover-color);
}

.submit-btn {
  width: 100%;
  padding: 0.8rem;
  margin-top: 1.5rem;
  border: none;
  border-radius: 5px;
  background-color: var(--primary-color);
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  box-sizing: border-box;
}

.submit-btn:hover {
  background-color: var(--primary-color-hover);
}
</style>
