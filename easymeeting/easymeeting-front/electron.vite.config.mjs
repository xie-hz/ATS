import { resolve } from 'path'
import { defineConfig, externalizeDepsPlugin } from 'electron-vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  main: {
    plugins: [externalizeDepsPlugin()]
  },
  preload: {
    plugins: [externalizeDepsPlugin()]
  },
  renderer: {
    resolve: {
      alias: {
        '@': resolve('src/renderer/src')
      }
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler'
        }
      },
    },
    plugins: [vue()],
    server: {
      historyApiFallback: true, // 确保所有路由回退到 index.html
      hmr: true,
      port: 6001,
      proxy: {
        "/api": {
          target: "http://localhost:6060",
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api'),
        }
      }
    }
  },
  build: {
    assetsDir: '.', // 确保资源在根目录
    rollupOptions: {
      output: {
        assetFileNames: '[name].[ext]' // 保持原始文件名
      }
    }
  }
})
