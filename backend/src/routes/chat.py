from flask import Blueprint, request, jsonify
from src.services.ai_service import ai_service
from src.models.user import db
from src.models.project import Project, CodeFile
import json
import os
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/project/<int:project_id>', methods=['POST'])
def chat_with_project(project_id):
    """与项目进行聊天对话"""
    try:
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        project_id = project_id  # 从URL参数获取
        message = data['message']
        model = data.get('model')  # 如果没有指定，将使用智能选择
        conversation_history = data.get('history', [])
        
        print(f"项目聊天请求: project_id={project_id}, message={message[:100]}...")
        
        # 获取项目信息
        project = Project.query.get_or_404(project_id)
        
        # 获取项目的代码文件（用于上下文）
        code_files = CodeFile.query.filter_by(project_id=project_id).limit(10).all()
        
        # 构建项目上下文
        project_context = {
            'name': project.name,
            'description': project.description,
            'github_url': project.github_url,
            'files': []
        }
        
        for file in code_files:
            if file.content and len(file.content.strip()) > 0:
                project_context['files'].append({
                    'path': file.file_path,
                    'name': file.file_name,
                    'type': file.file_type,
                    'content': file.content[:1000] if len(file.content) > 1000 else file.content  # 限制内容长度
                })
        
        # 如果没有指定模型，根据消息内容智能选择
        if model is None:
            # 根据消息类型选择模型
            if any(keyword in message.lower() for keyword in ['代码', 'code', '编程', 'programming', '函数', 'function', '类', 'class']):
                model = ai_service.get_optimal_model('coding', len(message))
            elif any(keyword in message.lower() for keyword in ['分析', 'analyze', '推理', 'reasoning', '逻辑', 'logic']):
                model = ai_service.get_optimal_model('reasoning', len(message))
            else:
                # 考虑项目上下文的大小
                context_size = sum(len(f['content']) for f in project_context['files'])
                model = ai_service.get_optimal_model('large_context' if context_size > 10000 else 'coding', context_size)
        
        # 构建聊天提示
        system_prompt = f"""
你是一个专业的编程助手，正在帮助用户处理项目 "{project_context['name']}"。

项目信息：
- 名称：{project_context['name']}
- 描述：{project_context['description']}
- GitHub URL：{project_context['github_url']}

项目文件结构：
"""
        
        for file in project_context['files']:
            system_prompt += f"\n文件：{file['path']} ({file['type']})\n```\n{file['content']}\n```\n"
        
        system_prompt += """

请基于以上项目信息回答用户的问题。你可以：
1. 分析和解释代码
2. 提供编程建议和最佳实践
3. 帮助调试问题
4. 建议代码改进
5. 回答关于项目架构的问题

请保持专业、准确和有帮助。
"""
        
        # 构建对话历史
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话
        for msg in conversation_history[-10:]:  # 只保留最近10条对话
            messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": message})
        
        # 调用AI模型
        try:
            # 构建完整的提示
            full_prompt = system_prompt + "\n\n用户问题：" + message
            response = ai_service._call_model(model, full_prompt)
            
            result = {
                'success': True,
                'response': response,
                'model_used': model,
                'project_id': project_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            print(f"聊天响应完成，使用模型: {model}")
            return jsonify(result)
            
        except Exception as e:
            print(f"AI模型调用失败: {e}")
            return jsonify({
                'success': False,
                'error': f'AI model error: {str(e)}'
            }), 500
        
    except Exception as e:
        print(f"项目聊天失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/general', methods=['POST'])
def general_chat():
    """通用聊天（不绑定特定项目）"""
    try:
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        message = data['message']
        model = data.get('model')
        conversation_history = data.get('history', [])
        
        print(f"通用聊天请求: message={message[:100]}...")
        
        # 如果没有指定模型，根据消息内容智能选择
        if model is None:
            if any(keyword in message.lower() for keyword in ['代码', 'code', '编程', 'programming']):
                model = ai_service.get_optimal_model('coding', len(message))
            elif any(keyword in message.lower() for keyword in ['分析', 'analyze', '推理', 'reasoning']):
                model = ai_service.get_optimal_model('reasoning', len(message))
            else:
                model = ai_service.get_optimal_model('coding', len(message))  # 默认使用编程模型
        
        # 构建系统提示
        system_prompt = """
你是一个专业的编程助手，擅长：
1. 代码分析和生成
2. 编程问题解答
3. 技术架构建议
4. 调试和优化建议
5. 最佳实践指导

请保持专业、准确和有帮助。
"""
        
        # 构建完整的提示
        full_prompt = system_prompt + "\n\n用户问题：" + message
        
        # 如果有对话历史，添加上下文
        if conversation_history:
            context = "\n\n对话历史：\n"
            for msg in conversation_history[-5:]:  # 只保留最近5条对话
                role = "用户" if msg.get('role') == 'user' else "助手"
                context += f"{role}: {msg.get('content', '')}\n"
            full_prompt = system_prompt + context + "\n\n当前问题：" + message
        
        # 调用AI模型
        try:
            response = ai_service._call_model(model, full_prompt)
            
            result = {
                'success': True,
                'response': response,
                'model_used': model,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            print(f"通用聊天响应完成，使用模型: {model}")
            return jsonify(result)
            
        except Exception as e:
            print(f"AI模型调用失败: {e}")
            return jsonify({
                'success': False,
                'error': f'AI model error: {str(e)}'
            }), 500
        
    except Exception as e:
        print(f"通用聊天失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/models', methods=['GET'])
def get_chat_models():
    """获取可用于聊天的AI模型"""
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

