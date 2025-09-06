from flask import Blueprint, request, jsonify
from src.services.github_service import github_service
from src.models.user import db
from src.models.project import Project, CodeFile
import os
import json
import requests
import re
from datetime import datetime

github_bp = Blueprint('github', __name__)

def parse_github_url(url):
    """解析GitHub URL，提取用户名和仓库名"""
    pattern = r'github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

@github_bp.route('/github/branches', methods=['GET'])
def get_branches():
    """获取GitHub仓库的分支列表"""
    try:
        github_url = request.args.get('url')
        if not github_url:
            return jsonify({
                'success': False,
                'error': 'GitHub URL is required'
            }), 400
        
        # 解析GitHub URL
        owner, repo = parse_github_url(github_url)
        if not owner or not repo:
            return jsonify({
                'success': False,
                'error': 'Invalid GitHub URL format'
            }), 400
        
        # 构建GitHub API URL
        api_url = f'https://api.github.com/repos/{owner}/{repo}/branches'
        
        # 设置请求头
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Coding-Agent/1.0'
        }
        
        # 如果有GitHub token，添加到请求头
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        # 发送请求
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            branches_data = response.json()
            branches = [branch['name'] for branch in branches_data]
            
            return jsonify({
                'success': True,
                'branches': branches
            })
        elif response.status_code == 404:
            return jsonify({
                'success': False,
                'error': 'Repository not found or private'
            }), 404
        else:
            return jsonify({
                'success': False,
                'error': f'GitHub API error: {response.status_code}'
            }), response.status_code
            
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Network error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@github_bp.route('/github/repo-info', methods=['POST'])
def get_repo_info():
    """获取GitHub仓库信息"""
    try:
        data = request.get_json()
        
        if not data or not data.get('github_url'):
            return jsonify({
                'success': False,
                'error': 'GitHub URL is required'
            }), 400
        
        github_url = data['github_url']
        result = github_service.get_repo_info(github_url)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@github_bp.route('/github/clone', methods=['POST'])
def clone_repository():
    """克隆GitHub仓库"""
    try:
        data = request.get_json()
        
        if not data or not data.get('github_url') or not data.get('project_id'):
            return jsonify({
                'success': False,
                'error': 'GitHub URL and project ID are required'
            }), 400
        
        github_url = data['github_url']
        project_id = data['project_id']
        branch = data.get('branch')
        
        # 获取项目信息
        project = Project.query.get_or_404(project_id)
        
        # 设置本地路径
        projects_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'projects')
        os.makedirs(projects_dir, exist_ok=True)
        local_path = os.path.join(projects_dir, f"project_{project_id}")
        
        # 更新项目状态
        project.status = 'cloning'
        project.github_url = github_url
        project.local_path = local_path
        db.session.commit()
        
        # 克隆仓库
        result = github_service.clone_repository(github_url, local_path, branch)
        
        if result['success']:
            # 更新项目状态
            project.status = 'ready'
            db.session.commit()
            
            # 扫描并保存文件信息
            scan_result = scan_project_files(project_id, local_path)
            result['files_scanned'] = scan_result
        else:
            # 克隆失败，更新状态
            project.status = 'error'
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        # 更新项目状态为错误
        try:
            project = Project.query.get(data.get('project_id'))
            if project:
                project.status = 'error'
                db.session.commit()
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@github_bp.route('/github/file-tree/<int:project_id>', methods=['GET'])
def get_file_tree(project_id):
    """获取项目文件树"""
    try:
        project = Project.query.get_or_404(project_id)
        
        if not project.local_path or not os.path.exists(project.local_path):
            return jsonify({
                'success': False,
                'error': 'Project not cloned or local path not found'
            }), 404
        
        max_depth = request.args.get('max_depth', 3, type=int)
        result = github_service.get_file_tree(project.local_path, max_depth)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@github_bp.route('/github/file-content', methods=['POST'])
