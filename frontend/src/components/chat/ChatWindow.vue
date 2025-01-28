<template>
  <div v-if="isOpen" class="chat-window">
    <div class="chat-window__header">
      <div class="chat-window__user-info">
        <span class="chat-window__username">{{ friend.username }}</span>
      </div>
      <button @click="$emit('close')" class="chat-window__close-btn">
        <span class="material-icons">{{ $t('chat.close') }}</span>
      </button>
    </div>

    <div class="chat-window__messages">
      <!-- Ici nous simulerons quelques messages pour l'exemple -->
      <div class="message message--received">
        <p>Hello!</p>
        <span class="message__time">10:00</span>
      </div>
      <div class="message message--sent">
        <p>Hi there!</p>
        <span class="message__time">10:01</span>
      </div>
    </div>

    <div class="chat-window__input">
      <input
        type="text"
        v-model="messageText"
        @keyup.enter="sendMessage"
        :placeholder="$t('chat.typemessage')"
      />
      <button @click="sendMessage" class="chat-window__send-btn">
        <span class="material-icons">{{ $t('chat.send') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  friend: {
    type: Object,
    required: true,
  },
  isOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'send-message'])
const messageText = ref('')

const sendMessage = () => {
  if (messageText.value.trim()) {
    emit('send-message', {
      text: messageText.value,
      timestamp: new Date(),
      to: props.friend.id,
    })
    messageText.value = ''
  }
}
</script>

<style scoped>
.chat-window {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 400px;
  background-color: var(--background-color);
  border: 1px solid var(--secondary-color);
  border-radius: 8px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.chat-window__header {
  padding: 10px 15px;
  background-color: var(--primary-color);
  color: var(--text-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.chat-window__user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-window__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.chat-window__username {
  font-weight: 500;
  color: white;
}

.chat-window__close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: white;
}

.chat-window__close-btn:hover {
  opacity: 0.8;
}

.chat-window__messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  background-color: var(--background-color);
}

.message {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 16px;
  position: relative;
}

.message--received {
  align-self: flex-start;
  background-color: var(--secondary-color);
  color: var(--text-color);
}

.message--sent {
  align-self: flex-end;
  background-color: var(--primary-color);
  color: white;
}

.message__time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
  display: block;
}

.chat-window__input {
  padding: 10px;
  display: flex;
  gap: 8px;
  border-top: 1px solid var(--secondary-color);
  background-color: var(--background-color);
}

.chat-window__input input {
  flex: 1;
  padding: 8px;
  border: 1px solid var(--secondary-color);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--text-color);
}

.chat-window__send-btn {
  background-color: var(--primary-color);
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  padding: 8px;
}

.chat-window__send-btn:hover {
  background-color: var(--primary-hover-color);
}
</style>
