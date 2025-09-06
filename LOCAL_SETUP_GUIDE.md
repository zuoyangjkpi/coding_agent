# 本地环境安装指南

## 🚀 快速开始

### 系统要求
- Python 3.8+
- Node.js 16+
- Git

### 1. 克隆仓库
```bash
git clone https://github.com/zuoyangjkpi/coding_agent.git
cd coding_agent
```

### 2. 后端设置

#### 安装Python依赖

**方案1: 使用核心依赖（推荐）**
```bash
cd backend
pip3 install -r requirements-core.txt
```

**方案2: 使用完整依赖**
```bash
cd backend
pip3 install -r requirements.txt
```

**方案3: 如果遇到版本冲突，使用虚拟环境**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements-core.txt
```

**方案4: 手动安装核心依赖**
```bash
pip3 install flask flask-socketio flask-cors flask-sqlalchemy gevent
pip3 install openai anthropic google-generativeai
pip3 install gitpython requests pyyaml
```

#### 配置环境变量
创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，添加您的API密钥：
```env
# AI模型API密钥
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# 数据库配置（可选，默认使用SQLite）
DATABASE_URL=sqlite:///database/app.db

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000

# 安全密钥
SECRET_KEY=your_secret_key_here
```

#### 启动后端服务
```bash
python3 src/main.py
```

后端将在 http://localhost:5001 启动

### 3. 前端设置

#### 安装Node.js依赖
```bash
cd ../frontend
npm install
# 或使用 pnpm
pnpm install
```

#### 配置环境变量
创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
VITE_API_BASE_URL=http://localhost:5001
```

#### 启动前端服务
```bash
npm run dev
# 或使用 pnpm
pnpm run dev
```

前端将在 http://localhost:5173 启动

## 🔧 常见问题解决

### 1. Python依赖安装失败

**问题**: `ModuleNotFoundError: No module named 'gevent'`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip
pip3 install gevent

# CentOS/RHEL
sudo yum install python3-devel python3-pip
pip3 install gevent

# macOS
brew install python3
pip3 install gevent
```

### 2. 权限错误

**问题**: `PermissionError: [Errno 13] Permission denied`

**解决方案**:
- 确保在项目目录中运行命令
- 不要使用sudo运行Python脚本
- 检查文件权限：`chmod +x push_to_git.sh`

### 3. 端口占用

**问题**: 端口5001或5173已被占用

**解决方案**:
```bash
# 查找占用端口的进程
lsof -ti:5001
lsof -ti:5173

# 终止进程
kill -9 <PID>

# 或修改配置使用其他端口
```

### 4. 数据库问题

**问题**: 数据库连接失败

**解决方案**:
- 确保 `backend/database` 目录存在
- 检查数据库文件权限
- 重新初始化数据库：删除 `database/app.db` 文件，重启后端

### 5. API密钥配置

**问题**: AI功能不工作

**解决方案**:
- 确保 `.env` 文件中的API密钥正确
- 检查API密钥权限和余额
- 验证网络连接

## 🎯 功能验证

### 1. 后端API测试
```bash
# 健康检查
curl http://localhost:5001/api/health

# 获取AI模型列表
curl http://localhost:5001/api/ai/models
```

### 2. 前端界面测试
- 访问 http://localhost:5173
- 创建新项目
- 测试聊天功能

## 📦 生产部署

### 使用Docker（推荐）
```bash
# 构建镜像
docker build -t coding-agent .

# 运行容器
docker-compose up -d
```

### 手动部署
1. 设置反向代理（Nginx）
2. 配置HTTPS证书
3. 设置环境变量
4. 使用进程管理器（PM2, systemd）

## 🔐 安全配置

### 1. API密钥管理
- 使用环境变量存储密钥
- 定期轮换API密钥
- 限制API密钥权限

### 2. 网络安全
- 配置防火墙规则
- 使用HTTPS
- 设置CORS策略

### 3. 数据安全
- 定期备份数据库
- 加密敏感数据
- 设置访问控制

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件
2. 检查GitHub Issues
3. 参考文档：
   - `README.md` - 项目概述
   - `DEPLOYMENT.md` - 部署指南
   - `GIT_PUSH_GUIDE.md` - Git使用指南

## 🎉 开始使用

安装完成后，您可以：

1. **创建项目**: 在前端界面创建新的代码分析项目
2. **聊天对话**: 与AI助手讨论代码问题
3. **代码分析**: 使用AI分析代码质量和结构
4. **Git管理**: 使用自动化脚本管理代码版本

享受您的AI编程助手之旅！🚀

