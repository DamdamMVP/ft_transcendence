import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

export function useUserStatus() {
  const socket = ref(null)
  const onlineUsers = ref(new Set())
  const authStore = useAuthStore()

  const fetchOnlineUsers = async () => {
    try {
      const response = await axios.get('/users/list_online')
      onlineUsers.value = new Set(response.data)
      console.log('Online users:', Array.from(onlineUsers.value))
    } catch (error) {
      console.error('Error fetching online users:', error)
    }
  }

  const connectWebSocket = () => {
    if (!authStore.isAuthenticated) {
      console.log('Not connecting WebSocket: user not authenticated')
      return
    }

    console.log('Connecting to WebSocket...')
    socket.value = new WebSocket('/ws/status/')

    socket.value.onopen = () => {
      console.log('WebSocket connected')
      fetchOnlineUsers() // Récupérer la liste initiale une fois connecté
    }

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('WebSocket message received:', data)
      if (data.type === 'user_status') {
        if (data.is_online) {
          onlineUsers.value.add(data.user_id)
        } else {
          onlineUsers.value.delete(data.user_id)
        }
        console.log('Updated online users:', Array.from(onlineUsers.value))
      }
    }

    socket.value.onclose = () => {
      if (authStore.isAuthenticated) {
        console.log('WebSocket disconnected, attempting to reconnect...')
        setTimeout(connectWebSocket, 1000)
      } else {
        console.log(
          'WebSocket disconnected, not reconnecting (user not authenticated)'
        )
      }
    }

    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  const closeWebSocket = () => {
    if (socket.value) {
      console.log('Closing WebSocket connection...')
      socket.value.close()
      socket.value = null
      onlineUsers.value.clear()
    }
  }

  const isUserOnline = (userId) => {
    const isOnline = onlineUsers.value.has(userId)
    console.log('Checking online status for user', userId, ':', isOnline)
    return isOnline
  }

  // Watch for authentication changes
  watch(
    () => authStore.isAuthenticated,
    (isAuthenticated) => {
      if (isAuthenticated) {
        connectWebSocket()
      } else {
        closeWebSocket()
      }
    }
  )

  onMounted(() => {
    if (authStore.isAuthenticated) {
      connectWebSocket()
    }
  })

  onUnmounted(() => {
    closeWebSocket()
  })

  return {
    isUserOnline,
    onlineUsers,
  }
}
