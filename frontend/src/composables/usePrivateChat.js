import { ref } from 'vue'

export function usePrivateChat() {
  const chatConnections = ref(new Map())
  const reconnectAttempts = ref(new Map())
  const MAX_RECONNECT_ATTEMPTS = 5
  const RECONNECT_DELAY = 3000 // 3 secondes

  const getChatRoomName = (user1, user2) => {
    const sortedUsers = [user1, user2].sort()
    return `private_${sortedUsers[0]}_${sortedUsers[1]}`
  }

  const handleReconnect = async (roomName, currentUser, otherUser) => {
    const attempts = reconnectAttempts.value.get(roomName) || 0
    
    if (attempts < MAX_RECONNECT_ATTEMPTS) {
      console.log(`Tentative de reconnexion ${attempts + 1}/${MAX_RECONNECT_ATTEMPTS} pour ${roomName}`)
      reconnectAttempts.value.set(roomName, attempts + 1)
      
      await new Promise(resolve => setTimeout(resolve, RECONNECT_DELAY))
      return connectToChat(currentUser, otherUser)
    } else {
      console.error(`Échec de reconnexion après ${MAX_RECONNECT_ATTEMPTS} tentatives pour ${roomName}`)
      reconnectAttempts.value.delete(roomName)
      return null
    }
  }

  const connectToChat = (currentUser, otherUser) => {
    const isGeneral = currentUser === 'general' && otherUser === 'general'
    const roomName = isGeneral ? 'general' : getChatRoomName(currentUser, otherUser)
    
    // Vérifier si une connexion existe et est active
    const existingConnection = chatConnections.value.get(roomName)
    if (existingConnection?.readyState === WebSocket.OPEN) {
      return existingConnection
    }

    // Fermer toute connexion existante qui ne serait pas en état OPEN
    if (existingConnection) {
      existingConnection.close()
      chatConnections.value.delete(roomName)
    }

    // Créer nouvelle connexion
    const wsUrl = isGeneral ? 'ws/chat/general/' : `/ws/chat/${roomName}/`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log(`Connecté à ${roomName}`)
      reconnectAttempts.value.delete(roomName) // Réinitialiser les tentatives après succès
    }

    ws.onclose = async (event) => {
      console.log(`Déconnecté de ${roomName}`, event.code, event.reason)
      chatConnections.value.delete(roomName)
      
      // Tenter une reconnexion automatique si la fermeture n'était pas volontaire
      if (event.code !== 1000) {
        await handleReconnect(roomName, currentUser, otherUser)
      }
    }

    ws.onerror = (error) => {
      console.error(`Erreur WebSocket pour ${roomName}:`, error)
    }

    chatConnections.value.set(roomName, ws)
    return ws
  }

  const sendMessage = (currentUser, otherUser, message) => {
    const isGeneral = currentUser === 'general' && otherUser === 'general'
    const roomName = isGeneral ? 'general' : getChatRoomName(currentUser, otherUser)
    const connection = chatConnections.value.get(roomName)

    if (!connection) {
      console.error(`Pas de connexion trouvée pour ${roomName}`)
      return false
    }

    if (connection.readyState !== WebSocket.OPEN) {
      console.error(`Connexion non ouverte pour ${roomName}. État: ${connection.readyState}`)
      // Tenter de se reconnecter
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
      console.error(`Erreur lors de l'envoi du message:`, error)
      return false
    }
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

//   const sendMessage = (currentUser, otherUser, message) => {
//     // Si c'est le canal général
//     if (currentUser === 'general' && otherUser === 'general') {
//       const connection = chatConnections.value.get('general')
//       if (connection && connection.readyState === WebSocket.OPEN) {
//         connection.send(
//           JSON.stringify({
//             message: message,
//             timestamp: new Date().toISOString(),
//           })
//         )
//         return true
//       }
//       return false
//     }

//     // Pour les chats privés
//     const roomName = getChatRoomName(currentUser, otherUser)
//     const connection = chatConnections.value.get(roomName)

//     if (connection && connection.readyState === WebSocket.OPEN) {
//       connection.send(
//         JSON.stringify({
//           message: message,
//           timestamp: new Date().toISOString(),
//         })
//       )
//       return true
//     }
//     return false
//   }

  return {
    connectToChat,
    disconnectFromChat,
    sendMessage,
    chatConnections,
  }
}

