# EasyMeeting Web 客户端

浏览器端视频会议客户端，供候选人与面试官无需安装客户端、凭会议号+密码直接入会。复用 Electron 客户端的 WebRTC Mesh 信令协议，与 Electron 端进入同一会议互通。

## 开发

```bash
cd easymeeting-web
npm install
npm run dev        # 启动在 http://localhost:5174
```

开发时 vite 代理：
- `/api` -> `http://localhost:6060`（EasyMeeting HTTP）
- `/ws`  -> `ws://localhost:6061`（EasyMeeting Netty WebSocket）

需先启动 EasyMeeting 后端（6060/6061）。

## 构建

```bash
npm run build      # 产物 dist/
```

生产部署：把 `dist/` 放到任意静态服务器或反代后，反向代理需把：
- `/api/*` -> EasyMeeting HTTP（6060）
- `/ws`    -> EasyMeeting WS（6061，支持 wss 升级）

## 环境变量（构建时）

在 `.env` 或构建环境设置：

| 变量 | 默认 | 说明 |
|---|---|---|
| `VITE_STUN_URL` | `stun:stun.l.google.com:19302` | STUN 服务器 |
| `VITE_TURN_URL` | 空 | TURN 服务器，格式 `turn:user:pass@host:port`，部署 coturn 后填 |

生产环境（复杂 NAT）必须配 `VITE_TURN_URL`，否则候选人与面试官在不同网络可能连不上。

## 入会流程（访客模式）

1. 打开 Web 页面 -> 输入会议号 + 密码 + 昵称
2. 调 `POST /api/meeting/guestJoin` -> 后端校验会议、签发临时 GUEST token，返回 `{token, userId, meetingId, meetingNo}`
3. 浏览器用 token 连 `ws://host/ws?token=xxx`
4. `POST /api/meeting/joinMeeting` 正式入会 -> 后端广播加入，前端与已在成员逐对建 RTCPeerConnection（Mesh）
5. SDP offer/answer、ICE candidate 经 WS 信令中转，建立音视频

## 与 Electron 互通

两端使用同一套 WS 信令协议（`PeerConnectionDataDto` / `MessageSendDto` / messageType 1-12），进入同一会议房间即可互相通信。

## 当前实现范围（Phase 1）

- ✅ 访客会议号密码登录
- ✅ WebRTC Mesh 音视频（摄像头/麦克风开关）
- ✅ 成员进出、信令断线重连
- ✅ STUN/TURN 可配置
- ⏳ 聊天（后续）
- ⏳ 屏幕共享（getDisplayMedia，后续）
- ⏳ 录制（继续用 Electron）
