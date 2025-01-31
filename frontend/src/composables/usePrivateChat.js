import { ref } from 'vue'

export function usePrivateChat() {
  const chatConnections = ref(new Map()) // Stocke les connexions WebSocket actives

  const getChatRoomName = (user1, user2) => {
    // Trie les noms d'utilisateurs pour assurer la cohérence
    const sortedUsers = [user1, user2].sort()
    return `private_${sortedUsers[0]}_${sortedUsers[1]}`
  }

  const connectToChat = (currentUser, otherUser) => {
    // Si c'est le canal général
    if (currentUser === 'general' && otherUser === 'general') {
      // Vérifie si une connexion existe déjà
      if (chatConnections.value.has('general')) {
        return chatConnections.value.get('general')
      }

      // Crée une nouvelle connexion WebSocket pour le canal général
      const ws = new WebSocket('ws/chat/general/')

      ws.onopen = () => {
        console.log('Connected to general channel')
      }

      ws.onclose = () => {
        console.log('Disconnected from general channel')
        chatConnections.value.delete('general')
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      // Stocke la connexion
      chatConnections.value.set('general', ws)
      return ws
    }

    // Pour les chats privés
    const roomName = getChatRoomName(currentUser, otherUser)

    // Vérifie si une connexion existe déjà
    if (chatConnections.value.has(roomName)) {
      return chatConnections.value.get(roomName)
    }

    // Crée une nouvelle connexion WebSocket
    const ws = new WebSocket(`/ws/chat/${roomName}/`)

    ws.onopen = () => {
      console.log(`Connected to chat room: ${roomName}`)
    }

    ws.onclose = () => {
      console.log(`Disconnected from chat room: ${roomName}`)
      chatConnections.value.delete(roomName)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    // Stocke la connexion
    chatConnections.value.set(roomName, ws)
    return ws
  }

  const disconnectFromChat = (currentUser, otherUser) => {
    // Si c'est le canal général
    if (currentUser === 'general' && otherUser === 'general') {
      const connection = chatConnections.value.get('general')
      if (connection) {
        connection.close()
        chatConnections.value.delete('general')
      }
      return
    }

    // Pour les chats privés
    const roomName = getChatRoomName(currentUser, otherUser)
    const connection = chatConnections.value.get(roomName)
    if (connection) {
      connection.close()
      chatConnections.value.delete(roomName)
    }
  }

  const sendMessage = (currentUser, otherUser, message) => {
    // Si c'est le canal général
    if (currentUser === 'general' && otherUser === 'general') {
      const connection = chatConnections.value.get('general')
      if (connection && connection.readyState === WebSocket.OPEN) {
        connection.send(
          JSON.stringify({
            message: message,
            timestamp: new Date().toISOString(),
          })
        )
        return true
      }
      return false
    }

    // Pour les chats privés
    const roomName = getChatRoomName(currentUser, otherUser)
    const connection = chatConnections.value.get(roomName)

    if (connection && connection.readyState === WebSocket.OPEN) {
      connection.send(
        JSON.stringify({
          message: message,
          timestamp: new Date().toISOString(),
        })
      )
      return true
    }
    return false
  }

  return {
    connectToChat,
    disconnectFromChat,
    sendMessage,
    chatConnections,
  }
}
