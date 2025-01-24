<script setup>
import IconGolem from './icons/IconGolem.vue'
import ThemeSelector from './ThemeSelector.vue'

defineEmits(['showSignIn', 'showRegister'])
</script>

<template>
  <div class="header">
    <div class="logo-container">
      <div class="logo-border">
        <IconGolem style="color: #000000"></IconGolem>
      </div>
    </div>
    <div class="spacer"></div>
    <ThemeSelector />
    <div class="auth-buttons">
      <button class="sign-in-button" @click="$emit('showSignIn')">
        Sign in
      </button>
      <button class="register-button" @click="$emit('showRegister')">
        Register
      </button>
    </div>
  </div>
</template>

<style scoped>
.header {
  align-self: stretch;
  padding: 32px 0;
  margin: 0;
  width: 100vw;
  background: var(--background-color);
  border-bottom: 1px solid var(--secondary-color);
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 24px;
  box-sizing: border-box;
}

.logo-container {
  padding-left: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo-border {
  width: 50px;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.spacer {
  flex: 1;
}

.auth-buttons {
  padding-right: 32px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.sign-in-button,
.register-button {
  flex: 1;
  height: 32px;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid;
  font-family: Inter, sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 16px;
  cursor: pointer;
  transition:
    background 0.3s,
    border-color 0.3s,
    color 0.3s;
}

.sign-in-button {
  background: var(--background-color);
  border-color: var(--secondary-color);
  color: var(--text-color);
}

.sign-in-button:hover {
  background: var(--secondary-color);
  color: var(--background-color);
}

.register-button {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--background-color);
}

.register-button:hover {
  background: var(--info-color);
  border-color: var(--info-color);
}
</style>
