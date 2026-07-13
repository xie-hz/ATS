<script setup>
import { ref } from "vue"
import GuestLogin from "./views/GuestLogin.vue"
import Meeting from "./views/Meeting.vue"

// 访客会话：guestJoin 成功后填充，Meeting 退出后清空回到登录页。
const session = ref(null)

function onJoined(s) {
  session.value = s
}
function onLeave() {
  session.value = null
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
