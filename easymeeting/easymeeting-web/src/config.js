// ICE servers config. STUN by default; TURN (coturn) added when VITE_TURN_URL
// is set at build time (Phase 4 production). Format: turn:user:pass@host:port
const stunUrl = import.meta.env.VITE_STUN_URL || "stun:stun.l.google.com:19302"
const turnUrl = import.meta.env.VITE_TURN_URL || "" // e.g. turn: user:pass@coturn:3478

export const iceServers = (() => {
  const list = [{ urls: stunUrl }]
  if (turnUrl) {
    // turn:user:pass@host:port -> { urls, username, credential }
    const m = turnUrl.match(/^turn:([^:]+):([^@]+)@(.+)$/)
    if (m) {
      list.push({ urls: `turn:${m[3]}`, username: m[1], credential: m[2] })
    } else {
      list.push({ urls: turnUrl })
    }
  }
  return list
})()
