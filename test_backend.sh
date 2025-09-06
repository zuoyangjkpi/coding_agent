#!/bin/bash

echo "🔍 测试后端连接状态..."

# 测试端口5001是否开放
if nc -z localhost 5001 2>/dev/null; then
    echo "✅ 端口5001已开放"
else
    echo "❌ 端口5001未开放"
    echo "请确保后端服务正在运行: cd backend && python3 src/main.py"
    exit 1
fi

# 测试健康检查端点
echo "🏥 测试健康检查端点..."
HEALTH_RESPONSE=$(curl -s -w "%{http_code}" http://localhost:5001/api/health -o /tmp/health_response.txt)

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "✅ 健康检查通过"
    echo "响应内容: $(cat /tmp/health_response.txt)"
else
    echo "❌ 健康检查失败 (HTTP $HEALTH_RESPONSE)"
    echo "响应内容: $(cat /tmp/health_response.txt)"
fi

# 测试AI模型端点
echo "🤖 测试AI模型端点..."
MODELS_RESPONSE=$(curl -s -w "%{http_code}" http://localhost:5001/api/ai/models -o /tmp/models_response.txt)

if [ "$MODELS_RESPONSE" = "200" ]; then
    echo "✅ AI模型端点正常"
    echo "可用模型: $(cat /tmp/models_response.txt)"
else
    echo "❌ AI模型端点失败 (HTTP $MODELS_RESPONSE)"
    echo "响应内容: $(cat /tmp/models_response.txt)"
fi

# 清理临时文件
rm -f /tmp/health_response.txt /tmp/models_response.txt

echo ""
echo "🎯 如果所有测试都通过，您可以："
echo "1. 重启前端服务: cd frontend && pnpm dev"
echo "2. 访问: http://localhost:5173"
echo ""
echo "如果测试失败，请检查："
echo "1. 后端是否正在运行: cd backend && python3 src/main.py"
echo "2. 环境变量是否正确配置: backend/.env"
echo "3. 依赖是否正确安装: pip3 install -r requirements-core.txt"

