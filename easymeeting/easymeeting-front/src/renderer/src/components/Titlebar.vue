<template>
  <div
    class="op-btns"
    :style="{
      top: `${styleTop}px`,
      right: `${styleRight}px`,
      'border-radius': `${borderRadius}px`
    }"
  >
    <div
      :style="{
        'border-radius': `${borderRadius}px`
      }"
      v-if="showMin"
      class="iconfont icon-min"
      @click="minimize()"
      title="最小化"
    ></div>
    <div
      :style="{
        'border-radius': `${borderRadius}px`
      }"
      v-if="showMax"
      :class="['iconfont', isMax ? 'icon-maximize' : 'icon-max']"
      :title="isMax ? '还原' : '最大化'"
      @click="maximize()"
    ></div>
    <div
      :style="{
        'border-radius': `${borderRadius}px`
      }"
      v-if="showClose"
      class="iconfont icon-close"
      @click="close()"
      title="关闭"
    ></div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
const props = defineProps({
  showMin: {
    type: Boolean,
    default: true
  },
  showMax: {
    type: Boolean,
    default: false
  },
  showClose: {
    type: Boolean,
    default: true
  },
  //关闭类型 0:关闭，1:隐藏
  closeType: {
    type: Number,
    default: 1
  },
  styleTop: {
    type: Number,
    default: 0
  },
  styleRight: {
    type: Number,
    default: 0
  },
  borderRadius: {
    type: Number,
    default: 0
  },
  forceClose: {
    type: Boolean,
    default: true
  }
})

//窗口操作
const winOp = (action, data) => {
  window.electron.ipcRenderer.send('winTitleOp', { action, data })
}

//关闭窗口
const close = () => {
  winOp('close', { closeType: props.closeType, forceClose: props.forceClose })
}

const custClose = () => {
  winOp('close', { closeType: props.closeType, forceClose: true })
}

const isMax = ref(false)
//最小化
const minimize = () => {
  winOp('minimize')
}
//最大化
const maximize = () => {
  if (isMax.value) {
    winOp('unmaximize')
  } else {
    winOp('maximize')
  }
}
//置顶窗口
const isTop = ref(false)
const top = () => {
  isTop.value = !isTop.value
  winOp('top', { top: isTop.value })
}

onMounted(() => {
  isMax.value = false
  window.electron.ipcRenderer.on('winIsMax', (e, result) => {
    isMax.value = result
  })
})

onUnmounted(() => {
  window.electron.ipcRenderer.removeAllListeners('winIsMax')
})

defineExpose({
  custClose
})
</script>

<style lang="scss" scoped>
.op-btns {
  position: absolute;
  -webkit-app-region: no-drag;
  display: flex;
  .iconfont {
    color: var(--text);
    padding: 6px;
    cursor: pointer;
    &:hover {
      background: #ddd;
    }
  }
  .icon-close {
    &:hover {
      background: #fa4e32;
      color: #fff;
    }
  }
  .win-top {
    color: var(--pink);
  }
}
</style>
