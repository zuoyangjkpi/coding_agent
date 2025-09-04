# 多阶段构建 - 前端构建阶段
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY frontend/ ./
RUN pnpm run build

# Python后端阶段
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码
COPY backend/ ./backend/

# 安装Python依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制前端构建结果到后端静态文件目录
COPY --from=frontend-builder /app/frontend/dist ./backend/src/static/

# 创建必要的目录
RUN mkdir -p backend/src/database backend/projects

# 设置环境变量
ENV FLASK_APP=backend/src/main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令
CMD ["python", "backend/src/main.py"]

