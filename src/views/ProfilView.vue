<script setup>
import ProfilLeft from '../components/ProfilLeft.vue'
import NavBarProfil from '../components/NavBarProfil.vue'
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
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  width: 100%;
}
</style>
