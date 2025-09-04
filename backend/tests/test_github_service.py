import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from src.services.github_service import GitHubService

class TestGitHubService:
    """GitHub服务测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.github_service = GitHubService()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """测试后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_parse_github_url_https(self):
        """测试解析HTTPS GitHub URL"""
        url = "https://github.com/user/repo"
        result = self.github_service.parse_github_url(url)
        
        assert result['owner'] == 'user'
        assert result['repo'] == 'repo'
        assert result['full_name'] == 'user/repo'
    
    def test_parse_github_url_git(self):
        """测试解析Git GitHub URL"""
        url = "https://github.com/user/repo.git"
        result = self.github_service.parse_github_url(url)
        
        assert result['owner'] == 'user'
        assert result['repo'] == 'repo'
        assert result['full_name'] == 'user/repo'
    
    def test_parse_github_url_invalid(self):
        """测试解析无效GitHub URL"""
        with pytest.raises(ValueError, match="Invalid GitHub URL format"):
            self.github_service.parse_github_url("invalid-url")
    
    @patch('requests.get')
    def test_get_repo_info_success(self, mock_get):
        """测试获取仓库信息成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test-repo',
            'full_name': 'user/test-repo',
            'description': 'Test repository',
            'language': 'Python',
            'size': 1024,
            'stargazers_count': 10,
            'forks_count': 5,
            'clone_url': 'https://github.com/user/test-repo.git',
            'ssh_url': 'git@github.com:user/test-repo.git',
            'default_branch': 'main',
            'created_at': '2023-01-01T00:00:00Z',
            'updated_at': '2023-01-02T00:00:00Z'
        }
        mock_get.return_value = mock_response
        
        result = self.github_service.get_repo_info("https://github.com/user/test-repo")
        
        assert result['success'] is True
        assert result['repo_info']['name'] == 'test-repo'
        assert result['repo_info']['language'] == 'Python'
    
    @patch('requests.get')
    def test_get_repo_info_failure(self, mock_get):
        """测试获取仓库信息失败"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        result = self.github_service.get_repo_info("https://github.com/user/nonexistent")
        
        assert result['success'] is False
        assert 'GitHub API error' in result['error']
    
    def test_read_file_content_success(self):
        """测试读取文件内容成功"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, 'test.py')
        test_content = "print('Hello, World!')"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        result = self.github_service.read_file_content(test_file)
        
        assert result['success'] is True
        assert result['content'] == test_content
        assert result['encoding'] == 'utf-8'
    
    def test_read_file_content_large_file(self):
        """测试读取大文件"""
        # 创建大于1MB的测试文件
        test_file = os.path.join(self.temp_dir, 'large.txt')
        large_content = 'x' * (1024 * 1024 + 1)  # 1MB + 1 byte
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(large_content)
        
        result = self.github_service.read_file_content(test_file)
        
        assert result['success'] is False
        assert 'File too large' in result['error']
    
    def test_read_file_content_not_found(self):
        """测试读取不存在的文件"""
        result = self.github_service.read_file_content('/nonexistent/file.txt')
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_write_file_content_success(self):
        """测试写入文件内容成功"""
        test_file = os.path.join(self.temp_dir, 'new_file.py')
        test_content = "def hello():\n    print('Hello!')"
        
        result = self.github_service.write_file_content(test_file, test_content)
        
        assert result['success'] is True
        assert result['file_path'] == test_file
        assert os.path.exists(test_file)
        
        # 验证文件内容
        with open(test_file, 'r', encoding='utf-8') as f:
            assert f.read() == test_content
    
    def test_get_file_tree_success(self):
        """测试获取文件树成功"""
        # 创建测试目录结构
        os.makedirs(os.path.join(self.temp_dir, 'src'))
        os.makedirs(os.path.join(self.temp_dir, 'tests'))
        
        # 创建测试文件
        with open(os.path.join(self.temp_dir, 'README.md'), 'w') as f:
            f.write('# Test')
        with open(os.path.join(self.temp_dir, 'src', 'main.py'), 'w') as f:
            f.write('print("Hello")')
        
        result = self.github_service.get_file_tree(self.temp_dir, max_depth=2)
        
        assert result['success'] is True
        assert 'tree' in result
        
        items = result['tree']['items']
        assert len(items) >= 2  # README.md, src, tests
        
        # 检查文件和目录类型
        readme_item = next((item for item in items if item['name'] == 'README.md'), None)
        assert readme_item is not None
        assert readme_item['type'] == 'file'
        
        src_item = next((item for item in items if item['name'] == 'src'), None)
        assert src_item is not None
        assert src_item['type'] == 'directory'
    
    @patch('git.Repo.clone_from')
    def test_clone_repository_success(self, mock_clone):
        """测试克隆仓库成功"""
        # 模拟git仓库
        mock_repo = Mock()
        mock_repo.active_branch.name = 'main'
        mock_repo.head.commit.hexsha = 'abc123'
        mock_clone.return_value = mock_repo
        
        # 模拟_get_repo_stats方法
        with patch.object(self.github_service, '_get_repo_stats') as mock_stats:
            mock_stats.return_value = {'total_files': 5, 'total_size': 1024}
            
            result = self.github_service.clone_repository(
                "https://github.com/user/repo.git", 
                self.temp_dir
            )
        
        assert result['success'] is True
        assert result['local_path'] == self.temp_dir
        assert result['branch'] == 'main'
        assert result['commit_hash'] == 'abc123'
    
    @patch('git.Repo.clone_from')
    def test_clone_repository_failure(self, mock_clone):
        """测试克隆仓库失败"""
        mock_clone.side_effect = Exception("Clone failed")
        
        result = self.github_service.clone_repository(
            "https://github.com/user/repo.git", 
            self.temp_dir
        )
        
        assert result['success'] is False
        assert 'Clone failed' in result['error']
    
    def test_detect_language(self):
        """测试语言检测"""
        assert self.github_service._detect_language('.py') == 'Python'
        assert self.github_service._detect_language('.js') == 'JavaScript'
        assert self.github_service._detect_language('.java') == 'Java'
        assert self.github_service._detect_language('.unknown') is None
    
    def test_get_repo_stats(self):
        """测试获取仓库统计信息"""
        # 创建测试文件
        os.makedirs(os.path.join(self.temp_dir, 'src'))
        
        with open(os.path.join(self.temp_dir, 'main.py'), 'w') as f:
            f.write('print("Hello")')
        with open(os.path.join(self.temp_dir, 'src', 'utils.js'), 'w') as f:
            f.write('console.log("Hello")')
        
        stats = self.github_service._get_repo_stats(self.temp_dir)
        
        assert 'total_files' in stats
        assert 'total_size' in stats
        assert 'file_types' in stats
        assert 'languages' in stats
        
        assert stats['total_files'] == 2
        assert '.py' in stats['file_types']
        assert '.js' in stats['file_types']
        assert 'Python' in stats['languages']
        assert 'JavaScript' in stats['languages']

