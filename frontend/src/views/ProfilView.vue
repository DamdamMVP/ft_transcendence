<script setup>
import ProfilLeft from '../components/profil/ProfilLeft.vue'
import NavBarProfil from '../components/profil/NavBarProfil.vue'
</script>

<template>
  <main class="profil-view">
    <NavBarProfil />
    <div class="profil-content">
      <ProfilLeft />
      <router-view />
    </div>
  </main>
</template>

<style scoped>
.profil-view {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80vh;
  margin: 0;
  padding: 0;
}

.profil-content {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
}
</style>
