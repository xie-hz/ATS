<template>
  <div class="layout">
    <div class="left">
      <div class="top-panel">
        <div class="avatar">
          <Avatar
            ref="avatarRef"
            :width="30"
            :avatar="userInfoStore.userInfo.userId"
            :update="true"
            @click="showUserInfo"
          >
          </Avatar>
        </div>
        <div class="top-menus">
          <div
            :class="['menu-item', item.codes.includes(route.meta.code) ? 'active' : '']"
            v-for="item in leftTopMenus"
            @click="jumpMenu(item)"
          >
            <el-badge
              :value="item.messageCount"
              :max="99"
              :hidden="item.messageCount == 0"
              :offset="[-5, 0]"
            >
              <div :class="['iconfont', 'icon-' + item.icon]"></div>
              <div class="name">{{ item.name }}</div>
            </el-badge>
          </div>
        </div>
      </div>
      <div class="bottom-menus">
        <template v-for="item in leftBottomMenus">
          <div
            :class="['menu-item', item.codes.includes(route.meta.code) ? 'active' : '']"
            v-if="!item.onlyAdmin || (item.onlyAdmin && userInfoStore.userInfo.admin)"
            @click="jumpMenu(item)"
          >
            <div :class="['iconfont', 'icon-' + item.icon]"></div>
          </div>
        </template>
      </div>
    </div>
    <div class="right">
      <router-view></router-view>
    </div>
  </div>
  <UpdateUser ref="updateUserRef" @reloadInfo="reloadInfoHandler"></UpdateUser>

  <AppUpdate></AppUpdate>
</template>

