<script setup>
import { ref, onMounted } from "vue"
import GuestLogin from "./views/GuestLogin.vue"
import Meeting from "./views/Meeting.vue"
import { setToken } from "./api"

// 访客会话：guestJoin 成功后填充，Meeting 退出后清空回到登录页。
const session = ref(null)

// 刷新恢复：从 sessionStorage 读取上次会话，跳过登录直接进会议
onMounted(() => {
  const saved = sessionStorage.getItem("em_session")
  if (saved) {
    try {
      const s = JSON.parse(saved)
      setToken(s.token)
      session.value = s
    } catch {
      sessionStorage.removeItem("em_session")
      sessionStorage.removeItem("em_token")
    }
  }
})

function onJoined(s) {
  session.value = s
  // 持久化到 sessionStorage，刷新页面可恢复
  sessionStorage.setItem("em_session", JSON.stringify(s))
}
function onLeave() {
  session.value = null
  sessionStorage.removeItem("em_session")
  sessionStorage.removeItem("em_token")
}
</script>

<template>
  <GuestLogin v-if="!session" @joined="onJoined" />
  <Meeting v-else :session="session" @leave="onLeave" />
</template>

<style>
html,
body,
#app {
  height: 100%;
  margin: 0;
}
body {
  font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: #1f2329;
  color: #e5eaf0;
}
</style>
