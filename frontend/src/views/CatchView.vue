<template>
  <div class="Catch-view">
    <h1>Attrape-moi si tu peux</h1>
    <CatchGame />
  </div>
</template>

<script>
import CatchGame from '@/components/Catch/CatchGame.vue'

export default {
  name: 'CatchView',
  components: {
    CatchGame
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
</style>
