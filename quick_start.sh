#!/bin/bash

# Coding Agent 快速启动脚本
# 使用方法: ./quick_start.sh

set -e

echo "🚀 Coding Agent 快速启动脚本"
echo "================================"

# 检查Python版本
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "检测到Python版本: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ 错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 检查Node.js版本
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    echo "检测到Node.js版本: v$NODE_VERSION"
    if [[ $NODE_VERSION -lt 16 ]]; then
        echo "⚠️  警告: 建议使用Node.js 16或更高版本"
    fi
else
    echo "❌ 错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/database
mkdir -p backend/projects

# 后端设置
echo "🔧 设置后端..."
cd backend

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
if [ -f "requirements-core.txt" ]; then
    pip install -r requirements-core.txt
else
    echo "核心依赖文件不存在，尝试安装基础依赖..."
    pip install flask flask-socketio flask-cors flask-sqlalchemy gevent
    pip install openai anthropic google-generativeai
    pip install gitpython requests pyyaml
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "复制环境变量模板..."
        cp .env.example .env
        echo "⚠️  请编辑 backend/.env 文件，添加您的API密钥"
    else
        echo "创建基础环境变量文件..."
        cat > .env << EOF
# AI模型API密钥
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# 数据库配置
DATABASE_URL=sqlite:///database/app.db

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000

# 安全密钥
SECRET_KEY=your_secret_key_here
EOF
        echo "⚠️  请编辑 backend/.env 文件，添加您的API密钥"
    fi
fi

cd ..

# 前端设置
echo "🎨 设置前端..."
cd frontend

# 安装前端依赖
if command -v pnpm &> /dev/null; then
    echo "使用pnpm安装前端依赖..."
    pnpm install
elif command -v yarn &> /dev/null; then
    echo "使用yarn安装前端依赖..."
    yarn install
else
    echo "使用npm安装前端依赖..."
    npm install
fi

# 检查前端环境变量
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "复制前端环境变量模板..."
        cp .env.example .env
    else
        echo "创建前端环境变量文件..."
        cat > .env << EOF
VITE_API_BASE_URL=http://localhost:5001
EOF
    fi
fi

cd ..

echo ""
echo "✅ 安装完成！"
echo ""
echo "🚀 启动服务:"
echo "1. 启动后端 (在一个终端中):"
echo "   cd backend && source venv/bin/activate && python3 src/main.py"
echo ""
echo "2. 启动前端 (在另一个终端中):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. 访问应用:"
echo "   前端: http://localhost:5173"
echo "   后端API: http://localhost:5001"
echo ""
echo "📝 注意事项:"
echo "- 请确保在 backend/.env 中配置了正确的API密钥"
echo "- 如果遇到问题，请查看 LOCAL_SETUP_GUIDE.md"
echo ""
echo "🎉 开始使用您的AI编程助手吧！"

