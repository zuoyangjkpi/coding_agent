from datetime import datetime
from src.models.user import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    github_url = db.Column(db.String(500))
    local_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='created')  # created, cloning, analyzing, ready, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 关联关系
    analysis_tasks = db.relationship('AnalysisTask', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'github_url': self.github_url,
            'local_path': self.local_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }

class AnalysisTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(50), nullable=False)  # analyze, modify, generate, review
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    input_data = db.Column(db.Text)  # JSON格式的输入数据
    output_data = db.Column(db.Text)  # JSON格式的输出数据
    ai_model = db.Column(db.String(50))  # 使用的AI模型
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    def __repr__(self):
        return f'<AnalysisTask {self.task_type}:{self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'description': self.description,
            'file_path': self.file_path,
            'status': self.status,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'ai_model': self.ai_model,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'project_id': self.project_id
        }

class CodeFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50))  # python, javascript, etc.
    content = db.Column(db.Text)
    size = db.Column(db.Integer)
    last_modified = db.Column(db.DateTime)
    analysis_result = db.Column(db.Text)  # JSON格式的分析结果
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    def __repr__(self):
        return f'<CodeFile {self.file_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'content': self.content,
            'size': self.size,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'analysis_result': self.analysis_result,
            'project_id': self.project_id
        }

