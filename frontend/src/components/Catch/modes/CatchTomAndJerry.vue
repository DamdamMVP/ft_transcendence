<template>
  <div class="catch-game">
    <div v-if="!guestUsername" class="guest-form">
      <h2>{{ $t('catch.enterGuestName') }}</h2>
      <input 
        v-model="guestInput" 
        @keyup.enter="setGuestUsername"
        :placeholder="$t('catch.player2Placeholder')"
        class="guest-input"
      />
      <button @click="setGuestUsername" class="submit-btn">{{ $t('catch.start') }}</button>
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
import CatchGame from '../CatchGame.vue'
import { useAuthStore } from '@/stores/authStore'
import { ref } from 'vue'

export default {
  name: 'CatchTomAndJerry',
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
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.guest-form {
  background-color: var(--background-color-secondary);
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  text-align: center;
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

h2 {
  color: var(--text-color);
  margin-bottom: 20px;
  font-size: 1.5em;
}

.guest-input {
  width: calc(100% - 24px);
  padding: 12px;
  margin: 0 auto 15px auto;
  border: 2px solid var(--border-color);
  border-radius: 6px;
  font-size: 16px;
  transition: all 0.3s;
  box-sizing: border-box;
  display: block;
  background-color: var(--background-color);
  color: var(--text-color);
}

.submit-btn {
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn:hover {
  background-color: var(--primary-color-dark);
}
</style>
