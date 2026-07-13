//获取环境信息
export const getEvn = () => {
    new Promise(async (resolve, reject) => {
        //检查麦克风
        const devices = await navigator.mediaDevices.enumerateDevices()
        const defaultMic = devices.find(
            (device) => device.kind === 'audioinput' && device.deviceId === 'default'
        )
        const defaultCamera = devices.find((device) => device.kind === 'videoinput')
        //获取系统设置
        const sysSetting = await window.electron.ipcRenderer.invoke('getSysSetting')
        resolve({
            micEnable: defaultMic != null,
            camera: defaultCamera != null,
            micOpen: sysSetting.micOpen,
            cameraOpen: sysSetting.cameraOpen,
        })
    })
}