def get_file_content():
    """获取文件内容"""
    try:
        data = request.get_json()
        
        if not data or not data.get('project_id') or not data.get('file_path'):
            return jsonify({
                'success': False,
                'error': 'Project ID and file path are required'
            }), 400
        
        project_id = data['project_id']
        file_path = data['file_path']
        
        project = Project.query.get_or_404(project_id)
        
        if not project.local_path:
            return jsonify({
                'success': False,
                'error': 'Project not cloned'
            }), 404
        
        full_file_path = os.path.join(project.local_path, file_path)
        
        if not os.path.exists(full_file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        result = github_service.read_file_content(full_file_path)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@github_bp.route('/github/save-file', methods=['POST'])
def save_file_content():
    """保存文件内容"""
    try:
        data = request.get_json()
        
        if not data or not data.get('project_id') or not data.get('file_path') or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Project ID, file path, and content are required'
            }), 400
        
        project_id = data['project_id']
        file_path = data['file_path']
        content = data['content']
        
        project = Project.query.get_or_404(project_id)
        
        if not project.local_path:
            return jsonify({
                'success': False,
                'error': 'Project not cloned'
            }), 404
        
        full_file_path = os.path.join(project.local_path, file_path)
        result = github_service.write_file_content(full_file_path, content)
        
        if result['success']:
            # 更新数据库中的文件记录
            code_file = CodeFile.query.filter_by(
                project_id=project_id,
                file_path=file_path
            ).first()
            
            if code_file:
                code_file.content = content
                code_file.size = len(content.encode('utf-8'))
                code_file.last_modified = datetime.utcnow()
            else:
                # 创建新的文件记录
                code_file = CodeFile(
                    file_path=file_path,
                    file_name=os.path.basename(file_path),
                    file_type=os.path.splitext(file_path)[1].lower(),
                    content=content,
                    size=len(content.encode('utf-8')),
                    last_modified=datetime.utcnow(),
                    project_id=project_id
                )
                db.session.add(code_file)
            
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@github_bp.route('/github/commit', methods=['POST'])
def commit_changes():
    """提交更改"""
    try:
        data = request.get_json()
        
        if not data or not data.get('project_id') or not data.get('message'):
            return jsonify({
                'success': False,
                'error': 'Project ID and commit message are required'
            }), 400
        
        project_id = data['project_id']
        message = data['message']
        files = data.get('files')  # 可选，指定要提交的文件
        
        project = Project.query.get_or_404(project_id)
        
        if not project.local_path:
            return jsonify({
                'success': False,
                'error': 'Project not cloned'
            }), 404
        
        result = github_service.commit_changes(project.local_path, message, files)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@github_bp.route('/github/push', methods=['POST'])
def push_changes():
    """推送更改到远程仓库"""
    try:
        data = request.get_json()
        
        if not data or not data.get('project_id'):
            return jsonify({
                'success': False,
                'error': 'Project ID is required'
            }), 400
        
        project_id = data['project_id']
        remote = data.get('remote', 'origin')
        branch = data.get('branch')
        
        project = Project.query.get_or_404(project_id)
        
        if not project.local_path:
            return jsonify({
                'success': False,
                'error': 'Project not cloned'
            }), 404
        
        result = github_service.push_changes(project.local_path, remote, branch)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def scan_project_files(project_id: int, project_path: str) -> dict:
    """扫描项目文件并保存到数据库"""
    try:
        files_added = 0
        
        for root, dirs, files in os.walk(project_path):
            # 跳过.git和其他隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                
                # 只处理代码文件
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs']:
                    try:
                        # 读取文件内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查是否已存在
                        existing_file = CodeFile.query.filter_by(
                            project_id=project_id,
                            file_path=relative_path
                        ).first()
                        
                        if not existing_file:
                            code_file = CodeFile(
                                file_path=relative_path,
                                file_name=file,
                                file_type=file_ext,
                                content=content,
                                size=len(content.encode('utf-8')),
                                last_modified=datetime.fromtimestamp(os.path.getmtime(file_path)),
                                project_id=project_id
                            )
                            db.session.add(code_file)
                            files_added += 1
                    
                    except (UnicodeDecodeError, IOError):
                        # 跳过无法读取的文件
                        continue
        
        db.session.commit()
        
        return {
            'success': True,
            'files_added': files_added
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

