
const fs = require('fs')

const { spawn, exec } = require('child_process')
const NODE_ENV = process.env.NODE_ENV
const path = require('path')
const { app, screen } = require('electron')

import { getSysSetting } from "./sysSetting"

const ffmpegPath = "/assets/ffmpeg.exe"


const getResourcesPath = () => {
    let resourcesPath = app.getAppPath();
    if (NODE_ENV !== 'development') {
        resourcesPath = path.dirname(app.getPath('exe')) + "/resources";
    }
    return resourcesPath;
}

const getFFmpegPath = () => {
    return path.join(getResourcesPath(), ffmpegPath);
}

let ffmpegProcess = null
let currentTime = 0;
let sender = null;
const startRecording = (_sender, displayId, mic) => {
    sender = _sender
    currentTime = 0;
    let filePath = getSysSetting().screencapFolder;
    filePath = filePath + new Date().getTime() + "_temp.mp4";



    // 参数	值/选项	描述
    // -f gdigrab	gdigrab	指定使用 Windows GDI 屏幕捕获设备
    // -draw_mouse	1	捕获时包含鼠标指针（1=显示，0=隐藏）
    // -framerate	30	设置视频捕获帧率为 30 FPS
    // -offset_x	0	屏幕捕获起始水平偏移（左上角 X 坐标）
    // -offset_y	0	屏幕捕获起始垂直偏移（左上角 Y 坐标）
    // -video_size	1920x1080	设置捕获区域分辨率为 1080p
    // -i	desktop	输入源为整个桌面（可替换为 title=窗口标题 捕获特定窗口）
    // -f dshow	dshow	指定使用 DirectShow 音频设备
    // -i	audio="Microphone (USB_MIC)"	指定麦克风设备名称（需与实际设备名匹配）
    // -c:v	libx264	使用 H.264 编码器压缩视频
    // -preset	ultrafast	编码速度预设（牺牲压缩率换取速度）
    // -crf	18	视频质量系数（0-51，值越小质量越高）
    // -c:a	aac	使用 AAC 编码器压缩音频
    // -b:a	192k	设置音频比特率为 192 kbps
    // -pix_fmt	yuv420p	指定像素格式（确保广泛兼容性）
    // 输出路径	"c:/output.mp4"	输出文件路径（MP4 容器格式）
    // -y	(无值)	自动覆盖已存在的输出文件

    const { bounds, workArea } = getScreenInfo(displayId);
    const ffmpeg = getFFmpegPath();
    let args = [
        // 视频输入
        '-f', 'gdigrab',
        '-draw_mouse', '1',
        '-framerate', '30',
        '-offset_x', `${bounds.x}`,
        '-offset_y', '0',
        '-video_size', `${workArea.width}x${workArea.height}`,
        '-i', 'desktop',
    ]
    if (mic) {
        args = args.concat(['-f', 'dshow', '-i', `audio=${mic}`])
    }
    const otherArgs = [
        // 视频编码
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '18',
        '-g', '60',                   // 每2秒一个关键帧
        '-x264-params', 'nal-hrd=cbr:force-cfr=1', // 恒定帧率
        // 音频编码
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',
        '-ac', '2',                   // 立体声
        // 像素格式
        '-pix_fmt', 'yuv420p',
        // 防损坏关键参数 - 修复 moov atom 问题
        '-movflags', 'frag_keyframe+empty_moov+faststart',
        '-flush_packets', '1',
        '-fflags', '+genpts',
        '-max_interleave_delta', '0', // 减少交错延迟
        filePath
    ]
    args = args.concat(otherArgs)
    // console.log(args.join(" "));
    ffmpegProcess = spawn(ffmpeg, args, {
        stdio: ['ignore', 'pipe', 'pipe'], // 捕获 stdout 和 stderr
        detached: true // 创建独立进程组
    })
    //会将日志输出到stderr（标准错误流），而stdout（标准输出流）
    // 可能用于传输数据（例如当输出格式为流时）。在屏幕录制场景中，我们通常只关心stderr的内容，
    // 因为它包含了编码进度、警告和错误信息。
    ffmpegProcess.stderr.on('data', (data) => {
        const output = data.toString();
        const timeMatch = output.match(/time=(\S+)/);
        if (timeMatch && timeMatch[1]) {
            const seconds = parseTime(timeMatch[1])
            if (seconds > currentTime) {
                sender.send("recordTime", seconds);
                currentTime = seconds;
            }
        }
    });

    ffmpegProcess.on('error', (err) => {
        console.error('FFmpeg 启动失败:', err);
        ffmpegProcess = null;
    });

    ffmpegProcess.on('exit', (code, signal) => {
        ffmpegProcess = null;
        repairVideo(filePath);
    });
}
const parseTime = (timeStr) => {
    const parts = timeStr.split(':');
    let seconds = 0;
    if (parts.length === 3) {
        // HH:MM:SS.ms
        seconds = parseInt(parts[0]) * 3600 +
            parseInt(parts[1]) * 60 +
            parseInt(parts[2].split(".")[0]);
    }
    return seconds;
}
//修复文件
const repairVideo = (filePath) => {
    const ffmpeg = getFFmpegPath();
    const args = [
        '-i', filePath,
        filePath.replace("_temp", "")
    ]
    const process = spawn(ffmpeg, args, {
        stdio: ['ignore', 'pipe', 'pipe'], // 捕获 stdout 和 stderr
        detached: true // 创建独立进程组
    })
    process.on('error', (err) => {
        console.log("error");
    });
    process.on('exit', (code, signal) => {
        if (code === 0) {
            fs.unlinkSync(filePath)
            sender.send("finishRecording", filePath.replace("_temp", ""));
        }
    });
}

const getScreenInfo = (displayId) => {
    const displays = screen.getAllDisplays();
    return displays.find(item => {
        return item.id == displayId
    })
}

const stopRecording = () => {
    if (ffmpegProcess) {
        ffmpegProcess.kill('SIGINT');
    }
}
export {
    startRecording,
    stopRecording
}