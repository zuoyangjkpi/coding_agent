from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.project import Project, AnalysisTask, CodeFile
import os
import json

project_bp = Blueprint('project', __name__)

@project_bp.route('/projects', methods=['GET'])
def get_projects():
    """获取所有项目列表"""
    try:
        projects = Project.query.all()
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@project_bp.route('/projects', methods=['POST'])
def create_project():
    """创建新项目"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Project name is required'
            }), 400
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            github_url=data.get('github_url', ''),
            user_id=data.get('user_id', 1)  # 暂时使用默认用户ID
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@project_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取单个项目详情"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # 获取项目的代码文件
        code_files = CodeFile.query.filter_by(project_id=project_id).all()
        
        # 获取项目的分析任务
        analysis_tasks = AnalysisTask.query.filter_by(project_id=project_id).all()
        
        project_data = project.to_dict()
        project_data['code_files'] = [file.to_dict() for file in code_files]
        project_data['analysis_tasks'] = [task.to_dict() for task in analysis_tasks]
        
        return jsonify({
            'success': True,
            'project': project_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@project_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目信息"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        if data.get('name'):
            project.name = data['name']
        if data.get('description'):
            project.description = data['description']
        if data.get('github_url'):
            project.github_url = data['github_url']
        if data.get('status'):
            project.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    try:
        print(f"尝试删除项目 ID: {project_id}")  # 调试日志
        
        project = Project.query.get_or_404(project_id)
        print(f"找到项目: {project.name} (ID: {project.id})")  # 调试日志
        
        # 删除关联的代码文件记录
        code_files = CodeFile.query.filter_by(project_id=project_id).all()
        for code_file in code_files:
            db.session.delete(code_file)
        print(f"删除了 {len(code_files)} 个代码文件记录")  # 调试日志
        
        # 删除关联的分析任务
        analysis_tasks = AnalysisTask.query.filter_by(project_id=project_id).all()
        for task in analysis_tasks:
            db.session.delete(task)
        print(f"删除了 {len(analysis_tasks)} 个分析任务")  # 调试日志
        
        # 删除本地文件夹（如果存在）
        if project.local_path and os.path.exists(project.local_path):
            import shutil
            shutil.rmtree(project.local_path)
            print(f"删除了本地文件夹: {project.local_path}")  # 调试日志
        
        # 删除项目记录
        db.session.delete(project)
        db.session.commit()
        
        print(f"项目 {project_id} 删除成功")  # 调试日志
        
        return jsonify({
            'success': True,
            'message': 'Project deleted successfully',
            'deleted_project_id': project_id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"删除项目失败: {str(e)}")  # 调试日志
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@project_bp.route('/projects/<int:project_id>/tasks', methods=['POST'])
def create_analysis_task(project_id):
    """创建分析任务"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        if not data or not data.get('task_type'):
            return jsonify({
                'success': False,
                'error': 'Task type is required'
            }), 400
        
        task = AnalysisTask(
            task_type=data['task_type'],
            description=data.get('description', ''),
            file_path=data.get('file_path', ''),
            input_data=json.dumps(data.get('input_data', {})),
            ai_model=data.get('ai_model', 'deepseek-r1'),
            project_id=project_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@project_bp.route('/projects/<int:project_id>/files', methods=['GET'])
def get_project_files(project_id):
    """获取项目文件列表"""
    try:
        project = Project.query.get_or_404(project_id)
        code_files = CodeFile.query.filter_by(project_id=project_id).all()
        
        return jsonify({
            'success': True,
            'files': [file.to_dict() for file in code_files]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

