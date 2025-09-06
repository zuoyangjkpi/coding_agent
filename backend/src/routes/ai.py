from flask import Blueprint, request, jsonify
from src.services.ai_service import ai_service
from src.services.code_analysis_service import code_analysis_service
from src.models.user import db
from src.models.project import AnalysisTask, CodeFile
import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/supported-languages', methods=['GET'])
def get_supported_languages():
    """获取支持的编程语言列表"""
    try:
        languages = {
            'python': {'name': 'Python', 'extensions': ['.py'], 'type': 'programming'},
            'javascript': {'name': 'JavaScript', 'extensions': ['.js', '.jsx'], 'type': 'programming'},
            'typescript': {'name': 'TypeScript', 'extensions': ['.ts', '.tsx'], 'type': 'programming'},
            'java': {'name': 'Java', 'extensions': ['.java'], 'type': 'programming'},
            'cpp': {'name': 'C++', 'extensions': ['.cpp', '.cc', '.cxx', '.hpp'], 'type': 'programming'},
            'c': {'name': 'C', 'extensions': ['.c', '.h'], 'type': 'programming'},
            'csharp': {'name': 'C#', 'extensions': ['.cs'], 'type': 'programming'},
            'php': {'name': 'PHP', 'extensions': ['.php'], 'type': 'programming'},
            'ruby': {'name': 'Ruby', 'extensions': ['.rb'], 'type': 'programming'},
            'go': {'name': 'Go', 'extensions': ['.go'], 'type': 'programming'},
            'rust': {'name': 'Rust', 'extensions': ['.rs'], 'type': 'programming'},
            'swift': {'name': 'Swift', 'extensions': ['.swift'], 'type': 'programming'},
            'kotlin': {'name': 'Kotlin', 'extensions': ['.kt'], 'type': 'programming'},
            'scala': {'name': 'Scala', 'extensions': ['.scala'], 'type': 'programming'},
            'html': {'name': 'HTML', 'extensions': ['.html', '.htm'], 'type': 'markup'},
            'css': {'name': 'CSS', 'extensions': ['.css'], 'type': 'stylesheet'},
            'scss': {'name': 'SCSS', 'extensions': ['.scss'], 'type': 'stylesheet'},
            'sass': {'name': 'Sass', 'extensions': ['.sass'], 'type': 'stylesheet'},
            'less': {'name': 'Less', 'extensions': ['.less'], 'type': 'stylesheet'},
            'sql': {'name': 'SQL', 'extensions': ['.sql'], 'type': 'query'},
            'shell': {'name': 'Shell', 'extensions': ['.sh', '.bash', '.zsh', '.fish'], 'type': 'script'},
            'json': {'name': 'JSON', 'extensions': ['.json'], 'type': 'data'},
            'xml': {'name': 'XML', 'extensions': ['.xml'], 'type': 'markup'},
            'yaml': {'name': 'YAML', 'extensions': ['.yaml', '.yml'], 'type': 'data'},
            'toml': {'name': 'TOML', 'extensions': ['.toml'], 'type': 'data'},
            'ini': {'name': 'INI', 'extensions': ['.ini', '.cfg', '.conf'], 'type': 'config'},
            'markdown': {'name': 'Markdown', 'extensions': ['.md', '.markdown'], 'type': 'markup'},
            'text': {'name': 'Plain Text', 'extensions': ['.txt', '.log'], 'type': 'text'}
        }
        
        return jsonify({
            'success': True,
            'languages': languages,
            'total_count': len(languages)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/detect-language', methods=['POST'])
def detect_language():
    """检测代码语言"""
    try:
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        content = data['content']
        filename = data.get('filename', '')
        
        print(f"语言检测请求: filename={filename}")
        
        # 使用代码分析服务检测语言
        detected_language = code_analysis_service.detect_language_from_content(content, filename)
        
        # 构建结果
        result = {
            'success': True,
            'language': detected_language,
            'filename': filename,
            'confidence': 'high' if filename and os.path.splitext(filename)[1] else 'medium'
        }
        
        print(f"语言检测完成: {detected_language}")
        return jsonify(result)
        
    except Exception as e:
        print(f"语言检测失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/models', methods=['GET'])
def get_available_models():
    """获取可用的AI模型列表"""
    try:
        models = ai_service.get_available_models()
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/analyze-code', methods=['POST'])
def analyze_code():
    """分析代码"""
    try:
        data = request.get_json()
        
        if not data or not data.get('code'):
            return jsonify({
                'success': False,
                'error': 'Code content is required'
            }), 400
        
        code = data['code']
        file_type = data.get('file_type', 'python')
        model = data.get('model', 'claude-3.7-sonnet')
        project_id = data.get('project_id')
        
        print(f"分析代码请求: file_type={file_type}, model={model}, project_id={project_id}")
        
        # AI分析
        ai_result = ai_service.analyze_code(code, file_type, model)
        
        # 将文件类型转换为正确的文件扩展名
        file_ext_map = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'html': '.html',
            'css': '.css'
        }
        file_ext = file_ext_map.get(file_type, '.txt')
        
        # Tree-sitter分析
        ts_result = code_analysis_service.analyze_file('temp_file' + file_ext, code)
        
        # 如果提供了项目ID，保存分析任务
        if project_id:
            try:
                analysis_task = AnalysisTask(
                    task_type='code_analysis',
                    status='completed',
                    result=json.dumps({
                        'ai_analysis': ai_result,
                        'syntax_analysis': ts_result
                    }),
                    created_at=datetime.utcnow(),
                    project_id=project_id
                )
                db.session.add(analysis_task)
                db.session.commit()
                print(f"分析任务已保存: task_id={analysis_task.id}")
            except Exception as e:
                print(f"保存分析任务失败: {e}")
        
        # 合并结果
        result = {
            'success': True,
            'type': 'analysis',
            'ai_analysis': ai_result,
            'syntax_analysis': ts_result,
            'model_used': model,
            'file_type': file_type
        }
        
        print(f"分析完成，返回结果: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"代码分析失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/generate-code', methods=['POST'])
def generate_code():
    """生成代码"""
    try:
        data = request.get_json()
        
        if not data or not data.get('description'):
            return jsonify({
                'success': False,
                'error': 'Code description is required'
            }), 400
        
        description = data['description']
        language = data.get('language', 'python')
        model = data.get('model', 'claude-3.7-sonnet')
        project_id = data.get('project_id')
        
        # 生成代码
        result = ai_service.generate_code(description, language, model)
        
        # 如果提供了项目ID，保存分析任务
        if project_id and result['success']:
            task = AnalysisTask(
                task_type='generate',
                description=f'Code generation: {description}',
                input_data=json.dumps({
                    'description': description,
                    'language': language
                }),
                output_data=json.dumps(result),
                ai_model=model,
                status='completed',
                completed_at=datetime.utcnow(),
                project_id=project_id
            )
            db.session.add(task)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/modify-code', methods=['POST'])
def modify_code():
    """修改代码"""
    try:
        data = request.get_json()
        
        if not data or not data.get('original_code') or not data.get('modification_request'):
            return jsonify({
                'success': False,
                'error': 'Original code and modification request are required'
            }), 400
        
        original_code = data['original_code']
        modification_request = data['modification_request']
        file_type = data.get('file_type', 'python')
        model = data.get('model', 'claude-3.7-sonnet')
        project_id = data.get('project_id')
        
        # 修改代码
        result = ai_service.modify_code(original_code, modification_request, file_type, model)
        
        # 如果提供了项目ID，保存分析任务
        if project_id and result['success']:
            task = AnalysisTask(
                task_type='modify',
                description=f'Code modification: {modification_request}',
                input_data=json.dumps({
                    'original_code': original_code[:1000] + '...' if len(original_code) > 1000 else original_code,
                    'modification_request': modification_request,
                    'file_type': file_type
                }),
                output_data=json.dumps(result),
                ai_model=model,
                status='completed',
                completed_at=datetime.utcnow(),
                project_id=project_id
            )
            db.session.add(task)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/review-code', methods=['POST'])
def review_code():
    """代码审查"""
    try:
        data = request.get_json()
        
        if not data or not data.get('code'):
            return jsonify({
                'success': False,
                'error': 'Code content is required'
            }), 400
        
        code = data['code']
        file_type = data.get('file_type', 'python')
        model = data.get('model', 'claude-3.7-sonnet')
        project_id = data.get('project_id')
        
        print(f"代码审查请求: file_type={file_type}, model={model}, project_id={project_id}")
        
        # 代码审查
        ai_result = ai_service.review_code(code, file_type, model)
        
        # 如果提供了项目ID，保存分析任务
        if project_id:
            try:
                analysis_task = AnalysisTask(
                    task_type='code_review',
                    status='completed',
                    result=json.dumps({
                        'review_result': ai_result
                    }),
                    created_at=datetime.utcnow(),
                    project_id=project_id
                )
                db.session.add(analysis_task)
                db.session.commit()
                print(f"审查任务已保存: task_id={analysis_task.id}")
            except Exception as e:
                print(f"保存审查任务失败: {e}")
        
        # 构建结果
        result = {
            'success': True,
            'type': 'review',
            'review_result': ai_result,
            'model_used': model,
            'file_type': file_type
        }
        
        print(f"审查完成，返回结果: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"代码审查失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/analyze-repository', methods=['POST'])
def analyze_repository():
    """直接分析GitHub仓库（无需预先克隆到数据库）"""
    try:
        data = request.get_json()
        
        if not data or not data.get('github_url'):
            return jsonify({
                'success': False,
                'error': 'GitHub URL is required'
            }), 400
        
        github_url = data['github_url']
        analysis_type = data.get('analysis_type', 'overview')  # overview, security, performance, architecture
        model = data.get('model', 'claude-3.7-sonnet')
        branch = data.get('branch', 'main')
        
        print(f"仓库分析请求: github_url={github_url}, analysis_type={analysis_type}, model={model}, branch={branch}")
        
        # 导入GitHub服务
        from src.services.github_service import GitHubService
        github_service = GitHubService()
        
        # 获取仓库信息
        try:
            repo_info = github_service.get_repo_info(github_url)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get repository info: {str(e)}'
            }), 400
        
        # 创建临时目录用于克隆
        import tempfile
        import uuid
        temp_dir = os.path.join(tempfile.gettempdir(), f"coding_agent_{uuid.uuid4().hex[:8]}")
        
        try:
            # 克隆仓库
            clone_result = github_service.clone_repository(github_url, temp_dir, branch)
            if not clone_result['success']:
                return jsonify({
                    'success': False,
                    'error': f'Failed to clone repository: {clone_result["error"]}'
                }), 400
            
            # 分析仓库结构
            file_tree = github_service.get_file_tree(temp_dir, max_depth=5)
            
            # 扫描代码文件
            code_files = []
            total_files = 0
            languages = {}
            
            for root, dirs, files in os.walk(temp_dir):
                # 跳过.git目录和其他隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, temp_dir)
                    
                    # 检查是否为代码文件
                    if code_analysis_service._is_code_file(file):
                        total_files += 1
                        
                        # 检测语言
                        detected_lang = code_analysis_service.detect_language_from_content('', file)
                        if detected_lang in languages:
                            languages[detected_lang] += 1
                        else:
                            languages[detected_lang] = 1
                        
                        # 读取文件内容（限制大小）
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if len(content) > 5000:  # 限制文件大小
                                    content = content[:5000] + '...'
                                
                                code_files.append({
                                    'path': relative_path,
                                    'name': file,
                                    'type': detected_lang,
                                    'size': len(content),
                                    'content': content
                                })
                        except Exception as e:
                            print(f"Failed to read file {file_path}: {e}")
                            continue
                    
                    # 限制分析的文件数量
                    if len(code_files) >= 20:
                        break
                
                if len(code_files) >= 20:
                    break
            
            # 构建项目概览
            project_overview = {
                'name': repo_info.get('name', 'Unknown'),
                'description': repo_info.get('description', ''),
                'github_url': github_url,
                'branch': branch,
                'total_files': total_files,
                'languages': languages,
                'file_structure': file_tree,
                'clone_stats': clone_result.get('stats', {})
            }
            
            # 选择重要文件进行AI分析
            important_files = code_files[:10]  # 分析前10个文件
            
            # 调用AI服务进行项目分析
            ai_result = ai_service.analyze_project(project_overview, important_files, analysis_type, model)
            
            # 构建结果
            result = {
                'success': True,
                'type': 'repository_analysis',
                'repository_info': repo_info,
                'project_overview': project_overview,
                'ai_analysis': ai_result,
                'analysis_type': analysis_type,
                'model_used': model,
                'files_analyzed': len(important_files),
                'total_code_files': len(code_files)
            }
            
            print(f"仓库分析完成，分析了{len(important_files)}个文件")
            return jsonify(result)
            
        finally:
            # 清理临时目录
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Failed to cleanup temp directory: {e}")
        
    except Exception as e:
        print(f"仓库分析失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/ai/analyze-project', methods=['POST'])
def analyze_project():
    """分析整个项目"""
    try:
        data = request.get_json()
        
        if not data or not data.get('project_id'):
            return jsonify({
                'success': False,
                'error': 'Project ID is required'
            }), 400
        
        project_id = data['project_id']
        analysis_type = data.get('analysis_type', 'overview')  # overview, security, performance, architecture
        model = data.get('model', 'claude-3.7-sonnet')
        
        print(f"项目分析请求: project_id={project_id}, analysis_type={analysis_type}, model={model}")
        
        # 获取项目信息
        from src.models.project import Project
        project = Project.query.get_or_404(project_id)
        
        if not project.local_path or not os.path.exists(project.local_path):
            return jsonify({
                'success': False,
                'error': 'Project not cloned or local path not found'
            }), 404
        
        # 获取项目中的所有代码文件
        code_files = CodeFile.query.filter_by(project_id=project_id).all()
        
        if not code_files:
            return jsonify({
                'success': False,
                'error': 'No code files found in project'
            }), 404
        
        # 构建项目概览
        project_overview = {
            'name': project.name,
            'description': project.description,
            'github_url': project.github_url,
            'total_files': len(code_files),
            'languages': {},
            'file_structure': []
        }
        
        # 统计语言分布
        for file in code_files:
            lang = file.file_type or 'unknown'
            if lang in project_overview['languages']:
                project_overview['languages'][lang] += 1
            else:
                project_overview['languages'][lang] = 1
            
            project_overview['file_structure'].append({
                'path': file.file_path,
                'name': file.file_name,
                'type': file.file_type,
                'size': file.size
            })
        
        # 选择重要文件进行AI分析（限制数量避免token过多）
        important_files = []
        for file in code_files[:10]:  # 只分析前10个文件
            if file.content and len(file.content.strip()) > 0:
                important_files.append({
                    'path': file.file_path,
                    'content': file.content[:2000],  # 限制内容长度
                    'type': file.file_type
                })
        
        # 调用AI服务进行项目分析
        ai_result = ai_service.analyze_project(project_overview, important_files, analysis_type, model)
        
        # 保存分析任务
        try:
            analysis_task = AnalysisTask(
                task_type='project_analysis',
                status='completed',
                result=json.dumps({
                    'project_overview': project_overview,
                    'ai_analysis': ai_result,
                    'analysis_type': analysis_type
                }),
                created_at=datetime.utcnow(),
                project_id=project_id
            )
            db.session.add(analysis_task)
            db.session.commit()
            print(f"项目分析任务已保存: task_id={analysis_task.id}")
        except Exception as e:
            print(f"保存项目分析任务失败: {e}")
        
        # 构建结果
        result = {
            'success': True,
            'type': 'project_analysis',
            'project_overview': project_overview,
            'ai_analysis': ai_result,
            'analysis_type': analysis_type,
            'model_used': model,
            'files_analyzed': len(important_files)
        }
        
        print(f"项目分析完成，返回结果")
        return jsonify(result)
        
    except Exception as e:
        print(f"项目分析失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
        if not data or not data.get('project_path'):
            return jsonify({
                'success': False,
                'error': 'Project path is required'
            }), 400
        
        project_path = data['project_path']
        project_id = data.get('project_id')
        
        # 使用Tree-sitter分析项目
        result = code_analysis_service.analyze_project(project_path)
        
        # 如果提供了项目ID，保存分析任务
        if project_id and result['success']:
            task = AnalysisTask(
                task_type='analyze',
                description='Full project analysis',
                input_data=json.dumps({
                    'project_path': project_path
                }),
                output_data=json.dumps(result),
                ai_model='tree-sitter',
                status='completed',
                completed_at=datetime.utcnow(),
                project_id=project_id
            )
            db.session.add(task)
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

