<script setup>
import { useAuthStore } from '../stores/authStore'
import { computed } from 'vue'

const authStore = useAuthStore()

// URL de l'image par défaut avec le bon chemin backend
const defaultProfilePicture = 'http://localhost:8000/media/profile_pictures/default.jpg'

const profilePhotoUrl = computed(() => {
  return authStore.user?.profile_picture
    ? `http://localhost:8000${authStore.user.profile_picture}`
    : defaultProfilePicture
})
</script>

<template>
  <div class="profile-container">
    <div class="profile-card">
      <h2 class="profile-name">
        {{ authStore.user?.username || 'Utilisateur' }}
      </h2>
      <img
        :src="profilePhotoUrl"
        :alt="authStore.user?.username || 'Profile Picture'"
        class="profile-picture"
      />
      <p class="profile-stats" v-if="authStore.user?.stats">
        W: {{ authStore.user.stats.wins || 0 }} | L:
        {{ authStore.user.stats.losses || 0 }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.profile-card {
  width: 250px;
  padding: 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  background-color: var(--background-color);
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.profile-picture {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 16px;
}

.profile-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--text-color);
}

.profile-stats {
  font-size: 16px;
  color: var(--text-color);
}
</style>
