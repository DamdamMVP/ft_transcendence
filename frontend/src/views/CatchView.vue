<template>
  <div class="Catch-view">
    <h1>{{ $t('catch.title') }}</h1>
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
    />
  </div>
</template>

<script>
import CatchGame from '@/components/Catch/CatchGame.vue'
import { useAuthStore } from '@/stores/authStore'
import { useTheme } from '@/composables/useTheme'
import { useI18n } from 'vue-i18n'

export default {
  name: 'CatchView',
  components: {
    CatchGame
  },
  setup() {
    const authStore = useAuthStore()
    const { currentTheme } = useTheme()
    const { t } = useI18n()
    return { authStore, currentTheme, t }
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
