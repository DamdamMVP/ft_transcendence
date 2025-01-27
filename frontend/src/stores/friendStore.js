import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

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
    console.log('🔄 Début du chargement des amis...')
    try {
      const response = await axios.get('http://localhost:8000/users/friends', {
        withCredentials: true,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
      })

      console.log("📥 Réponse de l'API:", response)

      if (response.status === 200) {
        friends.value = response.data.map((friend) => ({
          ...friend,
          isOnline: false,
        }))
        console.log("✅ Liste d'amis mise à jour:", friends.value)
      }
    } catch (error) {
      console.log('❌ Erreur détaillée:', {
        message: error.message,
        response: error.response,
        config: error.config,
      })
      friends.value = []
    }
  }

  // Réinitialiser le store
  const reset = () => {
    friends.value = []
    blockedUsers.value = []
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
    reset,
  }
})
