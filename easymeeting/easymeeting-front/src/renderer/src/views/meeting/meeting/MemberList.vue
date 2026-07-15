<template>
  <div :class="['member-list', LIST_MAP[layoutType]]" :style="gridStyle">
    <div
      :class="[
        'member-item',
        currentSelectUserId == userInfoStore.userInfo.userId ? 'active' : '',
        proxy.Utils.isEmpty(screenId) ? 'member-my' : '',
        LAYOUT_MAP[layoutType]
      ]"
      @click="
        selectMember(
          userInfoStore.userInfo.userId,
          userInfoStore.userInfo.nickName,
          userInfoStore.userInfo.sex,
          (props.deviceInfo.cameraEnable && props.deviceInfo.cameraOpen) ||
            !proxy.Utils.isEmpty(screenId)
        )
      "
    >
      <div
        class="video-panel"
        v-show="
          (props.deviceInfo.cameraEnable && props.deviceInfo.cameraOpen) ||
          !proxy.Utils.isEmpty(screenId)
        "
      >
        <video
          :id="`member_${userInfoStore.userInfo.userId}`"
          ref="localVideoRef"
          autoplay
          playsinline
          loop
          muted
        ></video>
        <div class="video-user-name">
          <div :class="['iconfont', proxy.Utils.getSexIcon(userInfoStore.userInfo.sex)]"></div>
          <div class="user-name">{{ userInfoStore.userInfo.nickName }}</div>
        </div>
      </div>
      <div
        class="user-info"
        v-show="
          !(
            (props.deviceInfo.cameraEnable && props.deviceInfo.cameraOpen) ||
            !proxy.Utils.isEmpty(screenId)
          )
        "
      >
        <Avatar :avatar="userInfoStore.userInfo.userId" :update="true"> </Avatar>
        <div :class="['user-name', 'iconfont', proxy.Utils.getSexIcon(userInfoStore.userInfo.sex)]">
          {{ userInfoStore.userInfo.nickName }}
        </div>
      </div>
    </div>
    <div
      :class="[
        'member-item',
        currentSelectUserId == item.userId ? 'active' : '',
        LAYOUT_MAP[layoutType]
      ]"
      v-for="(item, index) in memberList"
      @click="selectMember(item.userId, item.nickName, item.sex, item.openVideo)"
    >
      <div class="video-panel" v-show="item.openVideo">
        <video autoplay playsinline :id="`member_${item.userId}`" loop></video>
        <div class="video-user-name">
          <div :class="['iconfont', proxy.Utils.getSexIcon(item.sex)]"></div>
          <div class="user-name">{{ item.nickName }}</div>
        </div>
      </div>
      <div class="user-info" v-show="!item.openVideo">
        <Avatar :avatar="item.userId" :update="true"> </Avatar>
        <div :class="['user-name', 'iconfont', proxy.Utils.getSexIcon(item.sex)]">
          {{ item.nickName }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, getCurrentInstance, nextTick, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
import { useUserInfoStore } from '@/stores/UserInfoStore'
const userInfoStore = useUserInfoStore()

import { useMeetingStore } from '@/stores/MeetingStore'
const meetingStore = useMeetingStore()
import { mitter } from '@/eventbus/eventBus.js'

const props = defineProps({
  deviceInfo: {
    type: Object,
    default: {}
  }
})
const currentSelectUserId = ref()
const screenId = ref(route.query.screenId)
const layoutType = ref(0)

const LIST_MAP = {
  0: 'member-list',
  1: 'member-list-top',
  2: 'member-list-right'
}

const LAYOUT_MAP = {
  0: 'member-item',
  1: 'member-item-top',
  2: 'member-item-right'
}

const memberList = ref([])
const gridStyle = computed(() => {
  if (layoutType.value != 0) {
    return ''
  }
  const { rows, cols } = calculateGrid(memberList.value.length + 1)
  return {
    gridTemplateRows: `repeat(${rows}, 1fr)`,
    gridTemplateColumns: `repeat(${cols}, 1fr)`
  }
})
const calculateGrid = (participantCount) => {
  if (participantCount <= 0) return { cols: 0, rows: 0 }
  if (participantCount === 1) return { cols: 1, rows: 1 }
  let cols = Math.ceil(Math.sqrt(participantCount))
  let rows = Math.ceil(participantCount / cols)
  return { cols, rows }
}

//创建空的视频轨道
const createEmptyVideoTrack = () => {
  const canvas = document.createElement('canvas')
  canvas.width = 1
  canvas.height = 1
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = 'black'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  const stream = canvas.captureStream(1)
  return stream.getVideoTracks()[0]
}

// 创建一个静音的音频轨道
const createEmptyAudioTrack = () => {
  const audioContext = new AudioContext()
  const oscillator = audioContext.createOscillator()
  const dst = oscillator.connect(audioContext.createMediaStreamDestination())
  oscillator.start()
  const track = dst.stream.getAudioTracks()[0]
  // 禁用轨道使其静音
  track.enabled = false
  return track
}

const localVideoRef = ref()
let cameraStream = null
let screenStream = null
let localStream = null
const initLocalStream = async () => {
  await nextTick()
  localStream = new MediaStream()
  //没有麦克风 加入空通道
  if (!props.deviceInfo.micEnable) {
    const micTrack = createEmptyAudioTrack()
    micTrack.enabled = false
    localStream.addTrack(micTrack)
  }
  //有麦克风或者有摄像头，先加入通道，不开启
  if (props.deviceInfo.cameraEnable || props.deviceInfo.micEnable) {
    await initLocalCameraStream(props.deviceInfo.cameraEnable, props.deviceInfo.micEnable)
    cameraStream.getTracks().forEach((track) => {
      track.enabled = false
      localStream.addTrack(track)
    })
  }
  //没有摄像头，也不是共享屏幕，添加空的视频轨道
  if (!props.deviceInfo.cameraEnable && !screenId.value) {
    const videoTrack = createEmptyVideoTrack()
    videoTrack.enabled = false
    localStream.addTrack(videoTrack)
  }
  if (screenId.value) {
    //如果有视频轨道，替换视频轨道,增加屏幕视频轨道
    const videoTrackes = localStream.getVideoTracks()
    if (videoTrackes.length > 0) {
      localStream.removeTrack(videoTrackes[0])
      videoTrackes[0].stop()
    }
    //共享屏幕，增加视频轨道
    await initLocalScreenStream()
    localStream.addTrack(screenStream.getVideoTracks()[0])
  } else if (!screenId.value && (props.deviceInfo.cameraEnable || props.deviceInfo.micEnable)) {
    //不共享屏幕，分别开启音频轨道，视频轨道
    localStream.getTracks().forEach((track) => {
      if (track.kind === 'audio') {
        track.enabled = props.deviceInfo.micOpen
      }
      if (track.kind === 'video') {
        track.enabled = props.deviceInfo.cameraOpen
      }
    })
  } else if (!screenId.value && !props.deviceInfo.cameraEnable) {
    //不共享屏幕，也没有摄像头，添加空视频轨道
    const videoTrack = createEmptyVideoTrack()
    videoTrack.enabled = false
    localStream.addTrack(videoTrack)
  }
  localVideoRef.value.srcObject = localStream
  //加入会议
  joinMeeting(
    (props.deviceInfo.cameraEnable && props.deviceInfo.cameraOpen) ||
      !proxy.Utils.isEmpty(screenId.value)
  )
}
const initLocalCameraStream = async (video, audio) => {
  return new Promise(async (resolve, reject) => {
    if (!props.deviceInfo.cameraEnable && !props.deviceInfo.micEnable) {
      cameraStream = null
      resolve(null)
      return
    }
    const stream = await navigator.mediaDevices
      .getUserMedia({
        video,
        audio
      })
      .catch((error) => {
        console.log(error)
      })
    cameraStream = stream
    resolve(stream)
  })
}

const initLocalScreenStream = async () => {
  return new Promise(async (resolve, reject) => {
    const constraints = {
      mandatory: {
        chromeMediaSource: 'desktop',
        chromeMediaSourceId: screenId.value,
        minWidth: 1024,
        maxWidth: 1600,
        minHeight: 768,
        maxHeight: 900,
        minFrameRate: 10,
        maxFrameRate: 25
      }
    }
    const stream = await navigator.mediaDevices
      .getUserMedia({
        audio: false, //启用系统声音
        video: constraints
      })
      .catch((error) => {
        console.error(error)
      })
    screenStream = stream
    resolve(stream)
    return
  })
}

//加入会议
const joinMeeting = async (videoOpen) => {
  let result = await proxy.Request({
    url: proxy.Api.joinMeeting,
    params: {
      videoOpen
    },
    showLoading: false
  })
  if (!result) {
    return
  }
}

const peerConnectionMap = new Map()
const remoteStreams = new Map() // userId -> MediaStream（已收到的远端流，避免 ontrack 早于视频元素渲染时丢失）
const SIGNAL_TYPE_OFFER = 'offer'
const SIGNAL_TYPE_ANSWER = 'answer'
const SIGNAL_TYPE_CANDIDATE = 'candidate'
const createPeerConnection = (member) => {
  let peerConnection = peerConnectionMap.get(member.userId)
  if (peerConnection) {
    return peerConnection
  }
  peerConnection = new RTCPeerConnection({
    sdpSemantics: 'unified-plan', // 明确使用现代标准
    codecs: { video: 'VP8' }, // 强制优先使用 VP8
    bundlePolicy: 'balanced', //优化媒体传输通道的绑定策略
    rtcpMuxPolicy: 'require', //强制 RTP/RTCP 多路复用
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  })

  // localStream 始终包含视频+音频轨道（无摄像头时为空画布轨道、无麦克风时为静音轨道）。
  // 不再为"关闭的设备"添加 recvonly transceiver——否则 addTrack 会复用它，
  // 导致 offer 的视频 m-line 变成 recvonly，本端不发送视频，对端 ontrack 不触发（黑屏），
  // 且屏幕共享时没有 video sender 可 replaceTrack。统一用 addTrack 建立 sendrecv 轨道。
  // ICE候选处理
  peerConnection.onicecandidate = (e) => {
    if (e.candidate) {
      sendPeerMessage({
        sendUserId: userInfoStore.userInfo.userId,
        signalType: SIGNAL_TYPE_CANDIDATE,
        signalData: e.candidate,
        receiveUserId: member.userId
      })
    }
  }
  // 处理远程视频流
  peerConnection.ontrack = (event) => {
    // 优先用发送方关联的流；若没有则把轨道挂到已有/新建流上
    let stream = event.streams[0]
    if (!stream) {
      stream = remoteStreams.get(member.userId) || new MediaStream()
      if (event.track && !stream.getTracks().includes(event.track)) stream.addTrack(event.track)
    }
    remoteStreams.set(member.userId, stream)
    bindRemoteVideo(member.userId)
  }
  // ICE 连通后再次绑定，确保开始解码渲染
  peerConnection.onconnectionstatechange = () => {
    if (peerConnection.connectionState === 'connected') bindRemoteVideo(member.userId)
  }
  localStream.getTracks().forEach((track) => {
    peerConnection.addTrack(track, localStream)
  })
  peerConnectionMap.set(member.userId, peerConnection)
  return peerConnection
}

// 把已收到的远端流绑定到对应视频元素；元素可能尚未渲染，调用方在成员列表变化后会重绑
const bindRemoteVideo = (userId) => {
  const stream = remoteStreams.get(userId)
  if (!stream) return
  nextTick(() => {
    const remoteVideo = document.querySelector('#member_' + userId)
    if (remoteVideo) {
      if (remoteVideo.srcObject !== stream) remoteVideo.srcObject = stream
      remoteVideo.play().catch(() => {})
    }
  })
}

//用户加入
const onUserJoin = async (messageContent) => {
  console.log(messageContent)
  const newMember = messageContent.newMember
  const allMemberList = messageContent.meetingMemberList.sort((a, b) => a.joinTime - b.joinTime)
  memberList.value = allMemberList.filter((item) => {
    return item.userId != userInfoStore.userInfo.userId && item.status == 1
  })
  meetingStore.setMemberList(memberList.value)
  meetingStore.setAllMemberList(allMemberList)

  await nextTick()
  if (newMember.userId !== userInfoStore.userInfo.userId) {
    //已经在会议中的用户，与新用户建立peer
    proxy.Message.success(`用户${newMember.nickName}加入了会议`)
    createPeerConnection(newMember)
    return
  }
  //新加入的用户与其他用户建立peer 并且发送offer
  memberList.value.forEach(async (member) => {
    const peerConnection = createPeerConnection(member)
    sendOffer(peerConnection, userInfoStore.userInfo.userId, member.userId)
  })
}

const sendOffer = async (peerConnection, sendUserId, receiveUserId) => {
  let offer = await peerConnection.createOffer({ iceRestart: true })
  console.log('offer send to ' + receiveUserId, offer)
  await peerConnection.setLocalDescription(offer)
  sendPeerMessage({
    sendUserId,
    receiveUserId,
    signalType: SIGNAL_TYPE_OFFER,
    signalData: offer
  })
}

const sendPeerMessage = async ({ sendUserId, receiveUserId, signalType, signalData }) => {
  window.electron.ipcRenderer.send('sendPeerConnection', {
    sendUserId,
    receiveUserId,
    signalType,
    signalData: JSON.stringify(signalData)
  })
}

//建立 peerConnection
const onPeerConnection = async ({ sendUserId, receiveUserId, messageContent }) => {
  if (receiveUserId != userInfoStore.userInfo.userId) {
    return
  }
  const signalData = messageContent.signalData ? JSON.parse(messageContent.signalData) : {}

  const member = memberList.value.find((item) => {
    return item.userId == sendUserId
  })
  const peerConnection = createPeerConnection(member)
  try {
    switch (messageContent.signalType) {
      case SIGNAL_TYPE_OFFER: {
        // 如果 PC 已连接，忽略重复 offer
        if (peerConnection.connectionState === 'connected') {
          break
        }
        // 如果 PC 处于 have-local-offer 状态（glare），关闭重建
        if (peerConnection.signalingState === 'have-local-offer') {
          peerConnection.close()
          peerConnectionMap.delete(sendUserId)
          remoteStreams.delete(sendUserId)
          const newPc = createPeerConnection(member)
          await newPc.setRemoteDescription(signalData)
          const answer = await newPc.createAnswer()
          await newPc.setLocalDescription(answer)
          sendPeerMessage({
            sendUserId: receiveUserId,
            receiveUserId: sendUserId,
            signalType: SIGNAL_TYPE_ANSWER,
            signalData: answer
          })
          break
        }
        //设置offer
        await peerConnection.setRemoteDescription(signalData)
        //创建answer
        const answer = await peerConnection.createAnswer()
        await peerConnection.setLocalDescription(answer)
        //发送answer到信令服务器
        sendPeerMessage({
          sendUserId: receiveUserId,
          receiveUserId: sendUserId,
          signalType: SIGNAL_TYPE_ANSWER,
          signalData: answer
        })
        break
      }
      case SIGNAL_TYPE_ANSWER: {
        console.log('answer from user ' + sendUserId, signalData)
        await peerConnection.setRemoteDescription(signalData)
        break
      }
      case SIGNAL_TYPE_CANDIDATE: {
        if (!peerConnection.remoteDescription) {
          return
        }
        peerConnection.addIceCandidate(signalData)
        break
      }
    }
  } catch (error) {
    console.error('err', error)
  }
}

const initMessageListener = () => {
  window.electron.ipcRenderer.on(
    'meetingMessage',
    (e, { sendUserId, receiveUserId, messageContent, messageType }) => {
      // console.log(sendUserId, receiveUserId, messageContent, messageType)
      switch (messageType) {
        case 1: //新用户加入
          onUserJoin(messageContent)
          break
        case 2: //建立peerconnection
          onPeerConnection({ sendUserId, receiveUserId, messageContent })
          break
        case 3: //用户退出
          onUserLeave(messageContent)
          break
        case 4: //会议结束
          meetingFinish(messageContent)
          break
        case 11: //用户视频状态改变
          memberVideoChange(sendUserId, messageContent)
          break
      }
    }
  )
}

const emit = defineEmits(['exitMeeting', 'selectMember'])
const onUserLeave = (messageContent) => {
  const { exitUserId, meetingMemberList } = JSON.parse(messageContent)
  //如果退出是自己，窗口关闭
  if (userInfoStore.userInfo.userId === exitUserId) {
    emit('exitMeeting')
    return
  }
  memberList.value = memberList.value.filter((item) => item.userId != exitUserId)
  meetingStore.setAllMemberList(meetingMemberList)
  meetingStore.setMemberList(memberList.value)
  const exitPc = peerConnectionMap.get(exitUserId)
  if (exitPc) exitPc.close()
  peerConnectionMap.delete(exitUserId)
  remoteStreams.delete(exitUserId)
}

const meetingFinish = (messageContent) => {
  emit('exitMeeting')
}

//开启关闭音频
const micSwitchHandler = async (open) => {
  if (localStream) {
    //改变开关，修改麦克风通道状态
    localStream.getAudioTracks().forEach((track) => (track.enabled = open))
  }
  memberList.value.forEach(async (member) => {
    const pc = peerConnectionMap.get(member.userId)
    const sender = pc.getSenders().find((sender) => sender.track && sender.track.kind === 'audio')
    sender.track.enabled = open
  })
}

//开启关闭摄像头
const cameraSwitchHandler = async (open) => {
  if (cameraStream) {
    //开关，修改摄像头通道的开关
    cameraStream.getVideoTracks().forEach((track) => (track.enabled = open))
  }
  if (screenId.value) {
    return
  }
  sendOpenVideoChangeMessage(open)
  //摄像头原本关闭，现在开启，同时取消了屏幕共享，切换轨道流
  if (!screenId.value && open) {
    const videoTrack = cameraStream.getVideoTracks()[0]
    videoTrack.enabled = true
    memberList.value.forEach(async (member) => {
      //切换视频流
      const peerConnection = peerConnectionMap.get(member.userId)
      peerConnection.getSenders().forEach((sender) => {
        if (sender.track && sender.track.kind === 'video') {
          sender.replaceTrack(videoTrack)
        }
      })
    })
    localVideoRef.value.srcObject = cameraStream
  }

  if (currentSelectUserId.value == userInfoStore.userInfo.userId) {
    emit('selectMember', {
      srcObject: localVideoRef.value.srcObject,
      userId: userInfoStore.userInfo.userId,
      nickName: userInfoStore.userInfo.userName,
      sex: userInfoStore.userInfo.sex,
      openVideo: open
    })
  }
}

//发送用户开启，关闭摄像头
const sendOpenVideoChangeMessage = async (openVideo) => {
  let result = await proxy.Request({
    url: proxy.Api.sendOpenVideoChangeMessage,
    params: {
      openVideo
    }
  })
  if (!result) {
    return
  }
}

//用户摄像头改变
const memberVideoChange = (sendUserId, openVideo) => {
  if (sendUserId === userInfoStore.userInfo.userId) {
    return
  }
  const member = memberList.value.find((item) => {
    return item.userId === sendUserId
  })
  member.openVideo = openVideo

  // replaceTrack 后接收方视频元素可能不自动刷新（黑屏），强制重绑流触发重新解码
  nextTick(() => {
    const remoteVideo = document.querySelector('#member_' + sendUserId)
    if (remoteVideo) {
      const current = remoteVideo.srcObject
      remoteVideo.srcObject = null
      remoteVideo.srcObject = current
      remoteVideo.play().catch(() => {})
    }
  })

  //选中的用户等于成员，就改变状态
  if (currentSelectUserId.value == member.userId) {
    emit('selectMember', {
      srcObject: document.querySelector('#member_' + member.userId).srcObject,
      userId: member.userId,
      nickName: member.nickName,
      sex: member.sex,
      openVideo
    })
  }
}

//选择屏幕共享
const shareScreenHandler = async (_screenId) => {
  sendOpenVideoChangeMessage(
    (props.deviceInfo.cameraEnable && props.deviceInfo.cameraOpen) ||
      !proxy.Utils.isEmpty(_screenId)
  )
  const oldScreenId = screenId.value
  screenId.value = _screenId
  //判断是取消还是开启共享
  if (!proxy.Utils.isEmpty(_screenId) && (!screenStream || oldScreenId !== _screenId)) {
    //桌面流不存在或者切换了桌面，重新获取桌面流
    await initLocalScreenStream()
    localStream = screenStream
  } else if (proxy.Utils.isEmpty(_screenId) && props.deviceInfo.cameraOpen) {
    localStream = cameraStream
  }
  localVideoRef.value.srcObject = localStream
  //替换视频流
  const videoTrack = localStream ? localStream.getVideoTracks()[0] : null
  memberList.value.forEach(async (member) => {
    //切换视频流
    const peerConnection = peerConnectionMap.get(member.userId)
    peerConnection.getSenders().forEach((sender) => {
      if (sender.track && sender.track.kind === 'video') {
        console.log('sender trck', sender.track)
        if (videoTrack) {
          sender.replaceTrack(videoTrack)
        } else {
          sender.track.enabled = false
        }
      }
    })
  })

  //切换选中
  if (currentSelectUserId.value == userInfoStore.userInfo.userId) {
    emit('selectMember', {
      srcObject: localStream,
      userId: userInfoStore.userInfo.userId,
      nickName: userInfoStore.userInfo.nickName,
      sex: userInfoStore.userInfo.sex,
      openVideo:
        (props.deviceInfo.cameraEnable && props.deviceInfo.cameraOpen) ||
        !proxy.Utils.isEmpty(_screenId)
    })
  }
}

const layoutChangeHandler = (type) => {
  if (layoutType.value == type) {
    return
  }
  layoutType.value = type
  if (type !== 0 && !currentSelectUserId.value) {
    currentSelectUserId.value = userInfoStore.userInfo.userId
    //改变布局，没有选中的，就默认选中自己
    emit('selectMember', {
      srcObject: localVideoRef.value.srcObject,
      userId: userInfoStore.userInfo.userId,
      nickName: userInfoStore.userInfo.nickName,
      sex: userInfoStore.userInfo.sex,
      openVideo:
        (props.deviceInfo.cameraEnable && props.deviceInfo.cameraOpen) ||
        !proxy.Utils.isEmpty(screenId.value)
    })
  }
}
//选择用户  出发用用户选择改变的场景 1、切换布局，默认选中第一个 2、用户手动选择 3、开启关闭视频 4、共享屏幕
const selectMember = (userId, nickName, sex, openVideo) => {
  if (layoutType.value === 0) {
    return
  }
  if (currentSelectUserId.value !== userId) {
    emit('selectMember', {
      srcObject: document.querySelector('#member_' + userId).srcObject,
      userId,
      nickName,
      sex,
      openVideo
    })
  }
  currentSelectUserId.value = userId
}

onMounted(() => {
  mitter.on('layoutChange', layoutChangeHandler)
  mitter.on('shareScreen', shareScreenHandler)
  mitter.on('micSwitch', micSwitchHandler)
  mitter.on('cameraSwitch', cameraSwitchHandler)
  initLocalStream()
  initMessageListener()
})

// 成员列表渲染后，把已收到的远端流重新绑定到对应视频元素。
// 修复竞态：ontrack 可能在 <video> 元素渲染出来之前触发，导致 srcObject 没绑上（黑屏）。
watch(memberList, () => {
  nextTick(() => {
    remoteStreams.forEach((_, userId) => bindRemoteVideo(userId))
  })
})

onUnmounted(() => {
  mitter.off('layoutChange', layoutChangeHandler)
  mitter.off('shareScreen', shareScreenHandler)
  mitter.off('micSwitch', micSwitchHandler)
  mitter.off('cameraSwitch', cameraSwitchHandler)
  window.electron.ipcRenderer.removeAllListeners('meetingMessage')
})
</script>

<style lang="scss" scoped>
.member-list {
  height: 100%;
  display: grid;
  gap: 8px;
  max-height: 100%;
  padding: 10px;
  background: #fff;
  transition: grid-template 0.3s ease;
  overflow-y: auto;
}

.member-list-top {
  display: inline-flex;
  grid-gap: 0px;
  padding: 10px 0px 10px 10px;
  overflow-x: auto;
  max-width: 100%;
  height: 120px;
  .member-item {
    cursor: pointer;
  }
  .active {
    border: 2px solid var(--blue);
  }
}

.member-list-right {
  display: flex;
  flex-direction: column;
  grid-gap: 0px;
  padding: 10px 10px 0px 10px;
  width: 130px;
  align-items: center;
  margin: auto;
  .member-item {
    cursor: pointer;
  }
  .active {
    border: 2px solid var(--blue);
  }
}

.member-item {
  background: #f7f7f7;
  position: relative;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 8px;
  border: 2px solid #fff;
  .video-panel {
    height: 100%;
    position: relative;
    video {
      height: 100%;
      width: 100%;
      object-fit: cover;
    }
    .video-user-name {
      position: absolute;
      top: 0px;
      right: 0px;
      display: flex;
      align-items: center;
      border-radius: 0px 0px 0px 5px;
      overflow: hidden;
      .iconfont {
        width: 20px;
        height: 20px;
        background: var(--blue);
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .icon-woman {
        background: #fb7373;
      }
      .user-name {
        background: rgb(0, 0, 0, 0.8);
        color: #fff;
        font-size: 12px;
        height: 20px;
        padding: 0px 3px;
        max-width: 80px;
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
        padding-top: 2px;
      }
    }
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

.member-my {
  video {
    transform: scaleX(-1);
  }
}

.member-item-top {
  width: 100px;
  height: 100px;
  margin-right: 10px;
  .video-panel {
    width: 100px;
    height: 100px;
  }
}
.member-item-right {
  width: 100px;
  height: 100px;
  margin-bottom: 10px;

  .video-panel {
    width: 100px;
    height: 100px;
  }
}
</style>
