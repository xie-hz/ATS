<template>
  <el-config-provider :locale="zhCn" :message="config">
    <div class="app-root">
      <router-view></router-view>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const config = ref({
  max: 1
})
import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

//监听退出
const onExitMeeting = () => {
  window.electron.ipcRenderer.on('closeWindow', async (e, { windowId }) => {
    if (windowId == 'meeting') {
      await proxy.Request({
        url: proxy.Api.exitMeeting
      })
    }
  })
}

//获取信息到store
const saveUserInfo2Store = async () => {
  userInfoStore.setInfo(JSON.parse(localStorage.getItem('userInfo')) || {})
}

onMounted(() => {
  saveUserInfo2Store()
  onExitMeeting()
})
</script>

<style lang="scss" scoped>
.app-root {
  background: #fff;
  overflow: hidden;
  border: 1px solid #ddd;
  border-radius: 5px;
  overflow: hidden;
}
</style>
