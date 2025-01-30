<template>
  <div class="not-found">
    <h1>404</h1>
    <h2>{{ $t('error.pageNotFound') }}</h2>
    <p>{{ $t('error.pageNotFoundDesc') }}</p>
    <router-link to="/" class="home-link">
      {{ $t('error.backToHome') }}
    </router-link>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 65vh;
  text-align: center;
  padding: 2rem;
}

h1 {
  font-size: 6rem;
  margin: 0;
  color: #4caf50;
}

h2 {
  font-size: 2rem;
  margin: 1rem 0;
}

p {
  margin: 1rem 0 2rem;
  color: #666;
}

.home-link {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  background-color: #4caf50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.home-link:hover {
  background-color: #45a049;
}
</style>
