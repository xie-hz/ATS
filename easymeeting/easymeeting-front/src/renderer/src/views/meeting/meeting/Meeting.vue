<template>
  <div>
    <Header>
      <Titlebar
        :showMax="true"
        :closeType="0"
        :styleTop="6"
        :styleRight="10"
        :borderRadius="5"
        ref="titlbarRef"
        :forceClose="false"
      >
      </Titlebar>
    </Header>
    <template v-if="inited">
      <div class="meeting-panel">
        <div :class="['layout', LAYOUT_CLASS[layoutType]]">
          <MemberList
            :layoutType="layoutType"
            @exitMeeting="forceExit"
            @selectMember="selectMemberHandler"
            :deviceInfo="deviceInfo"
          ></MemberList>
          <div
            :class="['show-panel', transformShowPanelVideo && !screenId ? 'transform-video' : '']"
            v-show="layoutType != 0"
            :style="{ height: `calc(100vh - ${(layoutType == 1 ? 123 : 0) + 90}px)` }"
          >
            <video muted autoplay ref="centerScreenRef" playsinline v-show="openVideoRef"></video>
            <div v-show="!openVideoRef" class="user-info">
              <Avatar :avatar="selectUserInfo.userId"> </Avatar>
              <div :class="['user-name', 'iconfont', proxy.Utils.getSexIcon(selectUserInfo.sex)]">
                {{ selectUserInfo.nickName }}
              </div>
            </div>
          </div>
        </div>
        <SplitLine
          v-show="chatOpened || memberOpened"
          :initWidth="initRightWidth"
          @widthChange="widthChange"
        >
        </SplitLine>
        <div v-show="chatOpened || memberOpened" :style="{ width: rightWidth + 'px' }">
          <ChatPanel v-show="chatOpened" ref="chatPanelRef"></ChatPanel>
          <MemberPanel v-show="memberOpened" ref="memberPanelRef"></MemberPanel>
        </div>
      </div>
      <Footer
        :deviceInfo="deviceInfo"
        @openChat="openChatHandler"
        @openMember="openMemberHandler"
      ></Footer>
    </template>
    <template v-else>
      <div class="check-env">正在检查系统环境....</div>
    </template>
  </div>
</template>

<script setup>
import SplitLine from './SplitLine.vue'
import MemberPanel from '../member/MemberPanel.vue'
import ChatPanel from '../chat/ChatPanel.vue'
import MemberList from './MemberList.vue'
import Footer from './Footer.vue'
import Header from './Header.vue'
import { ref, reactive, getCurrentInstance, nextTick, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
import { mitter } from '@/eventbus/eventBus.js'
import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

import { useMeetingStore } from '@/stores/MeetingStore'
const meetingStore = useMeetingStore()

//初始化环境
const inited = ref(false)
const deviceInfo = ref({})
const initEnv = async () => {
  //检查麦克风
  const devices = await navigator.mediaDevices.enumerateDevices()
  const defaultMic = devices.find((device) => device.kind === 'audioinput')
  //获取系统设置
  const sysSetting = await window.electron.ipcRenderer.invoke('getSysSetting')
  //检测摄像头是否可用,摄像头只能同时一个应用使用，不能通过设备来检测
  const stream = await navigator.mediaDevices
    .getUserMedia({
      video: true,
      audio: false
    })
    .catch((error) => {
      console.error('摄像头失败', error)
    })
  deviceInfo.value = {
    micEnable: defaultMic != null,
    cameraEnable: stream != null,
    micOpen: sysSetting.openMic,
    cameraOpen: sysSetting.openCamera
  }
  inited.value = true
}
initEnv()

const LAYOUT_CLASS = {
  0: 'layout-grid',
  1: 'layout-top',
  2: 'layout-right'
}
const layoutType = ref(0)
const layoutChangeHandler = (type) => {
  layoutType.value = type
}

const titlbarRef = ref()
const closeMeeting = () => {
  proxy.Confirm({
    message: '确认要退出会议吗?',
    okfun: async () => {
      titlbarRef.value.custClose()
    }
  })
  return false
}

const forceExit = () => {
  titlbarRef.value.custClose()
}

const screenId = ref()
const shareScreenHandler = (_screenId) => {
  screenId.value = _screenId
}
const centerScreenRef = ref()
//选择用户，中间就展示那个用户
//是否旋转video，如果选中的是自己,并且不是共享屏幕
const transformShowPanelVideo = ref(false)
const openVideoRef = ref(true)
const selectUserInfo = ref({})
const selectMemberHandler = async ({ srcObject, userId, sex, nickName, openVideo }) => {
  console.log('selectmember', srcObject, userId, nickName, openVideo)
  if (layoutType.value === 0) {
    return
  }
  selectUserInfo.value = {
    userId,
    nickName,
    sex
  }
  openVideoRef.value = openVideo
  await nextTick()
  centerScreenRef.value.srcObject = srcObject
  if (userId === userInfoStore.userInfo.userId) {
    //是自己，需要旋转video
    transformShowPanelVideo.value = true
  } else {
    transformShowPanelVideo.value = false
  }
}

//左边容器
const initRightWidth = 400
const rightWidth = ref(initRightWidth)
const widthChange = (width) => {
  rightWidth.value = width
}

//开启聊天
const chatPanelRef = ref()
const chatOpened = ref(false)
const openChatHandler = async () => {
  memberOpened.value = false
  chatOpened.value = !chatOpened.value
  //更新store开启关闭状态
  meetingStore.updateChatOpen(chatOpened.value)
  if (chatOpened.value) {
    chatPanelRef.value.showChatPanel()
  }
}

//查看成员
const memberPanelRef = ref()
const memberOpened = ref(false)
const openMemberHandler = () => {
  chatOpened.value = false
  memberOpened.value = !memberOpened.value
}
onMounted(() => {
  mitter.on('layoutChange', layoutChangeHandler)
  mitter.on('shareScreen', shareScreenHandler)

  window.electron.ipcRenderer.on('preCloseWindow', (e) => {
    closeMeeting()
  })
})
onUnmounted(async () => {
  mitter.off('layoutChange', layoutChangeHandler)
  mitter.off('shareScreen', shareScreenHandler)

  window.electron.ipcRenderer.removeAllListeners('preCloseWindow')
})
</script>

<style lang="scss" scoped>
.meeting-panel {
  display: flex;
  .layout {
    flex: 1;
    height: calc(100vh - 92px);
    .show-panel {
      display: flex;
      align-items: center;
      justify-content: center;
      video {
        height: 100%;
        width: 100%;
        object-fit: contain;
      }
      .user-info {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        .user-name {
          margin-top: 5px;
          font-size: 13px;
          color: #575757;
          display: flex;
          align-items: center;
          &::before {
            color: var(--blue);
            margin-right: 1px;
            font-size: 16px;
          }
        }
        .icon-woman {
          &::before {
            color: #fb7373;
          }
        }
      }
    }
    .transform-video {
      video {
        transform: scaleX(-1);
      }
    }
  }

  .layout-top {
    margin: 0px auto;
    text-align: center;
    .show-panel {
      border-top: 1px solid #ddd;
    }
  }
  .layout-right {
    display: flex;
    flex-direction: row-reverse;
    .show-panel {
      border-right: 1px solid #ddd;
      flex: 1;
    }
  }
}

.check-env {
  height: calc(100vh - 42px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #797979;
}
</style>
