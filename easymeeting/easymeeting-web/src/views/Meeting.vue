<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from "vue"
import { ElMessage } from "element-plus"
import { joinMeeting, exitMeeting, sendVideoChange, sendMessage } from "../api"
import { connectSignaling, sendPeer, closeSignaling } from "../ws"
import { iceServers } from "../config"

const props = defineProps({
  session: { type: Object, required: true },
})
const emit = defineEmits(["leave"])

const me = props.session // { token, userId, meetingId, meetingNo, meetingName }
const meetingName = ref(me.meetingName || "视频面试")
const members = ref([]) // other participants (MeetingMemberDto[], excludes self)
const micOpen = ref(true)
const cameraOpen = ref(true)
const localReady = ref(false)

// 右侧面板：参会人 / 聊天
const panelOpen = ref(false)
const panelTab = ref("members") // "members" | "chat"
const chatMessages = ref([])
const chatInput = ref("")
const chatScrollRef = ref(null)

let localStream = null
const pcs = new Map() // userId -> RTCPeerConnection
const videoRefs = {} // userId -> <video> element (remote)

// ICE servers: STUN + optional TURN (coturn, Phase 4). See src/config.js.
const ICE_SERVERS = iceServers

onMounted(start)
onBeforeUnmount(cleanup)

async function start() {
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    micOpen.value = true
    cameraOpen.value = true
    localReady.value = true
    await nextTick()
    const localEl = document.getElementById("video-local")
    if (localEl) localEl.srcObject = localStream
  } catch (e) {
    ElMessage.error("无法访问摄像头/麦克风：" + e.message)
  }
  // 连接信令（等 WS 打开后，后端 channel 已注册，再 joinMeeting 才能收到成员广播）
  await connectSignaling({
    userId: me.userId,
    onJoin,
    onPeer,
    onExit,
    onFinish,
    onVideoChange,
    onChat,
    onReconnect: async () => {
      // WS 重连成功后重新加入会议（恢复 Redis 房间成员状态 + 通知其他人）
      try { await joinMeeting(true) } catch { /* ignore */ }
    },
    onClose: () => ElMessage.warning("信令连接断开"),
  })
  try {
    await joinMeeting(true)
  } catch (e) {
    ElMessage.error("加入会议失败：" + (e.message || ""))
  }
}

// ---- 信令回调 ----

function onJoin(content) {
  const list = content.meetingMemberList || []
  const newMember = content.newMember
  // 更新在会成员（排除自己，仅状态正常）
  members.value = list.filter((m) => m.userId !== me.userId && m.status === 1)
  nextTick(bindRemoteVideos)
  if (newMember && newMember.userId === me.userId) {
    // 我刚加入：主动与已在的人建连（发起 offer）
    members.value.forEach((m) => {
      createPC(m.userId)
      sendOffer(m.userId)
    })
  } else if (newMember && newMember.userId !== me.userId) {
    // 别人加入：建 PC 等对方 offer
    createPC(newMember.userId)
  }
}

function onPeer(sendUserId, content) {
  const { signalType, signalData } = content
  let pc = pcs.get(sendUserId)
  if (signalType === "offer") {
    if (!pc) pc = createPC(sendUserId)
    pc.setRemoteDescription(JSON.parse(signalData))
      .then(() => pc.createAnswer())
      .then((answer) => pc.setLocalDescription(answer))
      .then(() => sendPeer(sendUserId, "answer", pc.localDescription))
  } else if (signalType === "answer") {
    if (pc) pc.setRemoteDescription(JSON.parse(signalData))
  } else if (signalType === "candidate") {
    if (pc) {
      try {
        pc.addIceCandidate(JSON.parse(signalData))
      } catch {
        /* remoteDescription 尚未设置，忽略 */
      }
    }
  }
}

function onExit(content) {
  const exitUserId = content.exitUserId
  if (exitUserId === me.userId) {
    leave()
    return
  }
  members.value = (content.meetingMemberList || []).filter(
    (m) => m.userId !== me.userId && m.status === 1,
  )
  closePC(exitUserId)
}

function onFinish() {
  ElMessage.info("会议已结束")
  leave()
}

function onVideoChange(sendUserId, openVideo) {
  const m = members.value.find((x) => x.userId === sendUserId)
  if (m) m.openVideo = openVideo
}

// ---- 聊天 ----

