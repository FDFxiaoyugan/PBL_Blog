#!/usr/bin/env python3
"""
数据库初始化脚本
Database Initialization Script
"""
import os
import sys
from flask import Flask
from app import create_app, db

def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # 删除所有表（如果存在）
            print("正在删除现有数据库表...")
            db.drop_all()
            
            # 创建所有表
            print("正在创建数据库表...")
            db.create_all()
            
            print("数据库初始化完成！")
            return True
            
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            return False

def create_test_data():
    """创建测试数据"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # 导入模型
            from app.models import User, Admin, Category, Article, Comment
            
            # 创建测试分类
            categories = [
                Category(name='技术', description='技术相关文章', slug='tech'),
                Category(name='生活', description='生活感悟', slug='life'),
                Category(name='学习', description='学习笔记', slug='study')
            ]
            
            for category in categories:
                db.session.add(category)
            
            # 创建测试用户
            from werkzeug.security import generate_password_hash
            
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                nickname='测试用户'
            )
            db.session.add(test_user)
            
            # 创建管理员用户
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                nickname='管理员'
            )
            db.session.add(admin_user)
            
            db.session.commit()
            
            # 创建管理员权限
            admin = Admin(user_id=admin_user.id, role='admin')
            db.session.add(admin)
            
            db.session.commit()
            
            print("测试数据创建完成！")
            print("测试用户: testuser / password123")
            print("管理员: admin / admin123")
            
        except Exception as e:
            print(f"测试数据创建失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--with-data':
        if init_database():
            create_test_data()
    else:
        init_database()