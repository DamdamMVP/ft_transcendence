import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  console.log('Environment variables:', env)
  
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
      port: 5173,
      strictPort: true,
      cors: true,
      allowedHosts: [env.VITE_HOSTNAME || 'localhost']
    },
    define: {
      'process.env.HOSTNAME': JSON.stringify(env.VITE_HOSTNAME)
    }
  }
})