function onChat(msg) {
  // 后端 saveChatMessage 用 CopyTools.copy 把 MeetingChatMessage 复制到 MessageSendDto，
  // 所以 WS 消息的顶层就是各字段：messageContent(纯文本)、sendUserId、sendUserNickName 等。
  const c = msg.messageContent
  let text = ""
  if (typeof c === "string") {
    text = c // 文本消息：messageContent 就是纯文本
  } else if (c && typeof c === "object") {
    text = c.messageContent || c.text || JSON.stringify(c)
  }
  chatMessages.value.push({
    messageId: msg.messageId,
    sendUserId: msg.sendUserId || "",
    sendUserNickName: msg.sendUserNickName || "参会者",
    messageContent: text,
    messageType: msg.messageType,
    sendTime: msg.sendTime,
    isMe: (msg.sendUserId || "") === me.userId,
  })
  nextTick(() => {
    const el = chatScrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

async function sendChat() {
  const text = chatInput.value.trim()
  if (!text) return
  try {
    await sendMessage(text, "0", 5)
    chatInput.value = ""
  } catch (e) {
    ElMessage.error("发送失败：" + (e.message || ""))
  }
}

// 面板切换
function togglePanel(tab) {
  if (panelOpen.value && panelTab.value === tab) {
    panelOpen.value = false
  } else {
    panelTab.value = tab
    panelOpen.value = true
  }
}

// ---- WebRTC ----

function createPC(userId) {
  if (pcs.has(userId)) return pcs.get(userId)
  const pc = new RTCPeerConnection({ iceServers: ICE_SERVERS })
  // 本地轨道加入
  if (localStream) {
    localStream.getTracks().forEach((t) => pc.addTrack(t, localStream))
  }
  pc.onicecandidate = (e) => {
    if (e.candidate) sendPeer(userId, "candidate", e.candidate)
  }
  pc.ontrack = (e) => {
    nextTick(() => {
      const el = document.getElementById("video-" + userId)
      if (el) el.srcObject = e.streams[0]
    })
  }
  pcs.set(userId, pc)
  return pc
}

async function sendOffer(userId) {
  const pc = pcs.get(userId)
  if (!pc) return
  const offer = await pc.createOffer()
  await pc.setLocalDescription(offer)
  sendPeer(userId, "offer", pc.localDescription)
}

function closePC(userId) {
  const pc = pcs.get(userId)
  if (pc) {
    pc.close()
    pcs.delete(userId)
  }
}

function bindRemoteVideos() {
  // 占位：实际远端流在 ontrack 中按 id 绑定
}

// ---- 控制 ----

function toggleMic() {
  micOpen.value = !micOpen.value
  if (localStream) {
    localStream.getAudioTracks().forEach((t) => (t.enabled = micOpen.value))
  }
}

function toggleCamera() {
  cameraOpen.value = !cameraOpen.value
  if (localStream) {
    localStream.getVideoTracks().forEach((t) => (t.enabled = cameraOpen.value))
  }
  sendVideoChange(cameraOpen.value).catch(() => {})
}

async function leave() {
  try {
    await exitMeeting()
  } catch {
    /* ignore */
  }
  cleanup()
  emit("leave")
}

function cleanup() {
  closeSignaling()
  pcs.forEach((pc) => pc.close())
  pcs.clear()
  if (localStream) {
    localStream.getTracks().forEach((t) => t.stop())
    localStream = null
  }
}
</script>

<template>
  <div class="meeting-wrap">
    <header class="meeting-header">
      <span class="title">{{ meetingName }}</span>
      <span class="meta">会议号 {{ me.meetingNo }}</span>
    </header>

    <div class="meeting-body">
      <div class="video-grid">
        <!-- 本地 -->
        <div class="video-cell">
          <video id="video-local" autoplay playsinline muted></video>
          <div class="name">{{ me.userId.startsWith("G") && !me.userId.match(/^\d/) ? "我（访客）" : "我" }}</div>
        </div>
        <!-- 远端 -->
        <div v-for="m in members" :key="m.userId" class="video-cell">
          <video :id="'video-' + m.userId" autoplay playsinline></video>
          <div class="name">
            {{ m.nickName }}
            <span v-if="m.memberType === 1" class="host">主持</span>
            <span v-if="!m.openVideo" class="off">（摄像头关闭）</span>
          </div>
        </div>
      </div>

      <!-- 右侧面板：参会人 / 聊天 -->
      <div v-if="panelOpen" class="side-panel">
        <div class="panel-tabs">
          <div :class="['tab', panelTab === 'members' ? 'active' : '']" @click="panelTab = 'members'">
            参会人（{{ members.length + 1 }}）
          </div>
          <div :class="['tab', panelTab === 'chat' ? 'active' : '']" @click="panelTab = 'chat'">
            聊天
          </div>
        </div>

        <!-- 参会人列表 -->
        <div v-if="panelTab === 'members'" class="panel-content">
          <div class="member-item">
            <span class="dot self"></span>
            <span class="nick">{{ me.userId.startsWith("G") && !me.userId.match(/^\d/) ? "我（访客）" : "我" }}</span>
          </div>
          <div v-for="m in members" :key="m.userId" class="member-item">
            <span :class="['dot', m.openVideo ? 'online' : 'off']"></span>
            <span class="nick">{{ m.nickName }}</span>
            <span v-if="m.memberType === 1" class="host-tag">主持</span>
          </div>
        </div>

        <!-- 聊天 -->
        <div v-if="panelTab === 'chat'" class="panel-content chat-panel">
          <div ref="chatScrollRef" class="chat-list">
            <div v-for="msg in chatMessages" :key="msg.messageId" :class="['chat-msg', msg.isMe ? 'me' : '']">
              <div class="chat-nick">{{ msg.isMe ? "我" : msg.sendUserNickName }}</div>
              <div class="chat-text">{{ msg.messageContent }}</div>
            </div>
            <div v-if="chatMessages.length === 0" class="chat-empty">暂无消息</div>
          </div>
          <div class="chat-input">
            <input
              v-model="chatInput"
              placeholder="输入消息，Enter 发送"
              @keyup.enter="sendChat"
            />
            <button @click="sendChat">发送</button>
          </div>
        </div>
      </div>
    </div>

    <footer class="meeting-footer">
      <el-button :type="micOpen ? 'primary' : 'info'" @click="toggleMic">
        {{ micOpen ? "麦克风开" : "麦克风关" }}
      </el-button>
      <el-button :type="cameraOpen ? 'primary' : 'info'" @click="toggleCamera">
        {{ cameraOpen ? "摄像头开" : "摄像头关" }}
      </el-button>
      <el-button @click="togglePanel('members')">参会人</el-button>
      <el-button @click="togglePanel('chat')">聊天</el-button>
      <el-button type="danger" @click="leave">离开会议</el-button>
    </footer>
  </div>
</template>

<style scoped>
.meeting-wrap {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.meeting-header {
  padding: 10px 16px;
  background: #2a2f38;
  display: flex;
  align-items: center;
  gap: 16px;
}
.meeting-header .title {
  font-weight: 600;
}
.meeting-header .meta {
  color: #909399;
  font-size: 13px;
}
.meeting-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.video-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 8px;
  padding: 8px;
  overflow: auto;
}
.video-cell {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 4 / 3;
}
.video-cell video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.video-cell .name {
  position: absolute;
  bottom: 6px;
  left: 8px;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.5);
  padding: 2px 8px;
  border-radius: 4px;
}
.host {
  color: #f56c6c;
  margin-left: 4px;
}
.off {
  color: #909399;
  margin-left: 4px;
}
.side-panel {
  width: 280px;
  background: #2a2f38;
  border-left: 1px solid #3a3f48;
  display: flex;
  flex-direction: column;
}
.panel-tabs {
  display: flex;
  border-bottom: 1px solid #3a3f48;
}
.panel-tabs .tab {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  cursor: pointer;
  font-size: 13px;
  color: #909399;
}
.panel-tabs .tab.active {
  color: #409eff;
  border-bottom: 2px solid #409eff;
}
.panel-content {
  flex: 1;
  overflow: auto;
  padding: 8px;
}
.member-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 4px;
  border-bottom: 1px solid #333;
}
.member-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.member-item .dot.online {
  background: #67c23a;
}
.member-item .dot.off {
  background: #909399;
}
.member-item .dot.self {
  background: #409eff;
}
.member-item .nick {
  font-size: 13px;
}
.member-item .host-tag {
  font-size: 11px;
  color: #f56c6c;
  margin-left: auto;
}
.chat-panel {
  display: flex;
  flex-direction: column;
}
.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}
.chat-msg {
  margin-bottom: 8px;
}
.chat-msg.me {
  text-align: right;
}
.chat-msg.me .chat-nick {
  color: #409eff;
}
.chat-nick {
  font-size: 11px;
  color: #909399;
  margin-bottom: 2px;
}
.chat-text {
  display: inline-block;
  font-size: 13px;
  background: #3a3f48;
  padding: 6px 10px;
  border-radius: 6px;
  max-width: 85%;
  word-break: break-word;
}
.chat-msg.me .chat-text {
  background: #409eff;
  color: #fff;
}
.chat-empty {
  text-align: center;
  color: #606266;
  font-size: 13px;
  padding: 20px;
}
.chat-input {
  display: flex;
  gap: 4px;
  padding: 8px;
  border-top: 1px solid #3a3f48;
}
.chat-input input {
  flex: 1;
  background: #1f2329;
  border: 1px solid #3a3f48;
  color: #e5eaf0;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 13px;
}
.chat-input input::placeholder {
  color: #606266;
}
.chat-input button {
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 6px 14px;
  cursor: pointer;
  font-size: 13px;
}
.meeting-footer {
  padding: 12px 16px;
  background: #2a2f38;
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
