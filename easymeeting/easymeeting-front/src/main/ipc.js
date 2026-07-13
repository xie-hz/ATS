import { saveWindow, getWindow, delWindow } from './windowProxy'
import { app, shell, BrowserWindow, ipcMain, dialog, desktopCapturer } from 'electron'
import icon from '../../resources/icon.png?asset'
import { join } from 'path'
import { is } from '@electron-toolkit/utils'
import store from "./store"
import { initWs, sendWsData, logout } from "./wsClient";
import { getSysSetting, saveSysSetting } from "./sysSetting"
const fs = require('fs');
const path = require('path');

const FormData = require('form-data'); // 引入FormData模块（用于构建表单数据）
const axios = require('axios'); // 引入axios库

import {
    startRecording,
    stopRecording
} from "./recording"

import {
    downloadUpdate
} from "./appUpdate"

const openWindow = ({ windowId, title = "详情", path, width = 960, height = 720, data, maximizable }) => {
    let newWindow = getWindow(windowId);
    const paramsArray = [];
    if (data && Object.keys(data).length > 0) {
        path = path.endsWith("?") ? path : path + "?";
        for (let i in data) {
            paramsArray.push(`${i}=${encodeURIComponent(data[i])}`)
        }
        path = path + paramsArray.join("&");
    }
    if (!newWindow) {
        newWindow = new BrowserWindow({
            width,
            height,
            minHeight: height,
            minWidth: width,
            show: false,
            autoHideMenuBar: true,
            frame: false,
            //transparent: true,
            fullscreenable: false,
            maximizable,
            resizable: maximizable,
            ...(process.platform === 'linux' ? { icon } : {}),
            webPreferences: {
                preload: join(__dirname, '../preload/index.js'),
                sandbox: false,
            }
        })
        //保存窗口
        saveWindow(windowId, newWindow);

        if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
            // newWindow.loadURL(process.env['ELECTRON_RENDERER_URL'] + "#" + path)
            newWindow.loadURL(`${process.env['ELECTRON_RENDERER_URL']}/index.html#${path}`);
        } else {
            newWindow.loadFile(join(__dirname, `../renderer/index.html`), { hash: `${path}` });
        }
        //打开调试窗口
        // if (NODE_ENV === 'development') {
        //     newWindow.webContents.openDevTools();
        // }

        newWindow.on('ready-to-show', () => {
            newWindow.setTitle(title);
            newWindow.show()
        })

        newWindow.on("close", (event) => {
            if (newWindow.forceClose !== undefined && !newWindow.forceClose) {
                preCloseWindow(windowId);
                event.preventDefault()
            }
        })

        newWindow.on('closed', () => {
            closeWindow(windowId);
            delWindow(windowId);
        })

        newWindow.on('maximize', (e) => {
            newWindow.webContents.send("winIsMax", true);
        });
        newWindow.on('unmaximize', (e) => {
            newWindow.webContents.send("winIsMax", false);
        });

    } else {
        if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
            // newWindow.loadURL(process.env['ELECTRON_RENDERER_URL'] + "#" + path)
            newWindow.loadURL(`${process.env['ELECTRON_RENDERER_URL']}/index.html#${path}`);
        } else {
            newWindow.loadFile(join(__dirname, `../renderer/index.html`), { hash: `${path}` });
        }
        newWindow.show();
        newWindow.setSkipTaskbar(false)
    }
}

const onWinTitleOp = () => {
    ipcMain.on("winTitleOp", (e, { action, data }) => {
        const webContents = e.sender
        const win = BrowserWindow.fromWebContents(webContents)
        switch (action) {
            case "close": {
                if (data.closeType == 0) {
                    win.forceClose = data.forceClose;
                    win.close();
                } else {
                    win.setSkipTaskbar(true) // 使窗口不显示在任务栏中
                    win.hide()
                }
                break;
            }
            case "minimize": {
                win.minimize();
                break;
            }
            case "maximize": {
                win.maximize();
                break;
            }
            case "unmaximize": {
                win.unmaximize();
                break;
            }
            case "top": {
                win.setAlwaysOnTop(data.top);
            }
        };
    });
}

