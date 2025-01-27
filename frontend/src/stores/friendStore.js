import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFriendStore = defineStore('friend', () => {
  // État
  const friends = ref([])
  const blockedUsers = ref([])

  // Getters
  const onlineFriends = computed(() => {
    return friends.value.filter((friend) => friend.isOnline)
  })

  const filteredFriends = computed(() => (searchQuery) => {
    return friends.value.filter((friend) =>
      friend.username.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  // Actions
  const addFriend = async (username) => {
    // TODO: Appel API pour ajouter un ami
    const newFriend = {
      id: Date.now(), // Temporaire, à remplacer par l'ID de l'API
      username,
      isOnline: false,
    }
    friends.value.push(newFriend)
  }

  const removeFriend = async (friendId) => {
    // TODO: Appel API pour supprimer un ami
    friends.value = friends.value.filter((friend) => friend.id !== friendId)
  }

  const blockUser = async (userId) => {
    // TODO: Appel API pour bloquer un utilisateur
    blockedUsers.value.push(userId)
    // Retirer l'utilisateur de la liste d'amis s'il y est
    friends.value = friends.value.filter((friend) => friend.id !== userId)
  }

  const unblockUser = async (userId) => {
    // TODO: Appel API pour débloquer un utilisateur
    blockedUsers.value = blockedUsers.value.filter((id) => id !== userId)
  }

  const updateFriendStatus = (userId, isOnline) => {
    const friend = friends.value.find((f) => f.id === userId)
    if (friend) {
      friend.isOnline = isOnline
    }
  }

  const loadFriends = async () => {
    // TODO: Appel API pour charger la liste d'amis
    // Pour le moment, on utilise des données de test
    friends.value = [
      { id: 1, username: 'User1', isOnline: true },
      { id: 2, username: 'User2', isOnline: false },
    ]
  }

  return {
    // État
    friends,
    blockedUsers,

    // Getters
    onlineFriends,
    filteredFriends,

    // Actions
    addFriend,
    removeFriend,
    blockUser,
    unblockUser,
    updateFriendStatus,
    loadFriends,
  }
})
