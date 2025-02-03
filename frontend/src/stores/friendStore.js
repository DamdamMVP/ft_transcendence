import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useFriendStore = defineStore('friend', () => {
  // State
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
        `/users/friends/add/${username}`,
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
        throw new Error('User not found')
      } else if (error.response?.status === 400) {
        if (
          error.response?.data?.error === 'You cannot add yourself as a friend'
        ) {
          throw new Error('You cannot add yourself as a friend')
        } else if (
          error.response?.data?.error === 'This user is already your friend'
        ) {
          throw new Error('This user is already your friend')
        } else {
          throw new Error(
            error.response?.data?.error || 'Error adding friend'
          )
        }
      } else {
        throw new Error('Error adding friend')
      }
    }
  }

  const removeFriend = async (username) => {
    try {
      console.log('Removing friend:', username)
      const response = await axios.post(
        `/users/friends/remove/${username}`,
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
        await loadFriends()
        return true
      }
    } catch (error) {
      console.error('Error removing friend:', error)
      if (error.response?.status === 404) {
        throw new Error('User not found')
      } else {
        throw new Error(
          error.response?.data?.error ||
            'Error removing friend'
        )
      }
    }
  }

  const blockUser = async (username) => {
    try {
      console.log('Blocking user:', username)

      // First find the ID of the user to block in the friends list
      const userToBlock = friends.value.find(
        (friend) => friend.username === username
      )
      console.log('User to block:', userToBlock)
      if (!userToBlock) {
        throw new Error('User not found in friends list')
      }

      // Keep ID for later
      const userIdToBlock = userToBlock.id

      // Remove from friends list
      await removeFriend(username)

      // Then block the user with the saved ID
      console.log('Sending block request with ID:', userIdToBlock)
      const response = await axios.post(
        '/users/block',
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
        // Update blocked users list
        const blockedResponse = await axios.get(
          `${import.meta.env.VITE_BASE_URL}/users/list_blocked`,
          {
            withCredentials: true,
            headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
            },
          }
        )

        if (blockedResponse.status === 200) {
          blockedUsers.value = blockedResponse.data
          await loadFriends()
          console.log('Updated blocked users list and friends list')
        }
        return true
      }
    } catch (error) {
      console.error('Error blocking user:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)
      if (error.response?.status === 404) {
        throw new Error('User not found')
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
      } else {
        throw new Error('Error blocking user')
      }
    }
  }

  const unblockUser = async (userId) => {
    blockedUsers.value = blockedUsers.value.filter((id) => id !== userId)
  }

  const updateFriendStatus = (userId, isOnline) => {
    const friend = friends.value.find((f) => f.id === userId)
    if (friend) {
      friend.isOnline = isOnline
	  console.log(`Updated status for user ${userId} to ${isOnline}`)
    }
  }

  const loadFriends = async () => {
    try {
      console.log('Loading friends list')
      const response = await axios.get('/users/friends', {
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

  // Reset store
  const reset = () => {
    friends.value = []
    blockedUsers.value = []
  }

  return {
    // State
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
