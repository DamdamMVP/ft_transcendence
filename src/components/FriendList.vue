<template>
  <div v-if="authStore.isAuthenticated" class="friend-list-container">
    <!-- Icône de message flottante -->
    <div class="message-icon" @click="toggleExpand">
      <span class="material-icons">chat</span>
      <div v-if="onlineFriends.length" class="online-badge">{{ onlineFriends.length }}</div>
    </div>

    <!-- Panel de la friend list -->
    <div v-if="isExpanded" class="friend-list">
      <div class="friend-list__header" @click="toggleExpand">
        <h3>{{ $t('friendList.title') }}</h3>
        <span class="friend-list__online-count">{{ onlineFriends.length }} {{ $t('friendList.online') }}</span>
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
          <div 
            v-for="friend in filteredFriends" 
            :key="friend.id" 
            class="friend-list__friend"
          >
            <div class="friend-list__friend-info">
              <div class="friend-list__status-indicator" :class="{ 'online': friend.isOnline }"></div>
              <span class="friend-list__friend-name">{{ friend.username }}</span>
            </div>
            <div class="friend-list__actions">
              <button @click="startChat(friend)" class="friend-list__action-btn" :title="$t('friendList.chat')">
                <span class="material-icons">{{ $t('friendList.icons.chat') }}</span>
              </button>
              <button @click="blockUser(friend)" class="friend-list__action-btn" :title="$t('friendList.block')">
                <span class="material-icons">{{ $t('friendList.icons.block') }}</span>
              </button>
            </div>
          </div>
        </div>

        <div class="friend-list__add">
          <input 
            type="text" 
            v-model="newFriendUsername" 
            :placeholder="$t('friendList.addFriend')"
            @keyup.enter="addFriend"
          />
          <button @click="addFriend" class="friend-list__add-btn" :title="$t('friendList.addFriend')">
            <span class="material-icons">{{ $t('friendList.icons.addFriend') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/authStore'

const authStore = useAuthStore()
const isExpanded = ref(false)
const searchQuery = ref('')
const newFriendUsername = ref('')
const friends = ref([
  // Exemple de données pour le développement
  { id: 1, username: 'User1', isOnline: true },
  { id: 2, username: 'User2', isOnline: false },
])

const onlineFriends = computed(() => {
  return friends.value.filter(friend => friend.isOnline)
})

const filteredFriends = computed(() => {
  return friends.value.filter(friend => 
    friend.username.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const startChat = (friend) => {
  // TODO: Implémenter la logique de chat
  console.log('Start chat with:', friend.username)
}

const blockUser = (friend) => {
  // TODO: Implémenter la logique de blocage
  console.log('Block user:', friend.username)
}

const addFriend = () => {
  if (newFriendUsername.value.trim()) {
    // TODO: Implémenter la logique d'ajout d'ami
    console.log('Add friend:', newFriendUsername.value)
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
}

.friend-list__friend {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid var(--secondary-color);
}

.friend-list__friend-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.friend-list__status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--error-color);
}

.friend-list__status-indicator.online {
  background-color: var(--success-color);
}

.friend-list__actions {
  display: flex;
  gap: 5px;
}

.friend-list__action-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-color);
  padding: 4px;
}

.friend-list__action-btn:hover {
  color: var(--primary-color);
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
</style>
