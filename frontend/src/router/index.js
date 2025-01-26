import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ProfilView from '../views/ProfilView.vue'
import History from '../components/History.vue'
import SettingsView from '../views/SettingsView.vue'
import PongView from '../views/PongView.vue'

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
      name: 'pong',
      component: PongView,
      meta: { requiresAuth: true }
    }
  ],
})

export default router
