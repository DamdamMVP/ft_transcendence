<template>
  <div v-if="isOpen" class="chat-window">
    <div class="chat-window__header">
      <div class="chat-window__user-info">
        <span class="chat-window__username">{{ displayName }}</span>
      </div>
      <button @click="closeChat" class="chat-window__close-btn">
        <span class="material-icons">{{ $t('chat.close') }}</span>
      </button>
    </div>

    <div class="chat-window__messages" ref="messagesContainer">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="[
          'message',
          message.sender === currentUser.username
            ? 'message--sent'
            : 'message--received',
        ]"
      >
        <div class="message__header">
          <span class="message__sender">{{ message.sender }}</span>
          <span class="message__time">{{ formatTime(message.timestamp) }}</span>
        </div>
        <p class="message__content">{{ message.message }}</p>
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
      <button @click="inviteToPlay" class="chat-window__invite-btn">
        <span class="material-icons">{{ $t('chat.play') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { usePrivateChat } from '../../composables/usePrivateChat'
import { useAuthStore } from '../../stores/authStore'
import { useI18n } from 'vue-i18n'

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

const emit = defineEmits(['close'])
const messageText = ref('')
const messages = ref([])
const messagesContainer = ref(null)
const {
  connectToChat,
  disconnectFromChat,
  sendMessage: sendWebSocketMessage,
} = usePrivateChat()
const authStore = useAuthStore()
const { t } = useI18n()

// Obtenir l'utilisateur actuel directement depuis le store
const currentUser = computed(() => authStore.user)

// Détermine si c'est le canal général
const isGeneralChannel = computed(() => props.friend.isChannel)

// Obtient le nom d'affichage approprié
const displayName = computed(() =>
  isGeneralChannel.value ? '#general' : props.friend.username
)

const closeChat = () => {
  if (currentUser.value && props.friend) {
    if (isGeneralChannel.value) {
      disconnectFromChat('general', 'general')
    } else {
      disconnectFromChat(currentUser.value.username, props.friend.username)
    }
  }
  emit('close')
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = () => {
  if (!messageText.value.trim() || !currentUser.value || !props.friend) return

  let success
  if (isGeneralChannel.value) {
    success = sendWebSocketMessage('general', 'general', messageText.value)
  } else {
    success = sendWebSocketMessage(
      currentUser.value.username,
      props.friend.username,
      messageText.value
    )
  }

  if (success) {
    messageText.value = ''
  }
}

const inviteToPlay = () => {
  messageText.value = t('chat.invite')
  sendMessage()
}

// Initialiser la connexion WebSocket
let ws = null

onMounted(() => {
  if (props.isOpen && props.friend && currentUser.value) {
    if (isGeneralChannel.value) {
      ws = connectToChat('general', 'general')
    } else {
      ws = connectToChat(currentUser.value.username, props.friend.username)
    }

    if (ws) {
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.message !== undefined) {
            messages.value.push({
              message: data.message,
              sender: data.sender,
              timestamp: data.timestamp,
            })
            scrollToBottom()
          }
        } catch (error) {
          console.error('Error processing message:', error)
        }
      }
    }
  }
})

onUnmounted(() => {
  if (ws && currentUser.value && props.friend) {
    if (isGeneralChannel.value) {
      disconnectFromChat('general', 'general')
    } else {
      disconnectFromChat(currentUser.value.username, props.friend.username)
    }
  }
})

watch(
  () => props.isOpen,
  (newValue) => {
    if (newValue && props.friend && currentUser.value && !ws) {
      if (isGeneralChannel.value) {
        ws = connectToChat('general', 'general')
      } else {
        ws = connectToChat(currentUser.value.username, props.friend.username)
      }
    } else if (!newValue && ws && currentUser.value && props.friend) {
      if (isGeneralChannel.value) {
        disconnectFromChat('general', 'general')
      } else {
        disconnectFromChat(currentUser.value.username, props.friend.username)
      }
      ws = null
    }
  }
)
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

.chat-window__messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 15px;
  max-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  margin: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  max-width: 70%;
}

.message__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 0.8em;
}

.message__sender {
  font-weight: 500;
  color: var(--text-secondary-color);
}

.message__time {
  color: var(--text-secondary-color);
  margin-left: 8px;
}

.message__content {
  margin: 0;
  word-break: break-word;
}

.message--sent {
  background-color: var(--primary-color);
  color: white;
  margin-left: auto;
}

.message--sent .message__sender,
.message--sent .message__time {
  color: rgba(255, 255, 255, 0.8);
}

.message--received {
  background-color: var(--secondary-color);
  margin-right: auto;
}

.chat-window__input {
  padding: 15px;
  display: flex;
  gap: 10px;
  border-top: 1px solid var(--secondary-color);
}

.chat-window__input input {
  flex-grow: 1;
  padding: 8px 12px;
  border: 1px solid var(--secondary-color);
  border-radius: 20px;
  background-color: var(--background-color);
  color: var(--text-color);
}

.chat-window__close-btn,
.chat-window__send-btn,
.chat-window__invite-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-color);
  padding: 4px;
}

.chat-window__close-btn:hover,
.chat-window__send-btn:hover,
.chat-window__invite-btn:hover {
  color: var(--primary-color);
}
</style>
