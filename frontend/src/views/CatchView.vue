<template>
  <div class="Catch-view">
    <h1>Attrape-moi si tu peux</h1>
    <div v-if="!guestUsername" class="guest-form">
      <h2>Entrez le pseudo du deuxième joueur</h2>
      <input 
        v-model="guestInput" 
        @keyup.enter="setGuestUsername"
        placeholder="Pseudo du joueur 2"
        class="guest-input"
      />
      <button @click="setGuestUsername" class="submit-btn">Commencer</button>
    </div>
    <CatchGame 
      v-else
      :player-username="authStore.user?.username || 'Joueur 1'"
      :guest-username="guestUsername"
    />
  </div>
</template>

<script>
import CatchGame from '@/components/Catch/CatchGame.vue'
import { useAuthStore } from '@/stores/authStore'
import { useTheme } from '@/composables/useTheme'

export default {
  name: 'CatchView',
  components: {
    CatchGame
  },
  setup() {
    const authStore = useAuthStore()
    const { currentTheme } = useTheme()
    return { authStore, currentTheme }
  },
  data() {
    return {
      guestUsername: null,
      guestInput: ''
    }
  },
  methods: {
    setGuestUsername() {
      if (this.guestInput.trim()) {
        this.guestUsername = this.guestInput.trim()
      }
    }
  }
}
</script>

<style scoped>
.Catch-view {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 80vh;
  background-color: var(--background-color);
}

h1 {
  margin-bottom: 40px;
  font-size: 2.5em;
  color: var(--text-color);
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

.guest-input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(46, 204, 113, 0.2);
}

.guest-input::placeholder {
  color: var(--text-color-secondary);
}

.submit-btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: var(--primary-hover-color);
}
</style>
