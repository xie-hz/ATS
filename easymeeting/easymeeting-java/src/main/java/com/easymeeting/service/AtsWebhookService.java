package com.easymeeting.service;

import com.easymeeting.entity.config.AppConfig;
import com.easymeeting.entity.po.MeetingInfo;
import com.easymeeting.utils.JsonUtils;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * 会议事件 Webhook：当 ATS 面试会议结束/取消时，通知 ATS 更新面试状态。
 * 异步发送，失败仅记录日志，不影响会议流程。
 */
@Service
@Slf4j
public class AtsWebhookService {

    @Resource
    private AppConfig appConfig;

    /**
     * 通知 ATS 会议已结束。
     *
     * @param meetingInfo 会议信息
     * @param event       事件类型：FINISHED / CANCELLED
     */
    @Async
    public void notifyMeetingEvent(MeetingInfo meetingInfo, String event) {
        String webhookUrl = appConfig.getAtsWebhookUrl();
        if (webhookUrl == null || webhookUrl.isEmpty()) {
            return;
        }
        // 仅 ATS 面试会议才回调
        if (meetingInfo.getAtsBusinessId() == null || meetingInfo.getAtsBusinessId().isEmpty()) {
            return;
        }
        Map<String, Object> payload = new HashMap<>();
        payload.put("event", event);
        payload.put("meetingId", meetingInfo.getMeetingId());
        payload.put("meetingNo", meetingInfo.getMeetingNo());
        payload.put("atsBusinessId", meetingInfo.getAtsBusinessId());
        payload.put("status", meetingInfo.getStatus());
        String body = JsonUtils.convertObj2Json(payload);
        HttpURLConnection conn = null;
        try {
            URL url = new URL(webhookUrl);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);
            conn.setDoOutput(true);
            try (OutputStream os = conn.getOutputStream()) {
                os.write(body.getBytes(StandardCharsets.UTF_8));
            }
            int code = conn.getResponseCode();
            if (code < 200 || code >= 300) {
                log.warn("ATS webhook 回调失败: code={}, meetingId={}", code, meetingInfo.getMeetingId());
            }
        } catch (Exception e) {
            log.warn("ATS webhook 回调异常: meetingId={}, error={}", meetingInfo.getMeetingId(), e.getMessage());
        } finally {
            if (conn != null) {
                conn.disconnect();
            }
        }
    }
}