const onOpenWindow = () => {
    ipcMain.on("openWindow", (e, { title, windowId, path, width, height, data, maximizable = true }) => {
        openWindow({
            title,
            windowId,
            path,
            width,
            height,
            data,
            maximizable
        })
    })
}

const closeWindow = (windowId) => {
    const mainWindow = getWindow("main");
    if (mainWindow) {
        mainWindow.webContents.send('closeWindow', { windowId });
    }
}

const preCloseWindow = (windowId) => {
    const win = getWindow(windowId);
    if (win) {
        win.webContents.send('preCloseWindow');
    }

}

const onGetScreenSource = () => {
    ipcMain.handle('getScreenSource', async (event, opts) => {
        // Linux 上 desktopCapturer 走 PipeWire/portal，用户取消或 portal 不可用时会 reject。
        // 用 try/catch 兜住，返回空数组，避免未捕获异常导致客户端崩溃退出。
        try {
            const sources = await desktopCapturer.getSources(opts);
            return sources.filter(source => {
                const size = source.thumbnail.getSize()
                return size.width > 10 && size.height > 10 // 排除空缩略图
            }).map(source => ({
                id: source.id,
                name: source.name,
                displayId: source.display_id,
                thumbnail: source.thumbnail.toDataURL()
            }))
        } catch (e) {
            console.error('getScreenSource 失败:', e && e.message)
            return []
        }
    })
}

const onLoginOrRegister = () => {
    ipcMain.handle("loginOrRegister", (e, isLogin) => {
        const login_width = 375;
        const login_height = 365;
        const register_height = 485;
        const mainWindow = getWindow("main");
        mainWindow.setResizable(true)
        mainWindow.setMinimumSize(login_width, login_height);
        if (isLogin) {
            mainWindow.setSize(login_width, login_height);
        } else {
            mainWindow.setSize(login_width, register_height);
        }
        mainWindow.setResizable(false)
    })
}

const onLoginSuccess = () => {
    ipcMain.handle("loginSuccess", (e, { userInfo, wsUrl }) => {
        const mainWindow = getWindow("main");
        mainWindow.setResizable(true);
        mainWindow.setMinimumSize(720, 480);
        mainWindow.setSize(720, 480);
        mainWindow.setResizable(false);
        store.initUserId(userInfo.userId);
        store.setData("userInfo", userInfo);
        initWs(wsUrl + userInfo.token)
    })
}

const onSelectFile = () => {
    ipcMain.handle('selectFile', async () => {
        const { canceled, filePaths } = await dialog.showOpenDialog(BrowserWindow.getFocusedWindow(), {
            title: "选择文件",
            properties: ['openFile']
        });
        if (canceled) {
            return {};
        }
        const filePath = filePaths[0]
        const { size } = await fs.promises.stat(filePath);
        return {
            fileName: path.basename(filePath),       // 文件名（带扩展名）
            fileSize: size,
            filePath
        }
    });
}

const onSendPeerConnection = () => {
    ipcMain.on("sendPeerConnection", (e, peerData) => {
        peerData.token = store.getData("userInfo")?.token;
        sendWsData(JSON.stringify(peerData));
    })
}

const onUploadChatFile = () => {
    ipcMain.on("uploadChatFile", (e, { uploadUrl, messageId, sendTime, filePath }) => {

        console.log(uploadUrl, messageId, sendTime, filePath)
        // 创建FormData对象，并添加图片文件到其中
        const meetingWin = getWindow("meeting");
        const formData = new FormData();
        formData.append("messageId", messageId);
        formData.append("sendTime", sendTime);
        formData.append('file', fs.createReadStream(filePath));
        // 设置POST请求参数
        const token = store.getData("userInfo")?.token;
        // 发送POST请求
        axios.post(uploadUrl, formData, {
            headers: { 'Content-Type': 'multipart/form-data', "token": token },
            onUploadProgress: (progressEvent) => {
                if (progressEvent.total) {
                    const percent = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    if (meetingWin) {
                        meetingWin.webContents.send('uploadProgress', { messageId, percent });
                    }
                }
            }
        }).catch((error) => {
            console.error('文件上传成功失败', error);
        });
    })
}

