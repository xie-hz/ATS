const fs = require('fs');
const axios = require('axios'); // 引入axios库
import store from "./store"
const os = require('os');
const userDir = os.homedir();
import { getWindow } from './windowProxy'
const { exec } = require("child_process");

const downloadUpdate = async ({ downloadUrl, id, fileName }) => {
    const token = store.getData("userInfo")?.token;
    const config = {
        responseType: 'stream',
        headers: {
            'Content-Type': 'multipart/form-data',
            "token": token
        },
        onDownloadProgress(progress) {
            const loaded = progress.loaded
            const mainWindow = getWindow("main");
            if (!mainWindow) {
                return;
            }
            mainWindow.webContents.send("updateDownloadCallback", loaded);
        }
    }
    // 发送POST请求
    const response = await axios.post(downloadUrl, { id }, config);
    const localFile = userDir + "/" + fileName
    const stream = fs.createWriteStream(localFile);
    response.data.pipe(stream);
    stream.on('finish', async () => {
        stream.close();
        //开始安装
        const command = `${localFile}`
        execCommand(command);
    });
}

const execCommand = (command) => {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            resolve(stdout);
        });
    })
}

export {
    downloadUpdate
}