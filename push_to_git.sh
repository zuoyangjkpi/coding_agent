#!/bin/bash

# Coding Agent Git推送脚本
# 使用方法: ./push_to_git.sh [commit_message]

set -e

echo "🚀 Coding Agent Git推送脚本"
echo "================================"

# 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD --; then
    echo "📝 检测到未提交的更改"
    
    # 显示状态
    echo "当前Git状态:"
    git status --short
    
    # 添加所有更改
    echo "📦 添加所有更改到暂存区..."
    git add .
    
    # 获取提交消息
    if [ -n "$1" ]; then
        COMMIT_MSG="$1"
    else
        COMMIT_MSG="feat: 更新Coding Agent系统

- 完善AI模型配置和智能选择
- 添加项目聊天界面功能
- 修复前端显示问题
- 优化代码分析功能
- 更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    # 提交更改
    echo "💾 提交更改..."
    git commit -m "$COMMIT_MSG"
    
    echo "✅ 代码已成功提交到本地仓库"
else
    echo "✅ 没有检测到未提交的更改"
fi

# 检查远程仓库
echo "🔍 检查远程仓库配置..."
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "❌ 错误: 没有配置远程仓库"
    echo "请先配置远程仓库: git remote add origin <your-repo-url>"
    exit 1
fi

echo "远程仓库: $REMOTE_URL"

# 推送到远程仓库
echo "🚀 推送到远程仓库..."
echo "注意: 如果需要认证，请输入您的GitHub用户名和Personal Access Token"
echo "Personal Access Token获取方法: GitHub Settings > Developer settings > Personal access tokens"
echo ""

# 尝试推送
# 如果设置了GITHUB_TOKEN环境变量，使用token推送
if [ -n "$GITHUB_TOKEN" ]; then
    REPO_URL=$(git remote get-url origin)
    REPO_PATH=${REPO_URL#https://github.com/}
    if git push https://$GITHUB_TOKEN@github.com/$REPO_PATH main; then
        PUSH_SUCCESS=true
    else
        PUSH_SUCCESS=false
    fi
elif git push origin main; then
    PUSH_SUCCESS=true
else
    PUSH_SUCCESS=false
fi

if [ "$PUSH_SUCCESS" = true ]; then
    echo ""
    echo "🎉 成功推送到远程仓库!"
    echo "您可以在以下地址查看更新: $REMOTE_URL"
else
    echo ""
    echo "❌ 推送失败"
    echo "可能的原因:"
    echo "1. 网络连接问题"
    echo "2. 认证失败 - 请检查用户名和Personal Access Token"
    echo "3. 权限不足 - 请确保您有推送权限"
    echo ""
    echo "解决方案:"
    echo "1. 检查网络连接"
    echo "2. 使用Personal Access Token而不是密码"
    echo "3. 确保您是仓库的协作者或拥有者"
    echo ""
    echo "手动推送命令: git push origin main"
fi

echo ""
echo "📊 当前仓库状态:"
git log --oneline -5

