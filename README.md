# Coding Agent - AI-Powered Code Analysis & Generation

一个基于AI的智能编程助手，能够读取GitHub仓库代码并进行分析、修改和生成。使用现代技术栈构建，提供完整的前后端解决方案。

## 🚀 功能特性

### 核心功能
- **GitHub集成**: 支持克隆、读取、修改和推送GitHub仓库
- **AI代码分析**: 使用多种AI模型进行代码分析和审查
- **代码生成**: 基于自然语言描述生成代码
- **实时协作**: WebSocket实时通信支持
- **语法解析**: 基于Tree-sitter的代码语法分析

### AI模型支持
- **DeepSeek R1**: 免费的高性能编程模型
- **Gemini 2.5 Flash**: Google的大上下文模型
- **Claude 3.5 Sonnet**: Anthropic的商业编程模型

### 支持的编程语言
- Python
- JavaScript/TypeScript
- Java
- C/C++
- C#
- PHP
- Ruby
- Go
- Rust
- 以及更多...

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Flask + Flask-SocketIO
- **数据库**: SQLite (可扩展到PostgreSQL)
- **代码分析**: Tree-sitter
- **版本控制**: GitPython
- **AI集成**: 多模型API支持

### 前端技术栈
- **框架**: React 18 + JavaScript
- **状态管理**: React Hooks
- **UI组件**: shadcn/ui + Tailwind CSS
- **代码编辑器**: Monaco Editor
- **实时通信**: Socket.IO Client

## 📦 安装部署

### 环境要求
- Python 3.11+
- Node.js 20+
- Git

### 后端部署

1. 克隆项目
```bash
git clone https://github.com/zuoyangjkpi/coding_agent.git
cd coding_agent
```

2. 设置后端环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量
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

4. 启动后端服务
```bash
python src/main.py
```

### 前端部署

1. 安装依赖
```bash
cd frontend
pnpm install
```

2. 启动开发服务器
```bash
pnpm run dev
```

3. 构建生产版本
```bash
pnpm run build
```

## 🔧 配置说明

### API密钥配置
在使用前，需要配置相应的AI模型API密钥：

- **OpenAI API**: 用于Claude模型调用
- **Google AI API**: 用于Gemini模型
- **DeepSeek API**: 用于DeepSeek R1模型
- **GitHub Token**: 用于GitHub仓库操作

### 数据库配置
默认使用SQLite数据库，数据文件位于 `backend/src/database/app.db`。
如需使用PostgreSQL，请修改 `backend/src/main.py` 中的数据库配置。

## 📖 使用指南

### 1. 创建项目
- 在主界面点击"新建项目"
- 填写项目名称和描述
- 可选择性添加GitHub仓库URL

### 2. 克隆仓库
- 如果项目关联了GitHub仓库，点击"克隆仓库"按钮
- 系统会自动下载并分析仓库结构

### 3. 代码分析
- 在文件浏览器中选择代码文件
- 使用代码编辑器进行查看和编辑
- 点击"分析代码"获取AI分析结果
- 点击"代码审查"获取代码质量报告

### 4. 代码生成
- 在编辑器中输入代码描述
- 选择目标编程语言
- 点击生成按钮获取AI生成的代码

### 5. 版本控制
- 修改代码后可以提交更改
- 支持推送到远程GitHub仓库

## 🔌 API接口

### 项目管理
- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建新项目
- `GET /api/projects/{id}` - 获取项目详情

### GitHub集成
- `POST /api/github/clone` - 克隆仓库
- `GET /api/github/file-tree/{project_id}` - 获取文件树
- `POST /api/github/file-content` - 获取文件内容
- `POST /api/github/save-file` - 保存文件
- `POST /api/github/commit` - 提交更改
- `POST /api/github/push` - 推送到远程

### AI分析
- `POST /api/ai/analyze-code` - 代码分析
- `POST /api/ai/generate-code` - 代码生成
- `POST /api/ai/modify-code` - 代码修改
- `POST /api/ai/review-code` - 代码审查

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Tree-sitter](https://tree-sitter.github.io/) - 代码语法解析
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) - 代码编辑器
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [React](https://reactjs.org/) - 前端框架
- [shadcn/ui](https://ui.shadcn.com/) - UI组件库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [提交Issue](https://github.com/zuoyangjkpi/coding_agent/issues)
- Email: your-email@example.com

---

**Coding Agent** - 让AI成为您的编程伙伴 🤖✨

