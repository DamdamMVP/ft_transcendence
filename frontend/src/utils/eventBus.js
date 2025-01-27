import { ref } from 'vue'

const bus = {
  events: ref(new Map()),

  emit(event, data) {
    if (this.events.value.has(event)) {
      this.events.value.get(event).forEach(callback => callback(data))
    }
  },

  on(event, callback) {
    if (!this.events.value.has(event)) {
      this.events.value.set(event, [])
    }
    this.events.value.get(event).push(callback)
  },

  off(event, callback) {
    if (this.events.value.has(event)) {
      const callbacks = this.events.value.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }
}

export default bus
