<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
import FriendList from './components/FriendList.vue'
</script>

<template>
  <div class="app">
    <NavBar />
    <RouterView />
    <FriendList />
  </div>
</template>

<style>
.app {
  width: 100vw;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background: var(--background-color);
}
</style>
