# Coding Agent 部署文档

## 环境变量配置

### 必需的API密钥

```bash
# OpenAI API (用于GPT模型)
export OPENAI_API_KEY="your_openai_api_key"

# Anthropic API (用于Claude模型)
export ANTHROPIC_API_KEY="your_anthropic_api_key"

# Google AI API (用于Gemini模型)
export GOOGLE_API_KEY="your_google_api_key"

# DeepSeek API (用于DeepSeek R1模型)
export DEEPSEEK_API_KEY="your_deepseek_api_key"

# GitHub Token (用于仓库操作)
export GITHUB_TOKEN="your_github_token"
```

### API端点配置

- **DeepSeek API**: https://api.deepseek.com/v1
- **Anthropic API**: https://api.anthropic.com/v1
- **Google AI API**: https://generativelanguage.googleapis.com/v1beta
- **OpenAI API**: https://api.openai.com/v1

## 当前API实现状态

### ✅ 已实现
- **OpenAI GPT模型**: 完全集成
- **DeepSeek R1**: 暂时使用GPT-4o-mini作为替代

### ⚠️ 需要完善
- **Claude模型**: 需要集成Anthropic API
- **Gemini模型**: 需要集成Google AI API

## 快速修复Claude和Gemini集成

### 1. 安装额外依赖

```bash
cd backend
pip install anthropic google-generativeai
```

### 2. 更新requirements.txt

```bash
pip freeze > requirements.txt
```

### 3. 修改ai_service.py中的API调用

需要将模拟响应替换为真实的API调用。

## 文件完整性检查

### 核心文件列表

#### 后端文件 ✅
- `backend/src/main.py` - Flask应用入口
- `backend/src/models/` - 数据模型
  - `user.py` - 用户模型
  - `project.py` - 项目模型
- `backend/src/routes/` - API路由
  - `user.py` - 用户路由
  - `project.py` - 项目路由
  - `ai.py` - AI服务路由
  - `github.py` - GitHub集成路由
- `backend/src/services/` - 业务服务
  - `ai_service.py` - AI服务
  - `github_service.py` - GitHub服务
  - `code_analysis_service.py` - 代码分析服务
- `backend/requirements.txt` - Python依赖

#### 前端文件 ✅
- `frontend/src/App.jsx` - 主应用组件
- `frontend/src/components/` - React组件
  - `ProjectManager.jsx` - 项目管理
  - `FileBrowser.jsx` - 文件浏览器
  - `CodeEditor.jsx` - 代码编辑器
  - `ui/` - UI组件库 (shadcn/ui)
- `frontend/package.json` - Node.js依赖
- `frontend/vite.config.js` - Vite配置

#### 配置文件 ✅
- `README.md` - 项目说明
- `LICENSE` - MIT许可证
- `.gitignore` - Git忽略文件

### 缺失的文件

#### 🔴 需要添加的文件
1. **环境配置文件**
   - `backend/.env.example` - 环境变量示例
   - `docker-compose.yml` - Docker部署配置
   - `Dockerfile` - Docker镜像配置

2. **CI/CD配置**
   - `.github/workflows/ci.yml` - GitHub Actions

3. **数据库迁移**
   - `backend/migrations/` - 数据库迁移脚本

4. **测试文件**
   - `backend/tests/` - 后端测试
   - `frontend/src/__tests__/` - 前端测试

## 立即需要修复的问题

1. **API配置错误**: Claude使用Anthropic API，不是OpenAI API
2. **缺少环境配置文件**: 需要添加.env.example
3. **API实现不完整**: Claude和Gemini只有模拟响应
4. **缺少Docker配置**: 便于部署
5. **缺少测试文件**: 保证代码质量

