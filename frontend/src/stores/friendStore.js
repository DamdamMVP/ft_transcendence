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

  const removeFriend = async (username) => {
    try {
      console.log('Removing friend:', username)
      const response = await axios.post(
        `http://localhost:8000/users/friends/remove/${username}`,
        {},
        {
          withCredentials: true,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
        }
      )

      if (response.status === 200) {
        console.log('Friend removed successfully')
        await loadFriends() // Recharger la liste des amis
        return true
      }
    } catch (error) {
      console.error('Error removing friend:', error)
      if (error.response?.status === 404) {
        throw new Error('Utilisateur non trouvé')
      } else {
        throw new Error(error.response?.data?.error || "Erreur lors de la suppression de l'ami")
      }
    }
  }

  const blockUser = async (username) => {
    try {
      console.log('Blocking user:', username)
      
      // D'abord trouver l'ID de l'utilisateur à bloquer dans la liste des amis
      const userToBlock = friends.value.find(friend => friend.username === username)
      console.log('User to block:', userToBlock)
      if (!userToBlock) {
        throw new Error('Utilisateur non trouvé dans la liste des amis')
      }

      // Garder l'ID pour plus tard
      const userIdToBlock = userToBlock.id

      // Supprimer de la liste d'amis
      await removeFriend(username)

      // Ensuite bloquer l'utilisateur avec l'ID sauvegardé
      console.log('Sending block request with ID:', userIdToBlock)
      const response = await axios.post(
        'http://localhost:8000/users/block',
        { blocked_id: userIdToBlock },
        {
          withCredentials: true,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
        }
      )

      console.log('Block response:', response)

      if (response.status === 200 || response.status === 201) {
        console.log('User blocked successfully')
        // Mettre à jour la liste des utilisateurs bloqués
        const blockedResponse = await axios.get('http://localhost:8000/users/list_blocked', {
          withCredentials: true,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
        })

        if (blockedResponse.status === 200) {
          blockedUsers.value = blockedResponse.data
          await loadFriends() // Recharger la liste des amis une dernière fois pour s'assurer qu'elle est à jour
          console.log('Updated blocked users list and friends list')
        }
        return true
      }
    } catch (error) {
      console.error('Error blocking user:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)
      if (error.response?.status === 404) {
        throw new Error('Utilisateur non trouvé')
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
      } else {
        throw new Error("Erreur lors du blocage de l'utilisateur")
      }
    }
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
      console.log('Loading friends list')
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
        console.log('Friends list updated:', friends.value)
      }
    } catch (error) {
      console.error('Error loading friends:', error)
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