const onDownload = () => {
    ipcMain.handle('download', async (event, { fileName, messageId, url, sendTime }) => {
        const { filePath } = await dialog.showSaveDialog(BrowserWindow.getFocusedWindow(), {
            title: "保存文件",
            defaultPath: path.join(app.getPath('downloads'), fileName),
            properties: ['createDirectory']
        });
        if (!filePath) {
            return;
        }
        const suffix = fileName.substring(fileName.lastIndexOf("."));
        downloadFile(messageId, sendTime, suffix, url, filePath);
        return filePath;
    });
}

const downloadFile = (messageId, sendTime, suffix, url, savePath) => {
    const meetingWin = getWindow("meeting");
    return new Promise(async (resolve, reject) => {
        let response = await axios({
            method: 'post',
            url: url, // 后端接口地址
            responseType: 'stream', // 必须声明响应类型为二进制数据
            data: {
                messageId,
                sendTime,
                suffix,
                token: store.getData("userInfo")?.token
            },
            headers: { 'Content-Type': 'multipart/form-data' },
            onDownloadProgress: (progressEvent) => {
                // 计算下载进度百分比
                if (progressEvent.total) {
                    const percent = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    if (meetingWin) {
                        meetingWin.webContents.send('downloadProgress', { messageId, percent, localFilePath: savePath });
                    }
                }
            },
        })

        if (response.headers["content-type"] == "application/json") {
            //返回json 就是下载失败
        } else {
            const stream = fs.createWriteStream(savePath);
            response.data.pipe(stream);
            stream.on('finish', () => {
                stream.close();
                resolve();
            });
        }
    });
}

const onOpenLocalFile = () => {
    ipcMain.on("openLocalFile", (e, { localFilePath, folder = false }) => {
        if (folder) {
            shell.openPath(localFilePath)
        } else {
            shell.showItemInFolder(localFilePath);
        }

    })
}

const onStartRecording = () => {
    ipcMain.handle("startRecording", (e, { displayId, mic }) => {
        const sender = e.sender;
        startRecording(sender, displayId, mic);
    })
}

const onStopRecording = () => {
    ipcMain.handle("stopRecording", (e) => {
        stopRecording();
    })
}


const onSaveSysSetting = () => {
    ipcMain.handle("saveSysSetting", (e, sysSetting) => {
        saveSysSetting(sysSetting);
    })
}

const onGetSysSetting = () => {
    ipcMain.handle("getSysSetting", (e) => {
        return getSysSetting();
    })
}

const onChangeLocalFolder = () => {
    ipcMain.handle("changeLocalFolder", async (e, { localFilePath }) => {
        console.log(localFilePath);
        // 显示保存文件的对话框
        const options = {
            properties: ['openDirectory'],
            defaultPath: localFilePath
        }
        let result = await dialog.showOpenDialog(options);
        if (result.canceled) {
            return;
        }
        return result.filePaths[0].replaceAll("//", "\\");
    })
}

const onLogout = () => {
    ipcMain.handle("logout", async (e) => {
        logout();
    })
}

const onWindowCommunication = () => {
    ipcMain.on("windowCommunication", (e, { windowId, data }) => {
        const window = getWindow(windowId);
        if (window) {
            window.webContents.send('windowCommunication', data);
        }
    })
}

//打开链接
const onOpenUrl = () => {
    ipcMain.on("openUrl", async (e, { url }) => {
        shell.openExternal(url)
    });
}

//下载更新
const onDownloadUpdate = () => {
    ipcMain.on("downloadUpdate", async (e, { downloadUrl, id, fileName }) => {
        downloadUpdate({ downloadUrl, id, fileName });
    });
}

export {
    onWinTitleOp,
    onOpenWindow,
    onGetScreenSource,
    onLoginOrRegister,
    onLoginSuccess,
    onSelectFile,
    onSendPeerConnection,
    onUploadChatFile,
    onDownload,
    onOpenLocalFile,
    onStartRecording,
    onStopRecording,
    onSaveSysSetting,
    onGetSysSetting,
    onChangeLocalFolder,
    onLogout,
    onWindowCommunication,
    onOpenUrl,
    onDownloadUpdate
}