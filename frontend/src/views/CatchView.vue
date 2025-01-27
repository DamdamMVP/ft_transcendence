<template>
  <div class="Catch-view">
    <h1>Attrape-moi si tu peux</h1>
    <CatchGame 
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
      playerUsername: 'Joueur 1',  // À remplacer par le vrai username
      guestUsername: 'Joueur 2'    // À remplacer par le vrai username
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
</style>
