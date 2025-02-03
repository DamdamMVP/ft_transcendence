import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/authStore'
import { useFriendStore } from '../stores/friendStore'
// Singleton pattern for WebSocket
let socket = null
const onlineUsers = ref(new Set())

export function useUserStatus() {
	const authStore = useAuthStore()
  const fetchOnlineUsers = async () => {
    try {
        const response = await axios.get('/users/list_online')
        // Extract user IDs from response
        const users = response.data.online_users.map(user => user.user__id)
        onlineUsers.value = new Set(users)
        
        // Update friends status
        const friendStore = useFriendStore()
        friendStore.friends.forEach(friend => {
            const isOnline = onlineUsers.value.has(friend.id)
            friendStore.updateFriendStatus(friend.id, isOnline)
        })
        
        console.log('Online users:', Array.from(onlineUsers.value))
    } catch (error) {
        console.error('Error fetching online users:', error)
        onlineUsers.value = new Set()
    }
}


  const initializeWebSocket = () => {
    if (socket) {
      console.log('WebSocket already initialized')
      return
    }

    if (!authStore.isAuthenticated) {
      console.log('Not connecting WebSocket: user not authenticated')
      return
    }

    console.log('Connecting to WebSocket...')
    socket = new WebSocket('/ws/status/')

    socket.onopen = () => {
		console.log('WebSocket connected')
		fetchOnlineUsers()
		// Send regular heartbeat
		setInterval(() => {
		  if (socket?.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify({ type: 'heartbeat' }))
		  }
		}, 10000)
	  }

	socket.onmessage = (event) => {
		try {
		  const data = JSON.parse(event.data)
		  console.log('WebSocket message received:', data)
	  
		  if (data.type === 'user_status') {
			// Create a new Set to trigger reactivity
			const updatedUsers = new Set(onlineUsers.value)
			
			if (data.is_online) {
			  updatedUsers.add(data.user_id)
			} else {
			  updatedUsers.delete(data.user_id)
			}
	  
			// Complete Set replacement
			onlineUsers.value = updatedUsers
	  
			// Reactive store update
			const friendStore = useFriendStore()
			friendStore.updateFriendStatus(data.user_id, data.is_online)
	  
			// Force UI update if needed
			friendStore.friends = [...friendStore.friends]
		  }
		} catch (error) {
		  console.error('Error processing WebSocket message:', error)
		}
	  }

    socket.onclose = (event) => {
      console.log('WebSocket closed:', event)
      socket = null
      onlineUsers.value.clear()
      if (authStore.isAuthenticated) {
        console.log('WebSocket disconnected, attempting to reconnect...')
        setTimeout(initializeWebSocket, 1000)
      } else {
        console.log(
          'WebSocket disconnected, not reconnecting (user not authenticated)'
        )
      }
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      socket = null
    }
  }

  const closeWebSocket = () => {
    if (socket) {
      console.log('Closing WebSocket connection...')
      socket.close()
      socket = null
      onlineUsers.value.clear()
    }
  }

  const isUserOnline = (userId) => {
    return onlineUsers.value.has(userId)
  }

  watch(
    () => authStore.isAuthenticated,
    (isAuthenticated) => {
      if (isAuthenticated) {
        initializeWebSocket()
      } else {
        closeWebSocket()
      }
    }
  )

  return {
    initializeWebSocket,
    closeWebSocket,
    isUserOnline,
    onlineUsers,
  }
}
