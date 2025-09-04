import os
import git
import shutil
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import json

class GitHubService:
    """GitHub集成服务类"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CodingAgent/1.0'
        }
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
    
    def parse_github_url(self, github_url: str) -> Dict[str, str]:
        """解析GitHub URL，提取owner和repo信息"""
        try:
            # 支持多种GitHub URL格式
            if github_url.endswith('.git'):
                github_url = github_url[:-4]
            
            if 'github.com' in github_url:
                parts = github_url.split('/')
                if len(parts) >= 2:
                    owner = parts[-2]
                    repo = parts[-1]
                    return {
                        'owner': owner,
                        'repo': repo,
                        'full_name': f"{owner}/{repo}"
                    }
            
            raise ValueError("Invalid GitHub URL format")
        except Exception as e:
            raise ValueError(f"Failed to parse GitHub URL: {str(e)}")
    
    def get_repo_info(self, github_url: str) -> Dict[str, Any]:
        """获取GitHub仓库信息"""
        try:
            repo_info = self.parse_github_url(github_url)
            owner = repo_info['owner']
            repo = repo_info['repo']
            
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'repo_info': {
                        'name': data['name'],
                        'full_name': data['full_name'],
                        'description': data.get('description', ''),
                        'language': data.get('language', ''),
                        'size': data['size'],
                        'stars': data['stargazers_count'],
                        'forks': data['forks_count'],
                        'clone_url': data['clone_url'],
                        'ssh_url': data['ssh_url'],
                        'default_branch': data['default_branch'],
                        'created_at': data['created_at'],
                        'updated_at': data['updated_at']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f"GitHub API error: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def clone_repository(self, github_url: str, local_path: str, branch: str = None) -> Dict[str, Any]:
        """克隆GitHub仓库到本地"""
        try:
            # 确保本地路径不存在或为空
            if os.path.exists(local_path):
                if os.listdir(local_path):
                    shutil.rmtree(local_path)
                    os.makedirs(local_path)
            else:
                os.makedirs(local_path, exist_ok=True)
            
            # 克隆仓库
            if branch:
                repo = git.Repo.clone_from(github_url, local_path, branch=branch)
            else:
                repo = git.Repo.clone_from(github_url, local_path)
            
            # 获取仓库统计信息
            stats = self._get_repo_stats(local_path)
            
            return {
                'success': True,
                'local_path': local_path,
                'branch': repo.active_branch.name,
                'commit_hash': repo.head.commit.hexsha,
                'stats': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_tree(self, local_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """获取仓库文件树结构"""
        try:
            def build_tree(path: str, current_depth: int = 0) -> Dict[str, Any]:
                if current_depth > max_depth:
                    return None
                
                items = []
                try:
                    for item in sorted(os.listdir(path)):
                        if item.startswith('.'):
                            continue
                        
                        item_path = os.path.join(path, item)
                        relative_path = os.path.relpath(item_path, local_path)
                        
                        if os.path.isdir(item_path):
                            subtree = build_tree(item_path, current_depth + 1)
                            items.append({
                                'name': item,
                                'type': 'directory',
                                'path': relative_path,
                                'children': subtree['items'] if subtree else []
                            })
                        else:
                            file_size = os.path.getsize(item_path)
                            file_ext = os.path.splitext(item)[1].lower()
                            items.append({
                                'name': item,
                                'type': 'file',
                                'path': relative_path,
                                'size': file_size,
                                'extension': file_ext
                            })
                except PermissionError:
                    pass
                
                return {'items': items}
            
            tree = build_tree(local_path)
            return {
                'success': True,
                'tree': tree
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def read_file_content(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """读取文件内容"""
        try:
            # 检查文件大小，避免读取过大的文件
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB限制
                return {
                    'success': False,
                    'error': 'File too large (>1MB)'
                }
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                'success': True,
                'content': content,
                'size': file_size,
                'encoding': encoding
            }
            
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return {
                    'success': True,
                    'content': content,
                    'size': file_size,
                    'encoding': 'latin-1'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to decode file: {str(e)}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def write_file_content(self, file_path: str, content: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """写入文件内容"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {
                'success': True,
                'file_path': file_path,
                'size': len(content.encode(encoding))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def commit_changes(self, local_path: str, message: str, files: List[str] = None) -> Dict[str, Any]:
        """提交更改到本地仓库"""
        try:
            repo = git.Repo(local_path)
            
            # 添加文件到暂存区
            if files:
                for file_path in files:
                    repo.index.add([file_path])
            else:
                repo.git.add(A=True)  # 添加所有更改
            
            # 检查是否有更改
            if not repo.index.diff("HEAD"):
                return {
                    'success': False,
                    'error': 'No changes to commit'
                }
            
            # 提交更改
            commit = repo.index.commit(message)
            
            return {
                'success': True,
                'commit_hash': commit.hexsha,
                'message': message,
                'files_changed': len(commit.stats.files)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def push_changes(self, local_path: str, remote: str = 'origin', branch: str = None) -> Dict[str, Any]:
        """推送更改到远程仓库"""
        try:
            repo = git.Repo(local_path)
            
            if not branch:
                branch = repo.active_branch.name
            
            # 推送到远程仓库
            origin = repo.remote(remote)
            push_info = origin.push(branch)
            
            return {
                'success': True,
                'remote': remote,
                'branch': branch,
                'push_info': str(push_info[0]) if push_info else 'No changes pushed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_repo_stats(self, local_path: str) -> Dict[str, Any]:
        """获取仓库统计信息"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'file_types': {},
                'languages': {}
            }
            
            for root, dirs, files in os.walk(local_path):
                # 跳过.git目录
                if '.git' in root:
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        stats['total_files'] += 1
                        stats['total_size'] += file_size
                        
                        if file_ext:
                            stats['file_types'][file_ext] = stats['file_types'].get(file_ext, 0) + 1
                        
                        # 简单的语言检测
                        language = self._detect_language(file_ext)
                        if language:
                            stats['languages'][language] = stats['languages'].get(language, 0) + 1
                            
                    except (OSError, IOError):
                        continue
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_language(self, file_ext: str) -> Optional[str]:
        """根据文件扩展名检测编程语言"""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown'
        }
        return language_map.get(file_ext)

# 全局GitHub服务实例
github_service = GitHubService()

