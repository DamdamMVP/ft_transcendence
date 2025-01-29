<template>
  <div class="general-channel" @click="startChat">
    <div class="general-channel__info">
      <span class="general-channel__hash">#</span>
      <span class="general-channel__name">general</span>
    </div>
  </div>
  <div class="general-channel__separator"></div>
</template>

<script setup>
const emit = defineEmits(['chat'])

const startChat = () => {
  emit('chat', {
    id: 'general',
    username: 'general',
    isChannel: true,
  })
}
</script>

<style scoped>
.general-channel {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
  padding-left: 8px;
  border-radius: 4px;
  height: 40px;
}

.general-channel__separator {
  border-bottom: 1px solid var(--secondary-color);
}

.general-channel:hover {
  background-color: var(--secondary-color);
}

.general-channel__info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.general-channel__hash {
  color: var(--primary-color);
  font-weight: 500;
  font-size: 1em;
}

.general-channel__name {
  color: var(--text-color);
  font-weight: 500;
  font-size: 0.9em;
}
</style>
