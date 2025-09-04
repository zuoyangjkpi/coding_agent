import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from src.models.user import db
from src.routes.user import user_bp
from src.routes.project import project_bp
from src.routes.ai import ai_bp
from src.routes.github import github_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# 启用CORS支持
CORS(app, origins="*")

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(project_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(github_bp, url_prefix='/api')

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 导入所有模型以确保表被创建
from src.models.project import Project, AnalysisTask, CodeFile

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# SocketIO事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_project')
def handle_join_project(data):
    """加入项目房间"""
    project_id = data.get('project_id')
    if project_id:
        from flask_socketio import join_room
        join_room(f'project_{project_id}')
        print(f'Client joined project {project_id}')

@socketio.on('leave_project')
def handle_leave_project(data):
    """离开项目房间"""
    project_id = data.get('project_id')
    if project_id:
        from flask_socketio import leave_room
        leave_room(f'project_{project_id}')
        print(f'Client left project {project_id}')

@socketio.on('analysis_progress')
def handle_analysis_progress(data):
    """处理分析进度更新"""
    project_id = data.get('project_id')
    progress = data.get('progress', 0)
    message = data.get('message', '')
    
    if project_id:
        from flask_socketio import emit
        emit('analysis_update', {
            'progress': progress,
            'message': message
        }, room=f'project_{project_id}')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
