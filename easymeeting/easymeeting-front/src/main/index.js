import { app, shell, BrowserWindow, ipcMain, Menu, Tray, session } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
const NODE_ENV = process.env.NODE_ENV
// Linux 开发环境禁用 chrome-sandbox（避免 SUID 配置要求），生产构建可改用 chmod 4755
if (process.platform === 'linux') {
  app.commandLine.appendSwitch('no-sandbox')
}
import { saveWindow } from './windowProxy'
import {
  onLoginOrRegister,
  onWinTitleOp,
  onOpenWindow,
  onLoginSuccess,
  onGetScreenSource,
  onSelectFile,
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
  onDownloadUpdate,
  onSendPeerConnection
} from "./ipc"
import store from "./store"

function createWindow() {
  const mainWindow = new BrowserWindow({
    //宽度 1200(页面宽度)+80(左边菜单)+2(边框)+8(滚动条)+20(左右边距)
    width: 375,
    height: 365,
    show: false,
    autoHideMenuBar: true,
    resizable: true,
    frame: false,// 移除默认窗口边框
    transparent: false,//透明背景
    maximizable: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
    }
  })
  saveWindow("main", mainWindow);

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }

  //监听窗口大小变化
  mainWindow.on('maximize', (e) => {
    mainWindow.webContents.send("winIsMax", true);
  });
  mainWindow.on('unmaximize', (e) => {
    mainWindow.webContents.send("winIsMax", false);
  });

  mainWindow.on('close', (event) => {
    const userId = store.getUserId()
    if (userId == null || isQuit) {
      return;
    }
    event.preventDefault() // 阻止默认关闭行为
    mainWindow.hide() // 隐藏窗口
  })

  //托盘
  const tray = new Tray(icon)
  const contextMenu = [
    {
      label: '退出', click: function () {
        app.quit()
      }
    }
  ];

  const menu = Menu.buildFromTemplate(contextMenu)
  tray.setToolTip('EasyMeeting')
  tray.setContextMenu(menu)
  // 点击托盘图标，显示主窗口
  tray.on("click", () => {
    mainWindow.setSkipTaskbar(false)
    mainWindow.show();
  })
}


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

//是否退出
let isQuit = false;
//缓存是否清理
let isCleaned = false;
const clearStorage = async () => {
  try {
    await session.defaultSession.clearStorageData({
      storages: ['localstorage']
    })
    isCleaned = true;
    console.log('localStorage 已清除')
  } catch (error) {
    console.error('清除存储失败:', error)
  }
}

app.on('before-quit', async (event) => {
  isQuit = true;
  if (!isCleaned) {
    // 阻止立即退出
    event.preventDefault()
    // 清除存储
    await clearStorage()
    // 关闭所有窗口（触发渲染进程清理）
    BrowserWindow.getAllWindows().forEach(win => {
      if (!win.isDestroyed()) {
        win.close()
      }
    })
    // 确保所有窗口关闭后退出
    app.quit()
  }
})

app.whenReady().then(() => {
  electronApp.setAppUserModelId('com.electron')
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })
  createWindow()
  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })

  onWinTitleOp();

  //登录注册
  onLoginOrRegister();

  //登录成功
  onLoginSuccess();

  //发送peerconnecton
  onSendPeerConnection();

  onOpenWindow();

  //获取屏幕资源
  onGetScreenSource();

  onSelectFile();

  onUploadChatFile();

  onDownload();

  onOpenLocalFile();

  onStartRecording();

  onStopRecording();

  onSaveSysSetting();

  onGetSysSetting();

  onChangeLocalFolder();

  onLogout();

  onWindowCommunication();

  onOpenUrl();

  onDownloadUpdate();
})
