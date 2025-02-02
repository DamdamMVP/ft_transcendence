import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Charger les variables d'environnement avec un préfixe vide pour tout charger
  const env = loadEnv(mode, process.cwd(), '')
  
  console.log('Environment variables:', env) // Pour le débogage
  
  return {
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      host: true,
      port: 80,
      strictPort: true,
      cors: true,
      allowedHosts: [env.VITE_HOSTNAME || 'localhost'] // Utilisez VITE_ comme préfixe
    },
    // Exposer les variables d'environnement au client
    define: {
      'process.env.HOSTNAME': JSON.stringify(env.VITE_HOSTNAME),
	  'import.meta.env.VITE_BASE_URL': JSON.stringify(env.VITE_BASE_URL)
    }
  }
})