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
      date: 1737766730,
    },
    {
      id: 2,
      game: 'Tic-Tac-Toe',
      win: false,
      score: '3-1',
      opponent: 'Albert',
      date: 1737766731,
    },
    {
      id: 3,
      game: 'Pong',
      win: false,
      score: '3-2',
      opponent: 'Roger',
      date: 1737766732,
    },
  ])

  const addMatch = (match) => {
    matches.value.push(match)
  }

  return { matches, addMatch }
})
