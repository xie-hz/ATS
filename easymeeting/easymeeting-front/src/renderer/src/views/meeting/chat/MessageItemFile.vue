<template>
  <div class="file-panel">
    <div class="file-name" :title="data.fileName">{{ data.fileName }}</div>
    <div class="file-size">{{ proxy.Utils.size2Str(data.fileSize) }}</div>
    <div class="uploading" v-if="data.status === 0">
      <el-progress type="circle" :percentage="data.uploadProgress||0" :width="80" />
    </div>
    <div v-if="data.downloadProgress!=null" class="progress">
      <div v-if="data.downloadProgress<100" class="downloading">
        <span class="iconfont icon-download"></span>
        <el-progress :stroke-width="5" :percentage="data.downloadProgress" />
      </div>
      <div class="download-complete" v-else>
        <div class="iconfont icon-success download-success">下载完成</div>
        <div class="iconfont icon-folder" title="打开" @click="openLocalFile"></div>
      </div>
    </div>
    <div class="iconfont icon-download download-link" @click="download" v-else>下载</div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick } from 'vue'
const { proxy } = getCurrentInstance()

const props = defineProps({
  data: {
    type: Object,
    default: {}
  }
})

const download = async () => {
  const savePath = await window.electron.ipcRenderer.invoke('download', {
    url: import.meta.env.VITE_DOMAIN + proxy.Api.downloadFile,
    fileName: props.data.fileName,
    messageId: props.data.messageId,
    sendTime: props.data.sendTime
  })
  if (!savePath) {
    return
  }
  props.data.downloadProgress = 0
}

const openLocalFile = () => {
  window.electron.ipcRenderer.send('openLocalFile', {
    localFilePath: props.data.localFilePath
  })
}
</script>

<style lang="scss" scoped>
.file-panel {
  margin-top: 5px;
  display: flex;
  padding: 15px 10px 10px 10px;
  background: #e2e2e2;
  border: 1px solid #ddd;
  border-radius: 5px;
  width: 200px;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  .file-name {
    font-size: 14px;
    overflow: hidden; /* 隐藏溢出内容（必要） */
    text-overflow: ellipsis; /* 超出显示省略号（兼容性兜底） */
    white-space: nowrap;
  }
  .file-size {
    margin-top: 5px;
    font-size: 12px;
    color: #6e6e6e;
  }
  .uploading {
    width: 100%;
    height: 100%;
    position: absolute;
    left: 0px;
    top: 0px;
    background: rgb(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    :deep {
      .el-progress__text {
        color: #20a0ff;
      }
    }
  }
  .download-link {
    margin-top: 5px;
    text-align: right;
    font-size: 12px;
    color: var(--blue);
    cursor: pointer;
    &::before {
      font-size: 16px;
      margin-right: 2px;
    }
  }
  .progress {
    margin-top: 5px;
    .downloading {
      display: flex;
      align-items: center;
      .icon-download {
        margin-right: 5px;
        color: var(--blue);
      }
      :deep {
        .el-progress {
          flex: 1;
        }
        .el-progress__text {
          min-width: 20px;
        }
      }
    }

    .download-complete {
      display: flex;
      align-items: center;
      justify-content: space-between;
      .download-success {
        color: green;
        font-size: 13px;
        display: flex;
        align-items: center;
        &::before {
          font-size: 16px;
          margin-right: 2px;
        }
      }
    }

    .icon-folder {
      font-size: 20px;
      cursor: pointer;
      color: var(--blue);
    }
  }
}
</style>
