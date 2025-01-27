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
    try {
      const addFriendResponse = await axios.post(
        `http://localhost:8000/users/friends/add/${username}`,
        {},
        {
          withCredentials: true,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
        }
      )

      if (addFriendResponse.status === 200) {
        await loadFriends()
        return true
      }
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error('Utilisateur non trouvé')
      } else if (error.response?.status === 400) {
        if (error.response?.data?.error === 'You cannot add yourself as a friend') {
          throw new Error('Vous ne pouvez pas vous ajouter vous-même comme ami')
        } else if (error.response?.data?.error === 'This user is already your friend') {
          throw new Error('Cet utilisateur est déjà votre ami')
        } else {
          throw new Error(error.response?.data?.error || "Erreur lors de l'ajout d'ami")
        }
      } else {
        throw new Error("Erreur lors de l'ajout d'ami")
      }
    }
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
    try {
      const response = await axios.get('http://localhost:8000/users/friends', {
        withCredentials: true,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
      })

      if (response.status === 200) {
        friends.value = response.data.map((friend) => ({
          ...friend,
          isOnline: false,
        }))
      }
    } catch (error) {
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
