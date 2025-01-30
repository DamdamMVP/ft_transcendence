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
import CatchView from '../views/CatchView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import { useAuthStore } from '../stores/authStore'

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
      meta: { requiresAuth: true },
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
      meta: { requiresAuth: true },
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
    {
      path: '/Catch',
      name: 'Catch',
      component: CatchView,
      meta: { requiresAuth: true },
    },
    {
      path: '/auth-callback',
      name: 'AuthCallback',
      component: () => import('../views/AuthCallback.vue')
    },
    {
      path: '/404',
      name: 'not-found',
      component: NotFoundView
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ],
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  // Rediriger vers /pong si l'utilisateur est connecté et va sur la page d'accueil
  if (to.path === '/' && isAuthenticated) {
    next('/pong')
    return
  }

  // Si la route nécessite une authentification et que l'utilisateur n'est pas connecté
  if (requiresAuth && !isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
