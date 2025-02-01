<template>
  <div class="catch-view">
    <router-view></router-view>
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
.catch-view {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
