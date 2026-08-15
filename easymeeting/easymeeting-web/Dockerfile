# EasyMeeting 浏览器端（候选人 / 面试官 Web 客户端）
# 多阶段构建：Vite 打包 -> Nginx 托管静态资源并反代 /api、/ws
# 构建: docker build --build-arg VITE_TURN_URL=turn:user:pass@ip:3478 \
#         -t easymeeting-web ./easymeeting/easymeeting-web

# ---- 构建阶段 ----
FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# WebRTC ICE 配置（生产建议配 TURN，见 easymeeting/coturn-compose.yml）
ARG VITE_STUN_URL=stun:stun.l.google.com:19302
ARG VITE_TURN_URL=""
ENV VITE_STUN_URL=$VITE_STUN_URL
ENV VITE_TURN_URL=$VITE_TURN_URL

RUN npm run build

# ---- 运行阶段 ----
FROM nginx:1-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
