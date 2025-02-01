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
        <button @click="setGuestUsername" class="submit-btn">{{ $t('catch.start') }}</button>
      </div>
    </div>
    <FortyTwoCatchGame 
      v-else
      :player-username="authStore.user?.username || $t('catch.player1Default')"
      :guest-username="guestUsername"
      mode="fortytwo"
    />
  </div>
</template>

<script>
import FortyTwoCatchGame from '../42CatchGame.vue'
import { useAuthStore } from '@/stores/authStore'
import { ref } from 'vue'

export default {
  name: 'CatchFortyTwo',
  components: {
    FortyTwoCatchGame
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
  height: 100vh;
  background: var(--background-color);
}

.guest-form-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  height: 100vh;
  width: 100%;
  padding-top: 15vh;
}

.guest-form {
  background: var(--background-secondary-color);
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  text-align: center;
  width: 100%;
  max-width: 400px;
  margin: 0 1rem;
}

h1 {
  color: var(--primary-color);
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

h2 {
  color: var(--text-color);
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
}

.guest-input {
  width: 100%;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 2px solid var(--border-color);
  border-radius: 6px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 1rem;
}

.guest-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.submit-btn {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.submit-btn:hover {
  background: var(--primary-hover-color);
}
</style>
