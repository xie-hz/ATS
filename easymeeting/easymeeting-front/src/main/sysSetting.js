
const os = require('os');
const userDir = os.homedir();
const fs = require('fs')
import store from "./store"

const localFolder = userDir.replaceAll("\\", "/") + "/.easymeeting/";
if (!fs.existsSync(localFolder)) {
    fs.mkdirSync(localFolder);
}

const getSysSetting = () => {
    const userId = store.getUserId();
    const configFile = localFolder + userId;
    if (!fs.existsSync(configFile)) {
        return {
            openCamera: true,
            openMic: true,
            screencapFolder: localFolder
        }
    } else {
        return JSON.parse(fs.readFileSync(configFile, 'utf8'));
    }
}

const saveSysSetting = (sysSetting) => {
    const userId = store.getUserId();
    const configFile = localFolder + userId;
    fs.writeFileSync(configFile, sysSetting, 'utf8');
}

export {
    getSysSetting,
    saveSysSetting
}