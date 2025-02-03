import { ref } from 'vue'

export function usePrivateChat() {
  const chatConnections = ref(new Map())
  const reconnectAttempts = ref(new Map())
  const MAX_RECONNECT_ATTEMPTS = 5
  const RECONNECT_DELAY = 3000

  const getChatRoomName = (user1, user2) => {
    const sortedUsers = [user1, user2].sort()
    return `private_${sortedUsers[0]}_${sortedUsers[1]}`
  }

  const handleReconnect = async (roomName, currentUser, otherUser) => {
    const attempts = reconnectAttempts.value.get(roomName) || 0
    
    if (attempts < MAX_RECONNECT_ATTEMPTS) {
      console.log(`Reconnection attempt ${attempts + 1}/${MAX_RECONNECT_ATTEMPTS} for ${roomName}`)
      reconnectAttempts.value.set(roomName, attempts + 1)
      
      await new Promise(resolve => setTimeout(resolve, RECONNECT_DELAY))
      return connectToChat(currentUser, otherUser)
    } else {
      console.error(`Reconnection failed after ${MAX_RECONNECT_ATTEMPTS} attempts for ${roomName}`)
      reconnectAttempts.value.delete(roomName)
      return null
    }
  }

  const connectToChat = (currentUser, otherUser) => {
    const isGeneral = currentUser === 'general' && otherUser === 'general'
    const roomName = isGeneral ? 'general' : getChatRoomName(currentUser, otherUser)
    
    // Check if a connection exists and is active
    const existingConnection = chatConnections.value.get(roomName)
    if (existingConnection?.readyState === WebSocket.OPEN) {
      return existingConnection
    }

    // Close any existing connection that is not in the OPEN state
    if (existingConnection) {
      existingConnection.close()
      chatConnections.value.delete(roomName)
    }

    // Create new connection
    const wsUrl = isGeneral ? '/ws/chat/general/' : `/ws/chat/${roomName}/`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log(`Connected to ${roomName}`)
      reconnectAttempts.value.delete(roomName) // Reset reconnection attempts after success
    }

    ws.onclose = async (event) => {
      console.log(`Disconnected from ${roomName}`, event.code, event.reason)
      chatConnections.value.delete(roomName)
      
      // Attempt to reconnect if the connection was not closed intentionally
      if (event.code !== 1000) {
        await handleReconnect(roomName, currentUser, otherUser)
      }
    }

    ws.onerror = (error) => {
      console.error(`WebSocket error for ${roomName}:`, error)
    }

    chatConnections.value.set(roomName, ws)
    return ws
  }

  const sendMessage = (currentUser, otherUser, message) => {
    const isGeneral = currentUser === 'general' && otherUser === 'general'
    const roomName = isGeneral ? 'general' : getChatRoomName(currentUser, otherUser)
    const connection = chatConnections.value.get(roomName)

    if (!connection) {
      console.error(`No connection found for ${roomName}`)
      return false
    }

    if (connection.readyState !== WebSocket.OPEN) {
      console.error(`Connection not open for ${roomName}. State: ${connection.readyState}`)
      // Attempt to reconnect
      connectToChat(currentUser, otherUser)
      return false
    }

    try {
      connection.send(JSON.stringify({
        message: message,
        timestamp: new Date().toISOString(),
      }))
      return true
    } catch (error) {
      console.error(`Error sending message:`, error)
      return false
    }
  }
  const disconnectFromChat = (currentUser, otherUser) => {
    // If it's the general channel
    if (currentUser === 'general' && otherUser === 'general') {
      const connection = chatConnections.value.get('general')
      if (connection) {
        connection.close()
        chatConnections.value.delete('general')
      }
      return
    }

    // For private chats
    const roomName = getChatRoomName(currentUser, otherUser)
    const connection = chatConnections.value.get(roomName)
    if (connection) {
      connection.close()
      chatConnections.value.delete(roomName)
    }
  }

  return {
    connectToChat,
    disconnectFromChat,
    sendMessage,
    chatConnections,
  }
}
