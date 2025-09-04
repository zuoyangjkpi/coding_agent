#!/usr/bin/env python3
"""
数据库迁移工具
用于管理数据库schema的版本控制和迁移
"""

import os
import sqlite3
import sys
from pathlib import Path

def get_db_connection(db_path):
    """获取数据库连接"""
    return sqlite3.connect(db_path)

def create_migration_table(conn):
    """创建迁移记录表"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def get_applied_migrations(conn):
    """获取已应用的迁移"""
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM migrations ORDER BY id')
    return [row[0] for row in cursor.fetchall()]

def get_pending_migrations(migrations_dir, applied_migrations):
    """获取待应用的迁移"""
    migration_files = []
    for file in sorted(os.listdir(migrations_dir)):
        if file.endswith('.sql') and file not in applied_migrations:
            migration_files.append(file)
    return migration_files

def apply_migration(conn, migration_file, migrations_dir):
    """应用单个迁移"""
    migration_path = os.path.join(migrations_dir, migration_file)
    
    print(f"Applying migration: {migration_file}")
    
    with open(migration_path, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    cursor = conn.cursor()
    try:
        # 执行迁移SQL
        cursor.executescript(migration_sql)
        
        # 记录迁移
        cursor.execute(
            'INSERT INTO migrations (filename) VALUES (?)',
            (migration_file,)
        )
        
        conn.commit()
        print(f"✓ Successfully applied: {migration_file}")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Failed to apply {migration_file}: {str(e)}")
        raise

def main():
    """主函数"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    migrations_dir = os.path.join(project_root, 'migrations')
    db_path = os.path.join(project_root, 'src', 'database', 'app.db')
    
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接数据库
    conn = get_db_connection(db_path)
    
    try:
        # 创建迁移记录表
        create_migration_table(conn)
        
        # 获取已应用和待应用的迁移
        applied_migrations = get_applied_migrations(conn)
        pending_migrations = get_pending_migrations(migrations_dir, applied_migrations)
        
        if not pending_migrations:
            print("No pending migrations.")
            return
        
        print(f"Found {len(pending_migrations)} pending migrations:")
        for migration in pending_migrations:
            print(f"  - {migration}")
        
        # 确认是否继续
        if len(sys.argv) > 1 and sys.argv[1] == '--auto':
            proceed = True
        else:
            response = input("\nProceed with migrations? (y/N): ")
            proceed = response.lower() in ['y', 'yes']
        
        if not proceed:
            print("Migration cancelled.")
            return
        
        # 应用迁移
        for migration in pending_migrations:
            apply_migration(conn, migration, migrations_dir)
        
        print(f"\n✓ Successfully applied {len(pending_migrations)} migrations.")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        sys.exit(1)
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()