<script setup>
import AppUpdate from './AppUpdate.vue'
import UpdateUser from './UpdateUser.vue'
import { ref, reactive, getCurrentInstance, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
import { mitter } from '@/eventbus/eventBus.js'

import { ElLoading } from 'element-plus'

import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

import { useContactStore } from '@/stores/UserContactStore'
const contactStore = useContactStore()

import { useMeetingStore } from '@/stores/MeetingStore'
const meetingStore = useMeetingStore()

const leftTopMenus = ref([
  {
    name: '会议',
    icon: 'video',
    path: '/meetingMain',
    codes: ['meeting'],
    messageCount: 0
  },
  {
    name: '通讯录',
    icon: 'contact',
    path: '/contact',
    codes: ['contact'],
    messageCount: 0
  },
  {
    name: '录制',
    icon: 'record',
    path: '/screencap',
    codes: ['screencap'],
    messageCount: 0
  }
])

const leftBottomMenus = [
  {
    icon: 'settings',
    path: '/setting',
    codes: ['setting'],
    onlyAdmin: false
  },
  {
    icon: 'admin',
    codes: [],
    btnType: 'admin',
    onlyAdmin: true
  }
]
const jumpMenu = (menu) => {
  if (menu.btnType === 'admin') {
    window.electron.ipcRenderer.send('openWindow', {
      title: '管理后台',
      windowId: 'adminWindow',
      path: '/admin',
      width: 1310,
      height: 800
    })
    return
  }
  router.push(menu.path)
}
const listenMessage = () => {
  window.electron.ipcRenderer.on('mainMessage', (e, messageObj) => {
    console.log('收到消息', messageObj)
    switch (messageObj.messageType) {
      case 8: //联系人申请信息
        contactStore.updateLastUpdateTime()
        break
      case 12: //处理联系人申请
        let result = ''
        if (messageObj.messageContent == 1) {
          mitter.emit('reloadContact')
          result = '已同意你的申请'
        } else if (messageObj.messageContent == 2) {
          result = '已拒绝你的申请'
        } else if (messageObj.messageContent == 3) {
          result = '已将你拉黑'
        }
        proxy.Alert(`【${messageObj.sendUserNickName}】${result}`)
        break
      case 1: //加入会议
        const newMember = messageObj.messageContent.newMember
        if (newMember.userId === userInfoStore.userInfo.userId) {
          meetingStore.updateMeeting(true)
        }
        break
      case 3: //退出会议
        const { exitStatus, exitUserId } = JSON.parse(messageObj.messageContent)
        if ((exitStatus === 3 || exitStatus === 4) && exitUserId == userInfoStore.userInfo.userId) {
          proxy.Confirm({
            message: '你被强制退出会议',
            showCancelBtn: false
          })
        }
        //更新入会状态
        if (exitStatus === 2 || exitStatus === 3 || exitStatus === 4) {
          meetingStore.updateMeeting(false)
        }
        break
      case 4: //结束会议
        //设置入会状态为false
        meetingStore.updateMeeting(false)
        proxy.Confirm({
          message: '会议已结束，你已退出会议',
          showCancelBtn: false
        })
        break
      case 9: //邀请入会
        if (meetingStore.inMeeting) {
          return
        }
        const { meetingName, meetingId, inviteUserName } = JSON.parse(messageObj.messageContent)
        proxy.Confirm({
          message: `【${inviteUserName}】邀请你加入会议【${meetingName}】`,
          okText: '接受邀请',
          cancelText: '拒绝',
          okfun: () => {
            acceptInvite(meetingId)
          }
        })
        break
      case 10: //强制退出
        proxy.Alert('你被管理员强制退出', async () => {
          await window.electron.ipcRenderer.invoke('logout')
          router.push('/')
        })
    }
  })
}
const loadContactApplyCount = async () => {
  let result = await proxy.Request({
    url: proxy.Api.loadContactApplyDealWithCount
  })
  if (!result) {
    return
  }
  leftTopMenus.value[1].messageCount = result.data
}
const avatarRef = ref()
const reloadInfoHandler = async (data) => {
  userInfoStore.setInfo(data)
  avatarRef.value.updateAvatarUrl()
}

const updateUserRef = ref()
const showUserInfo = () => {
  updateUserRef.value.show()
}

//接受会议邀请
const acceptInvite = async (meetingId) => {
  let result = await proxy.Request({
    url: proxy.Api.acceptInvite,
    params: {
      meetingId
    }
  })
  if (!result) {
    return
  }
  window.electron.ipcRenderer.send('openWindow', {
    title: '会议详情',
    windowId: 'meeting',
    path: '/meeting',
    width: 1310,
    height: 800,
    resizable: false
  })
}

let reconnectLoading = null
const listenReconnect = () => {
  window.electron.ipcRenderer.on('reconnect', (e, connectSuccess) => {
    if (reconnectLoading == null && !connectSuccess) {
      reconnectLoading = ElLoading.service({
        lock: true,
        text: '与服务器断开连接，正在重连中.....',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      return
    }
    if (connectSuccess) {
      proxy.Message.success('重连成功')
      if (reconnectLoading != null) {
        reconnectLoading.close()
        reconnectLoading = null
      }
    }
  })
}

const listenLogout = () => {
  window.electron.ipcRenderer.on('logout', (e, messageObj) => {
    if (reconnectLoading != null) {
      reconnectLoading.close()
      reconnectLoading = null
    }
    // 登出时重置会议状态，避免下次登录按钮不可点
    meetingStore.updateMeeting(false)
    router.push('/')
  })
}

// 监听会议窗口关闭，重置入会状态
const listenCloseWindow = () => {
  window.electron.ipcRenderer.on('closeWindow', (e, { windowId }) => {
    if (windowId === 'meeting') {
      meetingStore.updateMeeting(false)
    }
  })
}

//监听联系人最后更新时间
watch(
  () => contactStore.lastUpdateTime,
  (newVal, oldVal) => {
    if (!newVal) {
      return
    }
    loadContactApplyCount()
  },
  { immediate: true, deep: true }
)

onMounted(() => {
  listenLogout()
  listenReconnect()
  listenCloseWindow()
  loadContactApplyCount()
  listenMessage()
})

onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('mainMessage')
  window.electron.ipcRenderer.removeAllListeners('logout')
  window.electron.ipcRenderer.removeAllListeners('reconnect')
  window.electron.ipcRenderer.removeAllListeners('closeWindow')
})
</script>

<style lang="scss" scoped>
.layout {
  display: flex;
  .left {
    width: 64px;
    background: #f3f3f4;
    margin: 0px auto;
    display: flex;
    align-items: center;
    flex-direction: column;
    justify-content: space-between;
    -webkit-app-region: drag;
    .top-panel {
      text-align: center;
      .avatar {
        display: flex;
        justify-content: center;
        -webkit-app-region: no-drag;
        margin: 40px 0px 20px 0px;
      }
    }
    .bottom-menus {
      margin-bottom: 30px;
    }

    .menu-item {
      text-align: center;
      -webkit-app-region: no-drag;
      cursor: pointer;
      margin-bottom: 20px;
      color: #4c5262;
      .iconfont {
        font-size: 20px;
      }
      .name {
        margin-top: 5px;
        font-size: 12px;
      }
      &:hover {
        color: #353535;
      }
      &:last-child {
        margin-bottom: 0px;
      }
    }
    .active {
      .iconfont {
        color: var(--blue);
      }
      .name {
        color: var(--blue);
      }
    }
  }
  .right {
    flex: 1;
    width: 0;
  }
}
</style>
