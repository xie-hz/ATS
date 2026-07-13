package com.easymeeting.entity.config;

import com.easymeeting.utils.StringTools;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component("appConfig")
public class AppConfig {
    private static final Logger logger = LoggerFactory.getLogger(AppConfig.class);

    /**
     * websocket 端口
     */
    @Value("${ws.port:}")
    private Integer wsPort;
    /**
     * 文件目录
     */
    @Value("${project.folder:}")
    private String projectFolder;

    @Value("${admin.emails:}")
    private String adminEmails;

    /**
     * 开放接口 API Key（ATS 服务账号调用 /openapi/* 时通过 X-API-Key 头校验）
     */
    @Value("${openapi.apikey:}")
    private String openApiApiKey;

    /**
     * ATS Webhook 地址，会议结束/取消时通知 ATS 更新面试状态
     */
    @Value("${ats.webhook.url:}")
    private String atsWebhookUrl;

    public String getProjectFolder() {
        if (!StringTools.isEmpty(projectFolder) && !projectFolder.endsWith("/")) {
            projectFolder = projectFolder + "/";
        }
        return projectFolder;
    }

    public String getAdminEmails() {
        return adminEmails;
    }

    public Integer getWsPort() {
        return wsPort;
    }

    public String getOpenApiApiKey() {
        return openApiApiKey;
    }

    public String getAtsWebhookUrl() {
        return atsWebhookUrl;
    }
}
