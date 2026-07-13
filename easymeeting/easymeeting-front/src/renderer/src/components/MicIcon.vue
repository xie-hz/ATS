<template>
  <div class="mic-panel">
    <div class="mic-show" :style="{ width: size + 'px', height: size + 'px' }">
      <div
        class="iconfont icon-mic-close"
        v-if="!micDeviceInfo.open || !micDeviceInfo.enable"
      ></div>
      <div class="iconfont icon-mic" v-else></div>
      <div class="volume" :style="{ height: volume * 1.5 + 'px' }"></div>
    </div>
    <div v-if="showLabel" :class="['mic-label', micDeviceInfo.open ? 'active' : '']">
      {{ micDeviceInfo.label }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()

const props = defineProps({
  size: {
    type: Number,
    default: 30
  },
  modelValue: {
    type: Object,
    default: {}
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  defaultOpen: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])
const micDeviceInfo = ref({})
let stream = null
//获取音频设备
const getMicrophones = async () => {
  let devices = []
  try {
    devices = await navigator.mediaDevices.enumerateDevices()
  } finally {
    let defaultMic = devices.find(
      (device) => device.kind === 'audioinput' && device.deviceId === 'default'
    )
    if (!defaultMic) {
      micDeviceInfo.value = {
        deviceId: '0',
        label: '未获取到麦克风',
        open: false,
        enable: false
      }
      emit('update:modelValue', micDeviceInfo.value)
      return
    }
    const label = getDevicesLabel(defaultMic)
    const constraints = {
      audio: {
        deviceId: defaultMic.deviceId ? { exact: defaultMic.deviceId } : undefined
      },
      video: false
    }
    stream = await navigator.mediaDevices.getUserMedia(constraints).catch((error) => {})
    micDeviceInfo.value = {
      deviceId: defaultMic.deviceId,
      label,
      open: props.defaultOpen,
      enable: stream != null
    }
    emit('update:modelValue', micDeviceInfo.value)
    if (!micDeviceInfo.value.enable) {
      return
    }
    if (micDeviceInfo.value.enable && props.defaultOpen) {
      showAnimation()
    }
  }
}

//获取可用的设备名称
const getDevicesLabel = (device) => {
  let label = device.label
  // 步骤1: 去除前缀（Default - / Communications -）
  label = label.replace(/^(Default|Communications)\s*-\s*/i, '')
  // 步骤2: 去除末尾的设备ID（十六进制格式）
  label = label.replace(/\s*\([0-9a-fA-F]+:[0-9a-fA-F]+\)$/, '')
  // 步骤3: 处理多个括号的情况（只保留第一个括号及其内容）
  const matches = label.match(/^([^(]+\([^)]+\))/)
  if (matches) {
    label = matches[0]
  }
  return label
}

const toggleMic = () => {
  if (!micDeviceInfo.value.enable) {
    return
  }
  micDeviceInfo.value.open = !micDeviceInfo.value.open
  emit('update:modelValue', micDeviceInfo.value)
  if (micDeviceInfo.value.open) {
    showAnimation()
  } else {
    stopAnimation()
  }
}
defineExpose({
  toggleMic
})

//显示动画
let analyser
let microphone
const showAnimation = async () => {
  if (!stream) {
    return false
  }
  // 初始化音频上下文
  const audioContext = new (window.AudioContext || window.webkitAudioContext)()
  //使用音频上下文创建一个分析器（AnalyserNode）节点
  analyser = audioContext.createAnalyser()
  //设置分析器节点的FFT（快速傅里叶变换）大小 值越高 → 频率分辨率越高（更精细的频谱） 值越低 → 时间分辨率越高（更快的更新）
  analyser.fftSize = 2048
  // 创建音频源
  microphone = audioContext.createMediaStreamSource(stream)
  //连接节点
  microphone.connect(analyser)
  animate()
}

const animate = () => {
  // 获取音频数据
  const bufferLength = analyser.frequencyBinCount
  //// 创建用于存储音频数据的数组
  const dataArray = new Uint8Array(bufferLength)
  // 获取时域数据（波形）
  analyser.getByteTimeDomainData(dataArray)
  // 获取频域数据（频谱）
  analyser.getByteFrequencyData(dataArray)
  // 计算音量
  calculateVolume(dataArray)
  // 继续动画循环
  requestAnimationFrame(() => {
    animate()
  })
}

//音量
const volume = ref(0)
const calculateVolume = (dataArray) => {
  let sum = 0
  for (let i = 0; i < dataArray.length; i++) {
    sum += dataArray[i]
  }
  const average = sum / dataArray.length // 平均音量值 (0-255)
  volume.value = Math.min(100, Math.round((average / 255) * 100))
}

//停止动画
const stopAnimation = () => {
  if (microphone && analyser) {
    microphone.disconnect(analyser)
  }
}
onMounted(() => {
  getMicrophones()
})
</script>

<style lang="scss" scoped>
.mic-panel {
  display: flex;
  align-items: center;
  .mic-show {
    background: #ddd;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    .icon-mic {
      color: var(--blue);
    }
    .icon-mic-close {
      color: #5b5b5b;
    }
    .volume {
      position: absolute;
      left: 0px;
      right: 0px;
      bottom: 0px;
      background: rgb(4, 91, 241, 0.3);
    }
  }
  .mic-label {
    margin-left: 5px;
    font-size: 14px;
    color: #8b8b8b;
  }
  .active {
    color: #494949;
  }
}
</style>
