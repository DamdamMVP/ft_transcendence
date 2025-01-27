<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'error',
  },
  duration: {
    type: Number,
    default: 3000,
  },
})

const emit = defineEmits(['close'])
const show = ref(false)
let timeout = null

const hideNotification = () => {
  show.value = false
  emit('close')
}

const showNotification = () => {
  // Nettoyer le timeout existant si présent
  if (timeout) {
    clearTimeout(timeout)
  }
  
  // Forcer la réinitialisation en cachant puis montrant
  show.value = false
  setTimeout(() => {
    show.value = true
    timeout = setTimeout(hideNotification, props.duration)
  }, 50)
}

// Regarder les changements de message
watch(() => props.message, (newMessage, oldMessage) => {
  if (newMessage && (newMessage !== oldMessage || !show.value)) {
    showNotification()
  }
})

// Nettoyer le timeout lors de la destruction du composant
onUnmounted(() => {
  if (timeout) {
    clearTimeout(timeout)
  }
})

// Montrer la notification initialement si un message est présent
if (props.message) {
  showNotification()
}
</script>

<template>
  <Transition name="notification">
    <div v-if="show" :class="['notification', type]">
      {{ message }}
    </div>
  </Transition>
</template>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 24px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.error {
  background-color: var(--error-color);
}

.success {
  background-color: var(--success-color);
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
