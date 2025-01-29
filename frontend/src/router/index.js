import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ProfilView from '../views/ProfilView.vue'
import History from '../components/profil/History.vue'
import SettingsView from '../views/SettingsView.vue'
import PongView from '../views/PongView.vue'
import HomePong from '../components/pong/HomePong.vue'
import PongLocal from '../components/pong/modes/PongLocal.vue'
import PongVsAI from '../components/pong/modes/PongVsAI.vue'
import PongTournament from '../components/pong/modes/PongTournament.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/profil',
      component: ProfilView,
      children: [
        {
          path: ':game',
          name: 'game',
          component: History,
        },
      ],
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView,
    },
    {
      path: '/pong',
      component: PongView,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'pong-home',
          component: HomePong
        },
        {
          path: 'local',
          name: 'pong-local',
          component: PongLocal
        },
        {
          path: 'ai',
          name: 'pong-ai',
          component: PongVsAI
        },
        {
          path: 'tournament',
          name: 'pong-tournament',
          component: PongTournament
        }
      ]
    },
  ],
})

export default router
