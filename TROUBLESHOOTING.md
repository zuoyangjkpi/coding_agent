# 🔧 故障排除指南

## 常见问题解决方案

### 1. 前端显示"未连接"状态

**症状**: 前端界面显示红色的"未连接"标识

**可能原因**:
- 后端服务未启动
- 端口配置错误
- 防火墙阻止连接

**解决步骤**:

1. **检查后端是否运行**:
```bash
./test_backend.sh
```

2. **如果后端未运行，启动后端**:
```bash
cd backend
python3 src/main.py
```

3. **检查端口占用**:
```bash
lsof -i :5001
netstat -tulpn | grep 5001
```

4. **重启前端服务**:
```bash
cd frontend
pnpm dev
```

### 2. API调用失败 (ECONNREFUSED)

**症状**: 控制台显示 `Error: connect ECONNREFUSED 127.0.0.1:5000`

**原因**: Vite代理配置指向错误的端口

**解决方案**:
1. 确保 `frontend/.env` 文件包含:
```env
VITE_BACKEND_URL=http://localhost:5001
```

2. 重启前端服务:
```bash
cd frontend
pnpm dev
```

### 3. 后端启动失败

**症状**: `python3 src/main.py` 报错

**常见错误和解决方案**:

#### 3.1 ModuleNotFoundError
```
ModuleNotFoundError: No module named 'flask'
```

**解决方案**:
```bash
cd backend
pip3 install -r requirements-core.txt
```

#### 3.2 权限错误
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
```bash
# 确保在正确的目录
cd backend
# 不要使用sudo运行
python3 src/main.py
```

#### 3.3 端口占用
```
OSError: [Errno 98] Address already in use
```

**解决方案**:
```bash
# 查找占用端口的进程
lsof -ti:5001
# 终止进程
kill -9 <PID>
```

### 4. 前端界面显示异常

#### 4.1 界面显示为长条形
**原因**: CSS样式问题

**解决方案**: 已在最新版本中修复，请拉取最新代码:
```bash
git pull origin main
```

#### 4.2 组件加载失败
**症状**: 界面空白或组件缺失

**解决方案**:
```bash
cd frontend
rm -rf node_modules
pnpm install
pnpm dev
```

### 5. WebSocket连接失败

**症状**: 实时功能不工作

**解决方案**:
1. 检查后端Socket.IO配置
2. 确保防火墙允许WebSocket连接
3. 重启前后端服务

### 6. AI功能不工作

**症状**: 代码分析、聊天功能无响应

**可能原因**:
- API密钥未配置
- API密钥无效
- 网络连接问题

**解决方案**:
1. 检查 `backend/.env` 文件:
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

2. 验证API密钥有效性
3. 检查网络连接

## 🚀 快速诊断命令

### 一键诊断
```bash
./test_backend.sh
```

### 手动检查步骤

1. **检查后端状态**:
```bash
curl http://localhost:5001/api/health
```

2. **检查AI模型**:
```bash
curl http://localhost:5001/api/ai/models
```

3. **检查前端代理**:
```bash
curl http://localhost:5173/api/health
```

4. **查看后端日志**:
```bash
cd backend
python3 src/main.py
# 观察启动日志
```

5. **查看前端日志**:
```bash
cd frontend
pnpm dev
# 观察浏览器控制台
```

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **收集信息**:
   - 操作系统版本
   - Python版本: `python3 --version`
   - Node.js版本: `node --version`
   - 错误日志截图

2. **检查文档**:
   - `README.md` - 基本使用说明
   - `LOCAL_SETUP_GUIDE.md` - 详细安装指南

3. **重新安装**:
```bash
# 完全重新开始
git pull origin main
./quick_start.sh
```

## 🔄 重置系统

如果问题持续存在，可以完全重置：

```bash
# 停止所有服务
pkill -f "python3 src/main.py"
pkill -f "vite"

# 清理依赖
cd backend
rm -rf venv __pycache__ database/*.db

cd ../frontend
rm -rf node_modules .vite

# 重新安装
cd ..
./quick_start.sh
```

这将清除所有缓存和临时文件，重新开始安装。

