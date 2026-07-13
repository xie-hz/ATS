// Browser WebSocket signaling client. Mirrors the Electron main-process
// wsClient.js but runs in-page (no IPC). Uses the same protocol as the Netty
// backend: connect /ws?token=xxx, heartbeat "ping", JSON MessageSendDto frames.

import { getToken } from "./api"

const HEART_INTERVAL = 5000
const MAX_RETRIES = 5
let ws = null
let heartTimer = null
let myUserId = null
let handlers = {}
let intentionalClose = false
let retryCount = 0
let firstOpenResolve = null

export function connectSignaling({ userId, onJoin, onPeer, onExit, onFinish, onVideoChange, onChat, onReconnect, onClose }) {
  myUserId = userId
  handlers = { onJoin, onPeer, onExit, onFinish, onVideoChange, onChat, onReconnect, onClose }
  intentionalClose = false
  retryCount = 0
  // 返回首次连接成功的 Promise，调用方应 await 后再 joinMeeting，
  // 确保后端 channel 已注册、能收到 ADD_MEETING_ROOM 成员广播。
  return new Promise((resolve) => {
    firstOpenResolve = resolve
    open(false)
  })
}

function open(isReconnect) {
  const token = getToken()
  const proto = location.protocol === "https:" ? "wss:" : "ws:"
  // 重连时带 reconnect=true，后端从临时缓存恢复 token（removeContext 会清除正式 token）
  const reconnectParam = isReconnect ? "&reconnect=true" : ""
  ws = new WebSocket(`${proto}//${location.host}/ws?token=${encodeURIComponent(token)}${reconnectParam}`)

  ws.onopen = () => {
    retryCount = 0
    heartTimer = setInterval(() => ws.readyState === WebSocket.OPEN && ws.send("ping"), HEART_INTERVAL)
    if (firstOpenResolve) {
      firstOpenResolve()
      firstOpenResolve = null
    }
    // 重连成功后通知上层重新 joinMeeting（恢复 Redis 房间成员状态）
    if (isReconnect && handlers.onReconnect) {
      handlers.onReconnect()
    }
  }
  ws.onmessage = (ev) => {
    if (ev.data === "pong" || ev.data === "heart") return
    let msg
    try {
      msg = JSON.parse(ev.data)
    } catch {
      return
    }
    route(msg)
  }
  ws.onclose = () => {
    clearInterval(heartTimer)
    if (intentionalClose) {
      handlers.onClose && handlers.onClose()
      return
    }
    // 断线重连（指数退避）
    if (retryCount < MAX_RETRIES) {
      retryCount += 1
      const delay = Math.min(2000 * 1.5 ** (retryCount - 1), 15000)
      setTimeout(() => open(true), delay)
    } else {
      handlers.onClose && handlers.onClose()
    }
  }
  ws.onerror = () => {
    // 错误后 onclose 会触发重连
  }
}

// Normalize messageContent: backend sometimes sends an object, sometimes a JSON string.
function content(msg) {
  const c = msg.messageContent
  if (typeof c === "string") {
    try {
      return JSON.parse(c)
    } catch {
      return c
    }
  }
  return c
}

function route(msg) {
  switch (msg.messageType) {
    case 1: // ADD_MEETING_ROOM
      handlers.onJoin && handlers.onJoin(content(msg))
      break
    case 2: // PEER (WebRTC signaling)
      handlers.onPeer && handlers.onPeer(msg.sendUserId, content(msg))
      break
    case 3: // EXIT_MEETING_ROOM
      handlers.onExit && handlers.onExit(content(msg))
      break
    case 4: // FINIS_MEETING
      handlers.onFinish && handlers.onFinish()
      break
    case 5: // CHAT_TEXT_MESSAGE
    case 6: // CHAT_MEDIA_MESSAGE
    case 7: // CHAT_MEDIA_MESSAGE_UPDATE
      handlers.onChat && handlers.onChat(msg)
      break
    case 11: // MEETING_USER_VIDEO_CHANGE
      handlers.onVideoChange && handlers.onVideoChange(msg.sendUserId, content(msg))
      break
    default:
      break
  }
}

// Send a WebRTC signal (offer/answer/candidate) to a peer via the backend.
export function sendPeer(receiveUserId, signalType, signalData) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return
  const payload = {
    token: getToken(),
    sendUserId: myUserId,
    receiveUserId,
    signalType,
    signalData: typeof signalData === "string" ? signalData : JSON.stringify(signalData),
  }
  ws.send(JSON.stringify(payload))
}

export function closeSignaling() {
  intentionalClose = true
  clearInterval(heartTimer)
  if (ws) {
    ws.onclose = null
    ws.close()
    ws = null
  }
}
