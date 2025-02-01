<template>
  <div class="catch-menu">
    <h1>CATCH</h1>
    <div class="menu-container">
      <router-link to="/catch/tomandjerry" class="menu-item">
        <div class="menu-box">
          <h2>Tom & Jerry</h2>
          <p>Chat contre souris</p>
        </div>
      </router-link>

      <router-link to="/catch/fortytwo" class="menu-item">
        <div class="menu-box">
          <h2>42</h2>
          <p>Version 42</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CatchMenu'
}
</script>

<style scoped>
.catch-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #1a1a1a;
  color: white;
}

h1 {
  color: #3498db;
  font-size: 3rem;
  margin-bottom: 2rem;
}

.menu-container {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.menu-item {
  text-decoration: none;
  color: white;
}

.menu-box {
  background-color: #2c3e50;
  border: 2px solid #3498db;
  border-radius: 8px;
  padding: 2rem;
  width: 200px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.menu-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
}

h2 {
  margin: 0 0 1rem 0;
  color: #3498db;
}

p {
  margin: 0;
  color: #95a5a6;
}
</style>
