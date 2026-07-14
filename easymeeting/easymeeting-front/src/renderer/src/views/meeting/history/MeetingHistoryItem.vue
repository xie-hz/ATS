<template>
  <div class="history-item">
    <div class="date-week">{{ proxy.Utils.getWeekAndDate(data.startTime) }}</div>
    <div class="meeting-panel">
      <div class="time-panel">
        <div>{{ proxy.Utils.formatDate(data.startTime) }}</div>
        <div>参会</div>
      </div>
      <div class="content-panel">
        <div class="meeting-name-panel">
          <div class="meeting-name">{{ data.meetingName }}</div>
          <div class="rejoin-btn" v-if="data.status === 0" @click="reJoinMeeting">进入会议</div>
          <div class="meeting-op">
            <div class="iconfont icon-close" @click="delMeetingRecord"></div>
            <div class="iconfont icon-chat" @click="showMeetingMessage"></div>
          </div>
        </div>
        <div class="meeting-info">发起人 {{ data.createUserName }} · {{ data.meetingNo }}</div>
        <div class="meeting-info">
          已参会
          <span class="join-member" @click="showMeetingMember">共{{data.memberCount}}人<span
              class="iconfont icon-narrow-right"></span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

const props = defineProps({
  data: {
    type: Object,
    default: {}
  }
})

const showMeetingMessage = () => {
  window.electron.ipcRenderer.send('openWindow', {
    title: '会议聊天记录',
    windowId: 'meetingMessage',
    path: '/meetingMessage',
    width: 600,
    height: 800,
    maximizable: false,
    data: {
      meetingId: props.data.meetingId,
      meetName: props.data.meetingName
    }
  })
}

const showMeetingMember = () => {
  window.electron.ipcRenderer.send('openWindow', {
    title: '会议成员',
    windowId: 'meetingMember',
    path: '/meetingMember',
    width: 500,
    height: 600,
    maximizable: false,
    data: {
      meetingId: props.data.meetingId,
      meetName: props.data.meetingName
    }
  })
}

const emit = defineEmits(['delRecrod'])
const delMeetingRecord = () => {
  proxy.Confirm({
    message: '确定要删除记录吗？',
    okfun: async () => {
      let result = await proxy.Request({
        url: proxy.Api.delMeetingRecord,
        params: {
          meetingId: props.data.meetingId
        }
      })
      if (!result) {
        return
      }
      emit('delRecrod', props.data.meetingId)
    }
  })
}

// 重新进入未结束的会议
const reJoinMeeting = async () => {
  let result = await proxy.Request({
    url: proxy.Api.preJoinMeeting,
    params: {
      meetingNo: props.data.meetingNo,
      nickName: userInfoStore.userInfo.nickName
    }
  })
  if (!result) {
    return
  }
  // 打开会议窗口
  window.electron.ipcRenderer.send('openWindow', {
    title: '会议详情',
    windowId: 'meeting',
    path: '/meeting',
    width: 1310,
    height: 800,
    maximizable: true
  })
}
</script>

<style lang="scss" scoped>
.history-item {
  margin: 10px 20px;
  background: #fff;
  border-radius: 5px;
  padding: 20px;
  &:hover {
    .meeting-panel {
      .content-panel {
        .meeting-name-panel {
          .meeting-op {
            display: flex;
          }
        }
      }
    }
  }
  .date-week {
    text-align: left;
    font-size: 13px;
    color: #9e9e9e;
  }
  .meeting-panel {
    margin-top: 10px;
    display: flex;
    .time-panel {
      font-size: 13px;
      color: #525252;
      padding-top: 2px;
    }
    .content-panel {
      margin-left: 10px;
      flex: 1;
      text-align: left;
      .meeting-name-panel {
        font-size: 16px;
        display: flex;
        .meeting-name {
          height: 28px;
          width: 0;
          flex: 1;
        }
        .rejoin-btn {
          background: var(--blue);
          color: #fff;
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 13px;
          margin-right: 10px;
          cursor: pointer;
          align-self: center;
          &:hover {
            opacity: 0.9;
          }
        }
        .meeting-op {
          display: none;
          align-items: center;
          .iconfont {
            background: #efefef;
            padding: 5px;
            border-radius: 5px;
            color: #656565;
            cursor: pointer;
          }
          .icon-close {
            margin-right: 10px;
            font-weight: bold;
          }
        }
      }
      .meeting-info {
        font-size: 13px;
        color: #525252;
        margin-top: 5px;
      }
      .join-member {
        margin-left: 5px;
        cursor: pointer;
        border-radius: 3px;
        padding: 2px;
        &:hover {
          background: #ddd;
        }
        .icon-narrow-right {
          font-size: 12px;
        }
      }
    }
  }
}
</style>
