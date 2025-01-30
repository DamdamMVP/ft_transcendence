<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import ProfilLeft from '../components/profil/ProfilLeft.vue'
import NavBarProfil from '../components/profil/NavBarProfil.vue'

const route = useRoute()
const router = useRouter()
const userExists = ref(false)

// Vérifier si l'utilisateur existe
const checkUserExists = async () => {
  try {
    await axios.get(`/users/read/${route.params.id_user}`, {
      withCredentials: true,
    })
    userExists.value = true
  } catch (err) {
    // Si l'utilisateur n'existe pas (404) ou autre erreur, rediriger vers la page 404
    router.push('/404')
  }
}

onMounted(async () => {
  await checkUserExists()
})
</script>

<template>
  <main v-if="userExists" class="profil-view">
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
