<template>
  <div class="media-window">
    <div class="header">
      <div class="media-op no-drag">
        <div
          :class="['iconfont icon-left', currentIndex == 0 ? 'not-allow' : '']"
          @dblclick.stop
          title="上一张"
          @click="next(-1)"
        ></div>
        <div
          :class="[
            'iconfont icon-right',
            currentIndex >= allFileList.length - 1 ? 'not-allow' : ''
          ]"
          @dblclick.stop
          title="下一张"
          @click="next(1)"
        ></div>
        <template v-if="currentFile.fileType == 0">
          <el-divider direction="vertical" />
          <div
            class="iconfont icon-enlarge"
            @click.stop="changeSize(0.1)"
            @dblclick.stop
            title="放大"
          ></div>
          <div
            class="iconfont icon-narrow"
            @click="changeSize(-0.1)"
            @dblclick.stop
            title="缩小"
          ></div>
          <div
            :class="['iconfont', isOne2One ? 'icon-resize' : 'icon-source-size']"
            @dblclick.stop
            @click="resize"
            :title="isOne2One ? '图片适应窗口大小' : '图片原始大小'"
          ></div>
          <div class="iconfont icon-rotate" @dblclick.stop @click="rotate" title="旋转"></div>
          <el-divider direction="vertical" />
        </template>
        <div
          class="iconfont icon-download"
          @dblclick.stop
          @click="download"
          title="另存为..."
        ></div>
      </div>
      <Titlebar :closeType="0" :styleTop="0" :styleRight="0" ref="titlbarRef"></Titlebar>
    </div>
    <div class="media-panel">
      <viewer
        :options="options"
        @inited="inited"
        :images="[currentFile.url]"
        v-if="currentFile.fileType == 0"
      >
        <img :src="currentFile.url" />
      </viewer>
      <Player v-show="currentFile.fileType == 1" ref="player"></Player>
    </div>
  </div>
</template>

<script setup>
import Player from '@/components/Player.vue'
import 'viewerjs/dist/viewer.css'
import { component as Viewer } from 'v-viewer'
import { ref, reactive, getCurrentInstance, nextTick, computed, onMounted, onUnmounted } from 'vue'
const { proxy } = getCurrentInstance()
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()

const options = ref({
  inline: true,
  toolbar: false,
  navbar: false,
  button: false,
  title: false,
  zoomRatio: 0.1,
  zoomOnWheel: false
})

const viewerMy = ref(null)
const inited = (e) => {
  viewerMy.value = e
}

//放大缩小
const changeSize = (zoomRatio) => {
  viewerMy.value.zoom(zoomRatio, true)
}
//旋转
const rotate = () => {
  viewerMy.value.rotate(90, true)
}
//原始大小
const isOne2One = ref(false)
const resize = () => {
  isOne2One.value = !isOne2One.value
  if (!isOne2One.value) {
    viewerMy.value.zoomTo(viewerMy.value.initialImageData.ratio, true)
  } else {
    viewerMy.value.zoomTo(1, true)
  }
}

const onWheel = (e) => {
  if (e.deltaY < 0) {
    changeSize(0.1)
  } else {
    changeSize(-0.1)
  }
}

//上一个下一个
const next = (index) => {
  if (currentIndex.value + index < 0 || currentIndex.value + index >= allFileList.value.length) {
    return
  }
  player.value.destroyPlayer()
  currentIndex.value = currentIndex.value + index
  getCurrentFile()
}

//初始化视频播放器
const player = ref()
const currentIndex = ref(0)
const allFileList = ref([])
const currentFile = ref({})
const getCurrentFile = () => {
  const curFile = allFileList.value[currentIndex.value]
  const url = proxy.Utils.getResroucePath(curFile)
  currentFile.value = { ...curFile, url }
  if (curFile.fileType == 1) {
    player.value.showPlayer(url)
  }
}

onUnmounted(() => {
  window.removeEventListener('wheel', onWheel)
})

const download = async () => {
  await window.electron.ipcRenderer.invoke('download', {
    url: import.meta.env.VITE_DOMAIN + proxy.Api.downloadFile,
    fileName: currentFile.value.fileName,
    messageId: currentFile.value.messageId,
    sendTime: currentFile.value.sendTime
  })
}

onMounted(() => {
  const { mediaList, currentMessageId } = route.query
  allFileList.value = JSON.parse(decodeURIComponent(mediaList))
  currentIndex.value = allFileList.value.findIndex((item) => item.messageId === currentMessageId)
  window.addEventListener('wheel', onWheel)
  getCurrentFile()
})
onUnmounted(() => {})
</script>
<style lang="scss" scoped>
.media-window {
  padding: 0px;
  background: #fff;
  position: relative;
  overflow: hidden;
  .header {
    height: 30px;
    -webkit-app-region: drag;
    display: flex;
    .media-op {
      -webkit-app-region: no-drag;
      height: 100%;
      line-height: 30px;
      display: flex;
      align-items: center;
      .iconfont {
        font-size: 18px;
        padding: 0px 10px;
        &:hover {
          background: #f3f3f3;
          cursor: pointer;
        }
      }
      .not-allow {
        cursor: not-allowed;
        color: #ddd;
        text-decoration: none;
        &:hover {
          color: #ddd;
          cursor: not-allowed;
          background: none;
        }
      }
    }
  }

  .media-panel {
    height: calc(100vh - 32px);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    :deep(.viewer-backdrop) {
      background: #f5f5f5;
    }

    .file-panel {
      .file-item {
        margin-top: 5px;
      }
      .donwload {
        margin-top: 20px;
        text-align: center;
      }
    }
  }
}
</style>
