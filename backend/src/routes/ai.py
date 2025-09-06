from flask import Blueprint, request, jsonify
from src.services.ai_service import ai_service
from src.services.code_analysis_service import code_analysis_service
from src.models.user import db
from src.models.project import AnalysisTask, CodeFile
import json
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

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
        model = data.get('model', 'deepseek-r1')
        project_id = data.get('project_id')
        
        print(f"分析代码请求: file_type={file_type}, model={model}, project_id={project_id}")
        
        # AI分析
        ai_result = ai_service.analyze_code(code, file_type, model)
        
        # Tree-sitter分析
        ts_result = code_analysis_service.analyze_file('temp_file.' + file_type, code)
        
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
            task = AnalysisTask(
                task_type='analyze',
                description=f'Code analysis using {model}',
                input_data=json.dumps({
                    'code': code[:1000] + '...' if len(code) > 1000 else code,
                    'file_type': file_type
                }),
                output_data=json.dumps({
                    'ai_analysis': ai_result,
                    'syntax_analysis': ts_result
                }),
                ai_model=model,
                status='completed',
                completed_at=datetime.utcnow(),
                project_id=project_id
            )
            db.session.add(task)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'ai_analysis': ai_result,
            'syntax_analysis': ts_result,
            'model_used': model
        })
        
    except Exception as e:
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
        model = data.get('model', 'deepseek-r1')
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
        model = data.get('model', 'deepseek-r1')
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
        model = data.get('model', 'deepseek-r1')
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
        model = data.get('model', 'deepseek-r1')
        
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

