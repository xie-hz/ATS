import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

// Dev: proxy /api -> EasyMeeting HTTP (6060), /ws -> EasyMeeting Netty WS (6061).
// Prod: a reverse proxy (nginx/traefik) routes the same paths.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: {
      "/api": {
        target: "http://localhost:6060",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:6061",
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
