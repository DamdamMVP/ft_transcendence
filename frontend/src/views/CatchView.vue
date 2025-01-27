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
      :player-username="playerUsername"
      :guest-username="guestUsername"
    />
  </div>
</template>

<script>
import CatchGame from '@/components/Catch/CatchGame.vue'

export default {
  name: 'CatchView',
  components: {
    CatchGame
  },
  data() {
    return {
      playerUsername: 'Joueur 1',
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
}

h1 {
  margin-bottom: 20px;
}

.guest-form {
  background-color: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5em;
}

.guest-input {
  width: calc(100% - 24px);
  padding: 12px;
  margin: 0 auto 15px auto;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
  display: block;
}

.guest-input:focus {
  border-color: #2ecc71;
  outline: none;
}

.submit-btn {
  background-color: #2ecc71;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #27ae60;
}
</style>
