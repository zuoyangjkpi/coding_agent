import os
import sys

# 模拟main.py中的路径计算
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 计算数据库路径
current_file = os.path.abspath(__file__)
print(f"Current file: {current_file}")

src_dir = os.path.dirname(current_file)
print(f"Src dir: {src_dir}")

backend_dir = os.path.dirname(src_dir)
print(f"Backend dir: {backend_dir}")

database_dir = os.path.join(backend_dir, 'database')
print(f"Database dir: {database_dir}")

database_file = os.path.join(database_dir, 'app.db')
print(f"Database file: {database_file}")

database_url = f"sqlite:///{database_file}"
print(f"Database URL: {database_url}")

# 检查目录是否存在
print(f"Database dir exists: {os.path.exists(database_dir)}")
print(f"Database dir is writable: {os.access(database_dir, os.W_OK) if os.path.exists(database_dir) else 'N/A'}")

# 尝试创建目录
try:
    os.makedirs(database_dir, exist_ok=True)
    print("Successfully created database directory")
except Exception as e:
    print(f"Failed to create database directory: {e}")

# 尝试创建数据库文件
try:
    import sqlite3
    conn = sqlite3.connect(database_file)
    conn.close()
    print("Successfully created database file")
except Exception as e:
    print(f"Failed to create database file: {e}")

