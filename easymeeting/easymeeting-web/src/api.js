// EasyMeeting HTTP API client. The EasyMeeting backend reads params from form/
// query bodies and the auth token from the `token` header (see ABaseController).

const BASE = "/api"

let token = null
export function setToken(t) {
  token = t
}
export function getToken() {
  return token
}

async function post(path, params = {}) {
  const body = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) body.append(k, v)
  }
  const headers = { "Content-Type": "application/x-www-form-urlencoded" }
  if (token) headers["token"] = token
  const resp = await fetch(BASE + path, { method: "POST", headers, body })
  const data = await resp.json()
  if (data.status !== "success") {
    throw new Error(data.info || "请求失败")
  }
  return data.data
}

// 访客入会：会议号 + 密码 + 昵称 -> 临时 GUEST token + 会议信息
export const guestJoin = (meetingNo, password, nickName) =>
  post("/meeting/guestJoin", { meetingNo, password, nickName })

// 正式加入会议（建 WebRTC 通道前调用）
export const joinMeeting = (videoOpen) =>
  post("/meeting/joinMeeting", { videoOpen })

// 退出会议
export const exitMeeting = () => post("/meeting/exitMeeting")

// 通知视频开关变更
export const sendVideoChange = (openVideo) =>
  post("/meeting/sendOpenVideoChangeMessage", { openVideo })

// 发送聊天消息（receiveUserId='0' 为全员，messageType 5=文本）
export const sendMessage = (message, receiveUserId = "0", messageType = 5) =>
  post("/chat/sendMessage", { message, messageType, receiveUserId })

// 加载当前会议的聊天消息（倒序分页）
export const loadMessage = (maxMessageId = 0, pageNo = 1) =>
  post("/chat/loadMessage", { maxMessageId, pageNo })
