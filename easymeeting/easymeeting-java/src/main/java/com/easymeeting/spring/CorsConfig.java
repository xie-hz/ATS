package com.easymeeting.spring;

import com.easymeeting.utils.StringTools;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web 客户端跨域配置：允许浏览器访问 /api/** 与 /openapi/**。
 * 允许的来源通过 web.cors.origins 配置（逗号分隔），默认开放本地开发端口。
 */
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Value("${web.cors.origins:http://localhost:5173,http://localhost:6001,http://localhost:8080}")
    private String corsOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        String[] origins;
        if (StringTools.isEmpty(corsOrigins) || "*".equals(corsOrigins.trim())) {
            origins = new String[]{"*"};
        } else {
            origins = corsOrigins.split(",");
        }
        registry.addMapping("/**")
                .allowedOriginPatterns(origins)
                .allowedMethods("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .exposedHeaders("Content-Disposition")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
