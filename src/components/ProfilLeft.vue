<script setup>
import { useProfilDatasStore } from '../stores/profilDatas'

const profilDatas = useProfilDatasStore()
</script>

<template>
  <div class="profile-container">
    <div class="profile-card">
      <h2 class="profile-name">{{ profilDatas.matches[0].name }}</h2>
      <img
        :src="profilDatas.matches[0].profilePicture"
        alt="Profile Picture"
        class="profile-picture"
      />
      <p class="profile-stats">
        W: {{ profilDatas.matches[0].wins }} | L:
        {{ profilDatas.matches[0].losses }}
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
