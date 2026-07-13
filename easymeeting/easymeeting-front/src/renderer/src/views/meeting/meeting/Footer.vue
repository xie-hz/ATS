<template>
  <div class="footer">
    <div class="btn-list">
      <!--音频-->
      <div class="btn-item" @click="micClickHandler">
        <MicIcon :defaultOpen="deviceInfo.micEnable && deviceInfo.micOpen" :size="20" :showLabel="false"
          v-model="micInfo" ref="micInfoRef">
        </MicIcon>
        <div class="name">
          {{ deviceInfo.micEnable && deviceInfo.micOpen ? '静音' : '取消静音' }}
        </div>
      </div>
      <!--视频-->
      <div class="btn-item" @click="cameraClickHandler">
        <div :class="[
            'iconfont',
            deviceInfo.cameraEnable && deviceInfo.cameraOpen ? 'icon-video2' : 'icon-video2-close'
          ]"></div>
        <div class="name">
          {{ deviceInfo.cameraEnable && deviceInfo.cameraOpen ? '关闭视频' : '开启视频' }}
        </div>
      </div>
      <!--共享屏幕-->
      <div class="btn-item" @click="shareScreenClickHandler">
        <div :class="['iconfont', shareScreen ? 'icon-share-screen2-close' : 'icon-share-screen2']"></div>
        <div class="name">{{ shareScreen ? '取消共享' : '共享屏幕' }}</div>
      </div>
      <div :class="['btn-item', item.active ? 'active' : '']" v-for="item in buttons" @click="clickHandler(item)">
        <el-badge :value="meetingStore.noReadChatCount" :max="99" :hidden="meetingStore.noReadChatCount==0"
          :offset="[0, 3]" v-if="item.btnType === 'chat'">
          <div :class="['iconfont', 'icon-' + item.icon]"></div>
          <div class="name">
            <span> {{ item.name }}</span>
            <span v-if="item.btnType == 'members'">({{ meetingStore.allMemberList.length }})</span>
          </div>
        </el-badge>
        <template v-else>
          <div :class="['iconfont', 'icon-' + item.icon]"></div>
          <div class="name">
            <span> {{ item.name }}</span>
            <span v-if="item.btnType == 'members'">({{ meetingStore.allMemberList.length }})</span>
          </div>
        </template>
      </div>
    </div>
  </div>
  <SelectScreen ref="selectScreenRef"></SelectScreen>
  <InviteMember ref="inviteMemberRef"></InviteMember>
</template>

<script setup>
import InviteMember from '../invite/InviteMember.vue'
import MicIcon from '@/components/MicIcon.vue'
import SelectScreen from './SelectScreen.vue'
import { ref, reactive, getCurrentInstance, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
import { useMeetingStore } from '@/stores/MeetingStore'
const meetingStore = useMeetingStore()

import { mitter } from '@/eventbus/eventBus.js'

const props = defineProps({
  deviceInfo: {
    type: Object,
    default: {}
  }
})

const shareScreen = ref(route.query.addType == 1)
//麦克风
const micInfoRef = ref()
const micInfo = ref({})
const micClickHandler = () => {
  if (!props.deviceInfo.micEnable) {
    return
  }
  micInfoRef.value.toggleMic()
  props.deviceInfo.micOpen = !props.deviceInfo.micOpen
  mitter.emit('micSwitch', props.deviceInfo.micOpen)
}
//开启关闭摄像头
const cameraClickHandler = () => {
  if (!props.deviceInfo.cameraEnable) {
    return
  }
  props.deviceInfo.cameraOpen = !props.deviceInfo.cameraOpen
  mitter.emit('cameraSwitch', props.deviceInfo.cameraOpen)
}
//共享取消共享
const selectScreenRef = ref()
const shareScreenClickHandler = () => {
  if (shareScreen.value) {
    mitter.emit('shareScreen', '')
    shareScreen.value = false
    return
  }
  selectScreenRef.value.show()
}

const shareScreenHandler = () => {
  shareScreen.value = true
}

const buttons = ref([
  {
    btnType: 'invite',
    name: '邀请',
    icon: 'invite'
  },
  {
    btnType: 'members',
    name: '成员',
    icon: 'members',
    showActive: true,
    active: false
  },
  {
    btnType: 'chat',
    name: '聊天',
    icon: 'chat',
    showActive: true,
    active: false
  }
])
const emit = defineEmits(['openChat', 'openMember'])
const inviteMemberRef = ref()
const clickHandler = (item) => {
  if (item.showActive) {
    buttons.value.forEach((element) => {
      if (element.btnType == item.btnType && !item.active) {
        element.active = true
      } else {
        element.active = false
      }
    })
  }
  switch (item.btnType) {
    case 'invite':
      inviteMemberRef.value.show()
      break
    case 'members':
      emit('openMember')
      break
    case 'chat':
      emit('openChat')
      break
  }
}

onMounted(() => {
  mitter.on('shareScreen', shareScreenHandler)
})
onUnmounted(async () => {
  mitter.off('shareScreen', shareScreenHandler)
})
</script>

<style lang="scss" scoped>
.footer {
  -webkit-app-region: drag;
  border-top: 1px solid #ddd;
  height: 50px;
  display: flex;
  justify-content: center;
  .btn-list {
    display: flex;
    align-items: center;
    .btn-item {
      -webkit-app-region: no-drag;
      margin: 0px 5px;
      padding: 5px 0px;
      width: 70px;
      border-radius: 3px;
      cursor: pointer;
      color: var(--text);
      display: flex;
      flex-direction: column;
      align-items: center;
      &:hover {
        background: #efefef;
      }
      .iconfont {
        font-size: 20px;
      }
      .name {
        font-size: 12px;
      }
    }
    .close-screen-share {
      &:hover {
        background: #fff;
      }
    }
    .active {
      background: #efefef;
    }
  }
}
</style>
