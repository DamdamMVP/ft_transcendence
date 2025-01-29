<template>
  <div v-if="authStore.isAuthenticated" class="friend-list-container">
    <Notification
      :message="notification.message"
      :type="notification.type"
      v-if="notification.show"
      @close="notification.show = false"
    />

    <!-- Icône de message flottante -->
    <div class="message-icon" @click="toggleExpand">
      <span class="material-icons">chat</span>
      <div v-if="onlineFriendsCount" class="online-badge">
        {{ onlineFriendsCount }}
      </div>
    </div>

    <!-- Panel de la friend list -->
    <div
      v-if="isExpanded && !activeChatFriend"
      class="friend-list"
      :class="{ 'friend-list--expanded': isExpanded }"
    >
      <div class="friend-list__header" @click="toggleExpand">
        <div class="friend-list__title">
          {{ $t('friendList.title') }}
          <span class="friend-list__count">({{ onlineFriendsCount }})</span>
        </div>
      </div>

      <div v-if="isExpanded" class="friend-list__content">
        <div class="friend-list__search">
          <input
            type="text"
            v-model="searchQuery"
            :placeholder="$t('friendList.search')"
          />
        </div>

        <div class="friend-list__channels">
          <GeneralChannel @chat="startChat" />
        </div>

        <div class="friend-list__friends">
          <FriendItem
            v-for="friend in filteredFriends"
            :key="friend.id"
            :friend="friend"
            @chat="startChat"
            @block="blockUser"
            @delete="deleteFriend"
          />
        </div>

        <div class="friend-list__add">
          <input
            type="text"
            v-model="newFriendUsername"
            :placeholder="$t('friendList.addFriend')"
            @keyup.enter="addFriend"
          />
          <button
            @click="addFriend"
            class="friend-list__add-btn"
            :title="$t('friendList.addFriend')"
          >
            <AddFriendIcon class="friend-list__add-icon" />
          </button>
        </div>
      </div>
    </div>

    <!-- Fenêtres de chat -->
    <ChatWindow
      v-if="activeChatFriend && isExpanded"
      :friend="activeChatFriend"
      :is-open="true"
      @close="closeChat"
      @send-message="handleSendMessage"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import { useFriendStore } from '../../stores/friendStore'
import { useUserStatus } from '../../composables/useUserStatus'
import AddFriendIcon from '../icons/AddFriendIcon.vue'
import FriendItem from './FriendItem.vue'
import GeneralChannel from './GeneralChannel.vue'
import Notification from '../Notification.vue'
import ChatWindow from './ChatWindow.vue'

const authStore = useAuthStore()
const friendStore = useFriendStore()
const { onlineUsers } = useUserStatus()

const isExpanded = ref(false)
const searchQuery = ref('')
const newFriendUsername = ref('')
const activeChatFriend = ref(null)
const notification = ref({
  show: false,
  message: '',
  type: 'error',
})
const isAddingFriend = ref(false)

const onlineFriendsCount = computed(() => {
  return friendStore.friends.filter((friend) =>
    onlineUsers.value.has(friend.id)
  ).length
})

const filteredFriends = computed(() => {
  return friendStore.friends.filter((friend) =>
    friend.username.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// Charger la liste d'amis au montage du composant et quand l'authentification change
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await friendStore.loadFriends()
  }
})

// Surveiller les changements d'authentification
watch(
  () => authStore.isAuthenticated,
  async (newValue) => {
    if (newValue) {
      await friendStore.loadFriends()
    } else {
      friendStore.friends = []
    }
  }
)

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const startChat = (friend) => {
  // Si c'est le canal général
  if (friend.isChannel) {
    activeChatFriend.value = friend
  } else {
    // Si c'est un ami normal
    activeChatFriend.value = friend
  }
}

const closeChat = () => {
  activeChatFriend.value = null
}

const handleSendMessage = (message) => {
  console.log('Message envoyé:', message)
  // Ici vous pourrez ajouter la logique pour envoyer le message via l'API
}

const blockUser = async (friend) => {
  try {
    await friendStore.blockUser(friend.username)
    showNotification('Utilisateur bloqué avec succès', 'success')
  } catch (error) {
    showNotification(error.message, 'error')
  }
}

const deleteFriend = async (friend) => {
  try {
    await friendStore.removeFriend(friend.username)
    showNotification('Ami supprimé avec succès', 'success')
  } catch (error) {
    showNotification(error.message, 'error')
  }
}

const addFriend = async () => {
  if (newFriendUsername.value.trim()) {
    try {
      await friendStore.addFriend(newFriendUsername.value.trim())
      newFriendUsername.value = ''
      showNotification('Ami ajouté avec succès', 'success')
    } catch (error) {
      showNotification(error.message, 'error')
    }
  }
}

const showNotification = (message, type = 'error') => {
  notification.value = {
    show: true,
    message,
    type,
  }
}
</script>

<style scoped>
.friend-list-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.message-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;
}

.message-icon:hover {
  transform: scale(1.1);
  background-color: var(--primary-hover-color);
}

.message-icon .material-icons {
  color: white;
  font-size: 24px;
}

.online-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: var(--success-color);
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.friend-list {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 400px;
  background-color: var(--background-color);
  border: 1px solid var(--secondary-color);
  border-radius: 8px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.friend-list__header {
  padding: 10px 15px;
  background-color: var(--primary-color);
  color: var(--text-color);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}

.friend-list__title {
  font-size: 1rem;
  margin: 0;
}

.friend-list__count {
  font-size: 0.8rem;
  color: var(--text-color);
  margin-left: 5px;
}

.friend-list__actions {
  display: flex;
  align-items: center;
}

.friend-list__add-btn {
  background-color: var(--primary-color);
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  padding: 8px;
}

.friend-list__add-btn:hover {
  background-color: var(--primary-hover-color);
}

.friend-list__content {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

.friend-list__search input,
.friend-list__add input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--secondary-color);
  border-radius: 4px;
  margin-bottom: 10px;
  background-color: var(--background-color);
  color: var(--text-color);
  box-sizing: border-box;
}

.friend-list__friends {
  margin-bottom: 10px;
}

.friend-list__add {
  display: flex;
  gap: 8px;
  padding-top: 10px;
}

.friend-list__add-icon {
  width: 20px;
  height: 20px;
  color: white;
}

.friend-list__channels {
  padding: 0px;
}
</style>
