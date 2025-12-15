#!/usr/bin/env python3
"""
测试模型导入
Test Model Imports
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing model imports...")
    
    # 测试基本导入
    from app.models.user import User
    print("✓ User model imported successfully")
    
    from app.models.admin import Admin
    print("✓ Admin model imported successfully")
    
    from app.models.category import Category
    print("✓ Category model imported successfully")
    
    from app.models.article import Article
    print("✓ Article model imported successfully")
    
    from app.models.comment import Comment
    print("✓ Comment model imported successfully")
    
    # 测试统一导入
    from app.models import User, Admin, Category, Article, Comment
    print("✓ All models imported from package successfully")
    
    print("\nAll model imports successful!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)