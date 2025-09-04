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
        
        # AI分析
        ai_result = ai_service.analyze_code(code, file_type, model)
        
        # Tree-sitter分析
        ts_result = code_analysis_service.analyze_file('temp_file.' + file_type, code)
        
        # 如果提供了项目ID，保存分析任务
        if project_id:
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
        
        # 代码审查
        result = ai_service.review_code(code, file_type, model)
        
        # 如果提供了项目ID，保存分析任务
        if project_id and result['success']:
            task = AnalysisTask(
                task_type='review',
                description=f'Code review using {model}',
                input_data=json.dumps({
                    'code': code[:1000] + '...' if len(code) > 1000 else code,
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

@ai_bp.route('/ai/analyze-project', methods=['POST'])
def analyze_project():
    """分析整个项目"""
    try:
        data = request.get_json()
        
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

