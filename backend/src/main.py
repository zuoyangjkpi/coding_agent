from gevent import monkey
monkey.patch_all()
# 以上两行代码必须放在文件的最前面，以确保正确的协作式多任务处理
import os
import sys
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from src.models.user import db
from src.routes.user import user_bp
from src.routes.project import project_bp
from src.routes.ai import ai_bp
from src.routes.github import github_bp
from src.routes.chat import chat_bp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# 启用CORS支持
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000')
CORS(app, origins=cors_origins.split(','), supports_credentials=True)

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins=cors_origins.split(','), async_mode='gevent')

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(project_bp, url_prefix='/api')
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(github_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')

# 数据库配置
database_path = '/home/ubuntu/coding_agent/backend/database/app.db'
database_url = os.getenv('DATABASE_URL', f"sqlite:///{database_path}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 导入所有模型以确保表被创建
from src.models.project import Project, AnalysisTask, CodeFile

# 健康检查端点
@app.route('/api/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'message': 'Coding Agent API is running',
        'version': '1.0.0'
    })

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

# 错误处理
@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f'Internal error: {str(error)}')
    return jsonify({'error': 'Internal server error'}), 500

# SocketIO事件处理
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('join_project')
def handle_join_project(data):
    """加入项目房间"""
    project_id = data.get('project_id')
    if project_id:
        from flask_socketio import join_room
        join_room(f'project_{project_id}')
        logger.info(f'Client joined project {project_id}')

@socketio.on('leave_project')
def handle_leave_project(data):
    """离开项目房间"""
    project_id = data.get('project_id')
    if project_id:
        from flask_socketio import leave_room
        leave_room(f'project_{project_id}')
        logger.info(f'Client left project {project_id}')

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
    # 确保必要的目录存在
    os.makedirs('/home/ubuntu/coding_agent/backend/database', exist_ok=True)
    os.makedirs('projects', exist_ok=True)
    
    # 暂时跳过数据库初始化，先让服务器运行起来
    # TODO: 修复数据库初始化问题
    print(f"Database path: {database_path}")
    print(f"Database URL: {database_url}")
    print("Skipping database initialization for now")
    
    # 运行数据库迁移
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'migrations'))
        from migrate import main as run_migrations
        run_migrations()
        logger.info('Database migrations completed')
    except Exception as e:
        logger.warning(f'Migration failed: {str(e)}')
    
    # 启动应用
    port = int(os.getenv('PORT', 5001))  # 使用5001端口避免冲突
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f'Starting Coding Agent on port {port}')
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
