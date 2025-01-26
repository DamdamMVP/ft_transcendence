import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useProfilDatasStore = defineStore('profilDatas', () => {
  const matches = ref([
    {
      id: 1,
      name: 'Zilean',
      wins: 45,
      losses: 35,
      profilePicture:
        'https://static.wikia.nocookie.net/lolesports_gamepedia_en/images/a/ac/ZileanSquare.png/revision/latest?cb=20170802185212',
    },
  ])

  const addMatch = (match) => {
    matches.value.push(match)
  }

  return { matches, addMatch }
})
