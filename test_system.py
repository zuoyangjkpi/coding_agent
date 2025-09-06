#!/usr/bin/env python3
import requests
import json
import time

def test_backend():
    """测试后端API"""
    try:
        # 测试健康检查
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端健康检查通过")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_ai_models():
    """测试AI模型接口"""
    try:
        response = requests.get('http://localhost:5000/api/ai/models', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ AI模型接口正常，可用模型: {len(models.get('models', []))}")
            return True
        else:
            print(f"❌ AI模型接口失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI模型接口连接失败: {e}")
        return False

def test_github_api():
    """测试GitHub API"""
    try:
        # 测试获取分支接口
        response = requests.get('http://localhost:5000/api/github/branches?url=https://github.com/octocat/Hello-World', timeout=10)
        if response.status_code == 200:
            print("✅ GitHub分支API正常")
            return True
        else:
            print(f"❌ GitHub分支API失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GitHub API连接失败: {e}")
        return False

def main():
    print("🚀 开始系统功能测试...")
    print("-" * 50)
    
    results = []
    results.append(test_backend())
    results.append(test_ai_models())
    results.append(test_github_api())
    
    print("-" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有测试通过! ({passed}/{total})")
        print("✅ 系统已完全就绪，可以正常使用!")
    else:
        print(f"⚠️  部分测试失败 ({passed}/{total})")
        print("💡 请检查相关服务状态")

if __name__ == "__main__":
    main()
