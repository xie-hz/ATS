import WebSocket from "ws"
import { getWindow, getWindowManage } from "./windowProxy"
let ws = null;
const maxRetries = 5;
const retryInterval = 2000;
let retryCount = 0;
const HEARTBEAT_INTERVAL = 5000;
let heartBeatTimer = null
let wsUrl = null;
let needReconnect = null;

const initWs = (_wsUrl) => {
    wsUrl = _wsUrl
    needReconnect = true;
    connectWs(false);
}

const wsCheck = () => {
    return import.meta.env.VITE_WS_CHECK === "true";
}

const connectWs = (reconnect) => {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
        console.log("已经连接上");
        return;
    }
    console.log(`尝试链接.....(重试次数：${retryCount}/${maxRetries},连接地址:${wsUrl})`);
    ws = new WebSocket(wsUrl + "&reconnect=" + reconnect);
    ws.onopen = () => {
        if (retryCount > 0 && wsCheck) {
            const mainWindow = getWindow("main");
            mainWindow.webContents.send("reconnect", true);
        }
        retryCount = 0
        console.log('websocket连接成功');
        startHeartBeat();
    }
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("收到ws消息", data);
        const meetingWin = getWindow("meeting");
        const mainWin = getWindow("main");
        switch (data.messageType) {
            case 1://加入房间
            case 2://发送peer
            case 3://退出房间
                if (mainWin && (data.messageType == 1 || data.messageType == 3)) {
                    mainWin.webContents.send("mainMessage", data);
                }
                if (meetingWin) {
                    meetingWin.webContents.send("meetingMessage", data);
                }
                break;
            case 4://结束会议
                if (mainWin) {
                    mainWin.webContents.send("mainMessage", data);
                }
                if (meetingWin) {
                    meetingWin.webContents.send("meetingMessage", data);
                }
                break;
            case 5://聊天 文本消息
            case 6:// 媒体消息
            case 7://媒体消息更新
                if (!meetingWin) {
                    return;
                }
                meetingWin.webContents.send("chatMessage", data);
                break;
            case 8://好友申请消息
            case 12://处理好友申请
            case 9://邀请入会
            case 10://被强制退出
                if (!mainWin) {
                    return;
                }
                mainWin.webContents.send("mainMessage", data);
                break;
            case 11://用户开启关闭视频
                if (!meetingWin) {
                    return;
                }
                meetingWin.webContents.send("meetingMessage", data);
                break;
        }
    }
    ws.onerror = () => {
        ws.close();
    }
    ws.onclose = () => {
        clearHeartbeatTimers();
        handleReconnect();
    }
}
const handleReconnect = () => {
    if (!needReconnect) {
        return;
    }
    if (retryCount >= maxRetries) {
        console.error("已经到达最大重试次数，停止重试");
        retryCount = 0;
        if (wsCheck) {
            logout(false);
        }
        return;
    }
    retryCount += 1;
    const delay = retryInterval * Math.pow(1.5, retryCount - 1);
    console.log(`连接断开,等待${delay / 1000}秒后重试`);
    if (wsCheck()) {
        const mainWindow = getWindow("main");
        mainWindow.webContents.send("reconnect", false);
    }
    setTimeout(() => {
        connectWs(true);
    }, delay);
}
const startHeartBeat = () => {
    heartBeatTimer = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send("ping");
        }
    }, HEARTBEAT_INTERVAL);
}

const clearHeartbeatTimers = () => {
    clearInterval(heartBeatTimer);
    heartBeatTimer = null;
}

const logout = (closeWs = true) => {
    const login_width = 375;
    const login_height = 365;
    const mainWindow = getWindow("main");
    mainWindow.setResizable(true);
    mainWindow.setMinimumSize(login_width, login_height);
    mainWindow.setSize(login_width, login_height);
    mainWindow.setResizable(false);
    if (closeWs) {
        needReconnect = false;
        ws.close();
    }
    const windows = getWindowManage();
    for (let winKey in windows) {
        const win = windows[winKey];
        if (winKey != "main") {
            win.close();
        }
    }
    mainWindow.webContents.send("logout");
}

const sendWsData = (data) => {
    if (!ws) {
        return;
    }
    ws.send(data);
}

export {
    initWs,
    logout,
    sendWsData,
}