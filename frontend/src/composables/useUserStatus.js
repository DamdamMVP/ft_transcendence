import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

// Singleton pattern pour le WebSocket
let socket = null
const onlineUsers = ref(new Set())

export function useUserStatus() {
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
    }

    socket.onmessage = (event) => {
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
    onlineUsers
  }
}
