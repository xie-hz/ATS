<template>
  <div class="chat-panel">
    <div class="chat-panel-title">
      <div class="iconfont icon-chat">聊天</div>
    </div>
    <div class="chat-list" id="chat-list" ref="chatListRef">
      <DataLoadMoreList
        ref="dataLoadingMoreRef"
        :loadMoreType="1"
        :dataSource="dataSource"
        :loading="loading"
        @loadData="loadMessage"
      >
        <template #default="{ data, index }">
          <MessageItem :data="data"></MessageItem>
        </template>
      </DataLoadMoreList>
    </div>
    <ChatSend :sysSetting="sysSetting"></ChatSend>
  </div>
</template>

<script setup>
import MessageItem from './MessageItem.vue'
import ChatSend from './ChatSend.vue'
import { ref, reactive, getCurrentInstance, nextTick, onUnmounted, onMounted, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

import { useMeetingStore } from '@/stores/MeetingStore'
const meetingStore = useMeetingStore()

const loading = ref(false)
const dataSource = ref({})
const dataLoadingMoreRef = ref()
const loadMessage = async () => {
  if (
    Object.keys(dataSource.value).length > 0 &&
    dataSource.value.pageNo == dataSource.value.pageTotal
  ) {
    return
  }
  loading.value = true
  let pageNo = dataSource.value.pageNo || 0
  pageNo++
  let result = await proxy.Request({
    url: proxy.Api.loadMessage,
    showLoading: false,
    params: {
      pageNo,
      maxMessageId: pageNo > 1 ? dataSource.value.list[0].messageId : null
    }
  })
  if (!result) {
    return
  }
  loading.value = false
  const queryMessageList = result.data.list.map((item) => {
    item.isMe = userInfoStore.userInfo.userId == item.sendUserId
    return item
  })
  let list = dataSource.value.list || []
  list.unshift(...queryMessageList)
  result.data.list = list
  dataSource.value = result.data
  sortMessage()
  if (dataSource.value.pageNo > 1) {
    await nextTick()
    dataLoadingMoreRef.value.gotoTop()
  }
}

const sortMessage = () => {
  dataSource.value.list.sort((a, b) => {
    const bigA = BigInt(a.messageId)
    const bigB = BigInt(b.messageId)
    if (bigA < bigB) {
      return -1
    }
    if (bigA > bigB) {
      return 1
    }
    return 0
  })
}

const listenMessage = () => {
  window.electron.ipcRenderer.on('chatMessage', async (e, messageObj) => {
    console.log('收到消息', messageObj)
    switch (messageObj.messageType) {
      case 5: //文本消息
      case 6: //媒体消息
        meetingStore.addNoReadChatCount()

        messageObj.isMe = userInfoStore.userInfo.userId == messageObj.sendUserId
        dataSource.value.list.push(messageObj)
        sortMessage()
        //收到消息滚动到底部
        await nextTick()
        dataLoadingMoreRef.value.gotoBottom(false)
        break
      case 7: //媒体消息更新
        const messageItem = dataSource.value.list.find((item) => {
          return item.messageId == messageObj.messageId
        })
        if (!messageItem) {
          return
        }
        messageItem.status = 1
        messageItem.messageContent = messageObj.messageContent
    }
  })
}

const listenDownloadProgress = () => {
  window.electron.ipcRenderer.on('downloadProgress', (e, { messageId, percent, localFilePath }) => {
    const message = dataSource.value.list.find((item) => {
      return item.messageId == messageId
    })
    if (!message) {
      return
    }
    console.log(percent)
    message.downloadProgress = percent
    message.localFilePath = localFilePath
  })
}

const listenUploadProgress = () => {
  window.electron.ipcRenderer.on('uploadProgress', (e, { messageId, percent }) => {
    const message = dataSource.value.list.find((item) => {
      return item.messageId == messageId
    })
    if (!message) {
      return
    }
    message.uploadProgress = percent
  })
}

onMounted(() => {
  listenMessage()
  listenDownloadProgress()
  listenUploadProgress()
})

onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('chatMessage')
  window.electron.ipcRenderer.removeAllListeners('downloadProgress')
  window.electron.ipcRenderer.removeAllListeners('uploadProgress')
})

const showChatPanel = async () => {
  await nextTick()
  dataLoadingMoreRef.value.gotoBottom(true)
}
defineExpose({
  showChatPanel
})

provide('showMedia', (messageId) => {
  let mediaList = dataSource.value.list
    .filter((item) => {
      return item.status == 1 && (item.fileType == 0 || item.fileType == 1)
    })
    .map((item) => {
      return {
        messageId: item.messageId + '',
        fileType: item.fileType,
        sendTime: item.sendTime,
        fileName: item.fileName
      }
    })
  window.electron.ipcRenderer.send('openWindow', {
    title: '媒体详情',
    windowId: 'media',
    path: '/showMedia',
    width: 960,
    height: 720,
    data: {
      currentMessageId: messageId,
      mediaList: JSON.stringify(mediaList)
    }
  })
})

const sysSetting = ref({})
const loadSysSetting = async () => {
  let result = await proxy.Request({
    url: proxy.Api.getSysSetting,
    showLoading: false
  })
  if (!result) {
    return
  }
  sysSetting.value = result.data
}
loadSysSetting()
</script>

<style lang="scss" scoped>
.chat-panel {
  height: calc(100vh - 300px);
  background: #fff;
  .chat-panel-title {
    border-bottom: 1px solid #ddd;
    padding: 10px;
    color: #4e5461;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    .icon-chat {
      display: flex;
      align-items: center;
      font-size: 14px;
      &::before {
        margin-right: 3px;
        font-size: 20px;
      }
    }
    .icon-transfer {
      cursor: pointer;
    }
  }
  .chat-list {
    overflow: auto;
    height: calc(100vh - 345px);
    border-bottom: 1px solid #ddd;
    padding-bottom: 10px;
  }
}
</style>
