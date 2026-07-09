# ATS 招聘流程管理系统

面向 50～500 人科技公司的招聘流程管理平台，基于 FastAPI 全栈模板开发。

## 功能

- **职位管理**：创建/编辑/删除/发布/关闭/重新打开，支持审批流程
- **候选人管理**：简历上传、标签、搜索、邮箱去重
- **招聘看板**：Kanban 式拖拽推进（投递→筛选→面试→Offer→入职），批量推进，按评分排序
- **面试管理**：安排面试（面试官时间冲突检测）、评价、取消、详情查看
- **Offer 管理**：自动创建 Draft、薪资编辑、审批流（提交→审批→发送）、候选人门户接受/拒绝
- **候选人门户**：公开职位浏览、投递、邮箱验证码登录、查看申请状态
- **权限系统**：RBAC（admin/hr/hiring_manager/interviewer）+ 数据权限（全部/本部门/本人）
- **通知系统**：面试提醒、评价催办（Celery 定时任务）
- **审计日志**：关键操作变更记录
- **数据分析**：招聘漏斗、渠道转化、统计仪表盘
- **国际化**：默认中文，可切换英文

## 技术栈

- **后端**：FastAPI + SQLModel + PostgreSQL + Alembic + Celery + Redis
- **前端**：React + TypeScript + TanStack Router/Query + shadcn/ui + Tailwind CSS + recharts
- **部署**：Docker Compose + Traefik

## 待实现

- MinIO 文件存储（当前本地存储）
- 全文搜索（PostgreSQL tsvector）
- Redis 缓存与分布式锁
- 人才库归档
- AI 简历解析与候选人匹配
