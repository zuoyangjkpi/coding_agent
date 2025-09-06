# Git推送指南

## 🚀 快速推送

### 方法1: 使用推送脚本（推荐）

```bash
# 使用默认提交消息
./push_to_git.sh

# 使用自定义提交消息
./push_to_git.sh "你的提交消息"
```

### 方法2: 手动推送

```bash
# 1. 添加所有更改
git add .

# 2. 提交更改
git commit -m "你的提交消息"

# 3. 推送到远程仓库
git push origin main
```

## 🔐 认证设置

### GitHub Personal Access Token

如果推送时需要认证，请使用Personal Access Token而不是密码：

1. 访问 GitHub Settings > Developer settings > Personal access tokens
2. 点击 "Generate new token"
3. 选择适当的权限（至少需要 `repo` 权限）
4. 复制生成的token
5. 在推送时使用token作为密码

### SSH密钥（推荐）

设置SSH密钥可以避免每次推送时输入认证信息：

```bash
# 1. 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 添加SSH密钥到ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. 复制公钥到GitHub
cat ~/.ssh/id_ed25519.pub
# 将输出的内容添加到GitHub Settings > SSH and GPG keys

# 4. 更改远程仓库URL为SSH格式
git remote set-url origin git@github.com:zuoyangjkpi/coding_agent.git
```

## 📊 当前仓库信息

- **远程仓库**: https://github.com/zuoyangjkpi/coding_agent.git
- **主分支**: main
- **最新提交**: 完善Coding Agent系统功能

## 🔧 常见问题解决

### 推送被拒绝

```bash
# 如果远程仓库有新的提交，先拉取
git pull origin main

# 然后再推送
git push origin main
```

### 认证失败

1. 确保使用正确的用户名
2. 使用Personal Access Token而不是密码
3. 检查token权限是否足够

### 权限不足

1. 确保您是仓库的协作者或拥有者
2. 检查仓库设置中的权限配置

## 📝 提交消息规范

建议使用以下格式的提交消息：

```
类型: 简短描述

详细描述（可选）
- 具体更改1
- 具体更改2
```

常用类型：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 🎯 最佳实践

1. **频繁提交**: 小而频繁的提交比大的提交更好
2. **清晰的消息**: 提交消息应该清楚地描述更改内容
3. **测试后提交**: 确保代码在提交前经过测试
4. **分支管理**: 对于大的功能，考虑使用功能分支

## 📞 获取帮助

如果遇到问题，可以：

1. 查看Git状态: `git status`
2. 查看提交历史: `git log --oneline -10`
3. 查看远程仓库: `git remote -v`
4. 查看当前分支: `git branch`

---

**注意**: 推送前请确保您有适当的权限，并且了解推送的内容。

