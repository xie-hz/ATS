<template>
  <div class="chat-send-panel">
    <div class="chat-send-bar">
      <div class="user-select">
        发送至
        <el-select v-model="receiveUserId" placeholder="所有人" class="select" filterable>
          <el-option label="所有人" value="0" />
          <el-option :label="item.nickName" :value="item.userId" v-for="item in meetingStore.memberList" />
        </el-select>
      </div>
      <el-popover :visible="showEmojiPopover" trigger="click" placement="top" :teleported="false" @show="openPopover"
        @hide="closePopover" :popper-style="{
          padding: '0px 10px 10px 10px',
          width: '490px'
        }">
        <template #default>
          <el-tabs v-model="activeEmoji" @click.stop>
            <el-tab-pane :label="emoji.name" :name="emoji.name" v-for="emoji in emojiList">
              <div class="emoji-list">
                <div class="emoji-item" v-for="item in emoji.emojiList" @click="sendEmoji(item)">
                  {{ item }}
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </template>
        <template #reference>
          <div class="iconfont icon-emoji" @click="showEmojiPopoverHandler" title="发送表情"></div>
        </template>
      </el-popover>
      <div class="iconfont icon-folder" @click="uploadFile" title="发送文件"></div>
    </div>
    <div class="input-area">
      <el-input type="textarea" clearable placeholder="请输入消息..." v-model="message" resize="none" :rows="6"
        @keydown.ctrl.enter.prevent="sendMessage"></el-input>
    </div>
    <div class="send-btn-panel">
      <div class="tips">Ctrl+Enter可以直接发送</div>
      <el-button type="primary" :disabled="!message" @click="sendMessage">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
import emojiList from '@/utils/Emoji.js'

import { useMeetingStore } from '@/stores/MeetingStore'
const meetingStore = useMeetingStore()
import { getFileType } from '@/utils/Constants.js'

const props = defineProps({
  sysSetting: {
    type: Object,
    default: {}
  }
})

//表情相关
const activeEmoji = ref('笑脸')
const sendEmoji = (emoji) => {
  message.value = message.value + emoji
  showEmojiPopover.value = false
}
const showEmojiPopover = ref(false)
const showEmojiPopoverHandler = () => {
  showEmojiPopover.value = true
}
const hidePopover = () => {
  showEmojiPopover.value = false
}
const openPopover = () => {
  document.addEventListener('click', hidePopover, false)
}
const closePopover = () => {
  document.removeEventListener('click', hidePopover, false)
}

const receiveUserId = ref('0')
const message = ref('')

const emit = defineEmits(['sendMessage'])
const sendMessage = async () => {
  if (!message.value) {
    return
  }
  sendMessageDo({
    messageContent: message.value,
    messageType: 5
  })
}

const sendMessageDo = async ({
  messageContent,
  messageType,
  fileSize,
  fileName,
  fileType,
  callback
}) => {
  let result = await proxy.Request({
    url: proxy.Api.sendChatMessage,
    showLoading: false,
    params: {
      receiveUserId: receiveUserId.value,
      message: message.value,
      messageType,
      fileSize,
      fileName,
      fileType
    }
  })
  if (!result) {
    return
  }
  if (messageContent) {
    message.value = ''
  }
  if (callback) {
    callback(result.data)
  }
}

const getFileTypeByName = (fileName) => {
  const fileSuffix = fileName.substr(fileName.lastIndexOf('.') + 1)
  return getFileType(fileSuffix)
}

//上传文件
const uploadFile = async () => {
  const { filePath, fileName, fileSize } = await window.electron.ipcRenderer.invoke('selectFile')
  if (!filePath) {
    return
  }
  if (fileSize == 0) {
    proxy.Message.warning(`空文件无法上传`)
    return
  }
  const fileType = getFileTypeByName(fileName)

  if (fileType == 0 && fileSize > props.sysSetting.maxImageSize * 1024 * 1024) {
    proxy.Message.error(`图片大小不能超过${props.sysSetting.maxImageSize}MB`)
    return
  }
  if (fileType == 1 && fileSize > props.sysSetting.maxVideoSize * 1024 * 1024) {
    proxy.Message.error(`视频大小不能超过${props.sysSetting.maxVideoSize}MB`)
    return
  }
  if (fileType == 2 && fileSize > props.sysSetting.maxFileSize * 1024 * 1024) {
    proxy.Message.error(`文件大小不能超过${props.sysSetting.maxVideoSize}MB`)
    return
  }

  sendMessageDo({
    messageType: 6,
    fileSize,
    fileName,
    fileType: fileType,
    callback: ({ messageId, sendTime }) => {
      window.electron.ipcRenderer.send('uploadChatFile', {
        uploadUrl: import.meta.env.VITE_DOMAIN + proxy.Api.uploadChatFile,
        messageId,
        sendTime,
        filePath
      })
    }
  })
}
</script>

<style lang="scss" scoped>
.emoji-list {
  .emoji-item {
    float: left;
    font-size: 23px;
    padding: 2px;
    text-align: center;
    border-radius: 3px;
    margin-left: 10px;
    margin-top: 5px;
    cursor: pointer;
    &:hover {
      background: #ddd;
    }
  }
}
.chat-send-panel {
  padding: 8px;
  .chat-send-bar {
    display: flex;
    align-items: center;
    .user-select {
      display: flex;
      align-items: center;
      font-size: 14px;
      .select {
        width: 150px;
        margin-left: 5px;
      }
    }
    .iconfont {
      margin: 0px 5px;
      font-size: 20px;
      color: #4e5461;
      cursor: pointer;
    }
  }
  .input-area {
    margin-top: 5px;
    :deep {
      .el-textarea__inner {
        box-shadow: none;
        padding: 0px;
      }
    }
  }
  .send-btn-panel {
    display: flex;
    justify-content: end;
    align-items: center;
    .tips {
      margin-right: 5px;
      font-size: 13px;
      color: #8c8c8c;
    }
  }
}
</style>
