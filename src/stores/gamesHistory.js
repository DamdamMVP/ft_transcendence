import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGamesHistoryStore = defineStore('gamesHistory', () => {
  const matches = ref([
    {
      id: 1,
      game: 'Pong',
      win: false,
      score: '3-2',
      opponent: 'Roger',
      date: '2024-10-20',
    },
    {
      id: 2,
      game: 'Tic-Tac-Toe',
      win: false,
      score: '3-1',
      opponent: 'Albert',
      date: '2024-10-20',
    },
    {
      id: 3,
      game: 'Pong',
      win: false,
      score: '3-2',
      opponent: 'Roger',
      date: '2024-10-20',
    },
  ])

  const addMatch = (match) => {
    matches.value.push(match)
    // Garder seulement les 6 derniers matchs de Pong
    const pongMatches = matches.value.filter(m => m.game === 'Pong')
    if (pongMatches.length > 6) {
      const oldestPongMatch = pongMatches[0]
      matches.value = matches.value.filter(m => m !== oldestPongMatch)
    }
  }

  return { matches, addMatch }
})
