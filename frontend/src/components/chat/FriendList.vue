<template>
  <div v-if="authStore.isAuthenticated" class="friend-list-container">
    <!-- Icône de message flottante -->
    <div class="message-icon" @click="toggleExpand">
      <span class="material-icons">chat</span>
      <div v-if="friendStore.onlineFriends.length" class="online-badge">
        {{ friendStore.onlineFriends.length }}
      </div>
    </div>

    <!-- Panel de la friend list -->
    <div v-if="isExpanded" class="friend-list">
      <div class="friend-list__header" @click="toggleExpand">
        <h3>{{ $t('friendList.title') }}</h3>
        <span class="friend-list__online-count"
          >{{ friendStore.onlineFriends.length }}
          {{ $t('friendList.online') }}</span
        >
      </div>

      <div class="friend-list__content">
        <div class="friend-list__search">
          <input
            type="text"
            v-model="searchQuery"
            :placeholder="$t('friendList.search')"
          />
        </div>

        <div class="friend-list__friends">
          <FriendItem
            v-for="friend in filteredFriends"
            :key="friend.id"
            :friend="friend"
            @chat="startChat"
            @block="blockUser"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { useFriendStore } from '../stores/friendStore'
import AddFriendIcon from '../icons/AddFriendIcon.vue'
import FriendItem from './FriendItem.vue'

const authStore = useAuthStore()
const friendStore = useFriendStore()

const isExpanded = ref(false)
const searchQuery = ref('')
const newFriendUsername = ref('')

// Charger la liste d'amis au montage du composant
onMounted(() => {
  friendStore.loadFriends()
})

const filteredFriends = computed(() => {
  return friendStore.filteredFriends(searchQuery.value)
})

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const startChat = (friend) => {
  // TODO: Implémenter la logique de chat
  console.log('Start chat with:', friend.username)
}

const blockUser = async (friend) => {
  await friendStore.blockUser(friend.id)
}

const addFriend = async () => {
  if (newFriendUsername.value.trim()) {
    await friendStore.addFriend(newFriendUsername.value.trim())
    newFriendUsername.value = ''
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
  width: 300px;
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

.friend-list__header h3 {
  margin: 0;
  font-size: 1rem;
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

.friend-list__add-icon {
  width: 20px;
  height: 20px;
  color: white;
}
</style>
