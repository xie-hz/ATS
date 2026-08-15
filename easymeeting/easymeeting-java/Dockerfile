# EasyMeeting 信令服务（Spring Boot + Netty）
# 多阶段构建：Maven 编译 -> JRE 运行
# 构建: docker build -t easymeeting-java ./easymeeting/easymeeting-java
# 运行时配置通过 Spring 环境变量覆盖（见 compose.prod.yml）：
#   SPRING_DATASOURCE_URL / SPRING_REDIS_HOST / ATS_WEBHOOK_URL / OPENAPI_APIKEY ...

# ---- 构建阶段 ----
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build

# 先拷贝 pom 拉依赖，利用层缓存
COPY pom.xml .
RUN mvn -B dependency:go-offline

COPY src ./src
RUN mvn -B clean package -DskipTests && mv target/*.jar /app.jar

# ---- 运行阶段 ----
FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=build /app.jar app.jar

# 6060 = HTTP API (context-path /api)，6061 = Netty WebSocket 信令
EXPOSE 6060 6061

# 上传文件目录（对应 project.folder=/data）
VOLUME ["/data"]

ENTRYPOINT ["java", "-jar", "app.jar"]
