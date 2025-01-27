<script setup>
import { ref, watch } from 'vue'

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

const show = ref(true)
let timeout = null

const startTimer = () => {
  show.value = true
  if (timeout) clearTimeout(timeout)
  timeout = setTimeout(() => {
    show.value = false
  }, props.duration)
}

watch(
  () => props.message,
  () => {
    if (props.message) {
      startTimer()
    }
  },
  { immediate: true }
)
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
