import pytest
import os
import sys
import tempfile
from unittest.mock import patch

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def temp_dir():
    """创建临时目录的fixture"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_env_vars():
    """模拟环境变量的fixture"""
    env_vars = {
        'OPENAI_API_KEY': 'test_openai_key',
        'ANTHROPIC_API_KEY': 'test_anthropic_key',
        'GOOGLE_API_KEY': 'test_google_key',
        'DEEPSEEK_API_KEY': 'test_deepseek_key',
        'GITHUB_TOKEN': 'test_github_token'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def sample_code():
    """示例代码的fixture"""
    return {
        'python': '''
def fibonacci(n):
    """计算斐波那契数列的第n项"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    for i in range(10):
        print(f"fibonacci({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()
''',
        'javascript': '''
function fibonacci(n) {
    // 计算斐波那契数列的第n项
    if (n <= 1) {
        return n;
    }
    return fibonacci(n-1) + fibonacci(n-2);
}

function main() {
    for (let i = 0; i < 10; i++) {
        console.log(`fibonacci(${i}) = ${fibonacci(i)}`);
    }
}

main();
''',
        'java': '''
public class Fibonacci {
    /**
     * 计算斐波那契数列的第n项
     */
    public static int fibonacci(int n) {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n-1) + fibonacci(n-2);
    }
    
    public static void main(String[] args) {
        for (int i = 0; i < 10; i++) {
            System.out.println("fibonacci(" + i + ") = " + fibonacci(i));
        }
    }
}
'''
    }

@pytest.fixture
def mock_github_repo_response():
    """模拟GitHub仓库API响应的fixture"""
    return {
        'name': 'test-repo',
        'full_name': 'testuser/test-repo',
        'description': 'A test repository',
        'language': 'Python',
        'size': 1024,
        'stargazers_count': 42,
        'forks_count': 7,
        'clone_url': 'https://github.com/testuser/test-repo.git',
        'ssh_url': 'git@github.com:testuser/test-repo.git',
        'default_branch': 'main',
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-12-01T00:00:00Z'
    }

