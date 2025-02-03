<template>
  <div class="catch-game">
    <div v-if="!guestUsername" class="guest-form-container">
      <div class="guest-form">
        <h1>{{ $t('catch.title') }}</h1>
        <h2>{{ $t('catch.enterGuestName') }}</h2>
        <input 
          v-model="guestInput" 
          @keyup.enter="setGuestUsername"
          :placeholder="$t('catch.player2Placeholder')"
          class="guest-input"
        />
        <button @click="setGuestUsername" class="submit-btn">{{ $t('catch.start') }}</button>
      </div>
    </div>
    <CatchGame 
      v-else
      :player-username="authStore.user?.username || $t('catch.player1Default')"
      :guest-username="guestUsername"
      mode="tomandjerry"
    />
  </div>
</template>

<script>
import CatchGame from '@/components/catch/modes/CatchGame.vue'
import { useAuthStore } from '@/stores/authStore'
import { ref } from 'vue'

export default {
  name: 'CatchSetup',
  components: {
    CatchGame
  },
  setup() {
    const authStore = useAuthStore()
    const guestUsername = ref(null)
    const guestInput = ref('')

    const setGuestUsername = () => {
      if (guestInput.value.trim()) {
        guestUsername.value = guestInput.value.trim()
      }
    }

    return {
      authStore,
      guestUsername,
      guestInput,
      setGuestUsername
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
  background: transparent;
  overflow: auto;
}

.guest-form-container {
  position: fixed;
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
