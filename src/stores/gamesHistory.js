import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGamesHistoryStore = defineStore('gamesHistory', () => {
  const matches = ref([
    {
      id: 1,
      win: false,
      score: '3-2',
      opponent: 'Roger',
      date: '2024-10-20',
    },
  ])

  const addMatch = (match) => {
    matches.value.push(match)
  }

  return { matches, addMatch }
})
