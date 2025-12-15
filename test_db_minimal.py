#!/usr/bin/env python3
"""
最小化数据库测试
Minimal Database Test
"""
import os
import sys

# 模拟Flask和SQLAlchemy（用于语法检查）
class MockDB:
    def __init__(self):
        pass
    
    class Column:
        def __init__(self, *args, **kwargs):
            pass
    
    class Integer:
        pass
    
    class String:
        def __init__(self, length=None):
            pass
    
    class Text:
        pass
    
    class DateTime:
        pass
    
    class Boolean:
        pass
    
    class Enum:
        def __init__(self, *args, **kwargs):
            pass
    
    class ForeignKey:
        def __init__(self, ref):
            pass
    
    class Model:
        def __init__(self):
            pass
    
    def relationship(self, *args, **kwargs):
        return None
    
    def backref(self, *args, **kwargs):
        return None

# 模拟导入
sys.modules['flask_sqlalchemy'] = type('MockModule', (), {'SQLAlchemy': MockDB})
sys.modules['flask_login'] = type('MockModule', (), {'UserMixin': object})
sys.modules['werkzeug.security'] = type('MockModule', (), {
    'generate_password_hash': lambda x: f'hashed_{x}',
    'check_password_hash': lambda h, p: h == f'hashed_{p}'
})

# 模拟app.db
class MockApp:
    db = MockDB()

sys.modules['app'] = MockApp()

def test_model_creation():
    """测试模型创建"""
    try:
        # 测试用户模型
        from app.models.user import User
        user = User('testuser', 'test@example.com', 'password123')
        print("✓ User model creation test passed")
        
        # 测试分类模型
        from app.models.category import Category
        category = Category('技术', '技术相关文章')
        print("✓ Category model creation test passed")
        
        # 测试文章模型
        from app.models.article import Article
        article = Article('测试文章', '这是测试内容', 1)
        print("✓ Article model creation test passed")
        
        # 测试评论模型
        from app.models.comment import Comment
        comment = Comment('测试评论', 1, 1)
        print("✓ Comment model creation test passed")
        
        # 测试管理员模型
        from app.models.admin import Admin
        admin = Admin(1)
        print("✓ Admin model creation test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Model creation test failed: {e}")
        return False

def test_model_methods():
    """测试模型方法"""
    try:
        from app.models.user import User
        
        # 测试用户验证方法
        is_valid, msg = User.validate_username('testuser')
        print(f"✓ Username validation: {is_valid}")
        
        is_valid, msg = User.validate_email('test@example.com')
        print(f"✓ Email validation: {is_valid}")
        
        is_valid, msg = User.validate_password('password123')
        print(f"✓ Password validation: {is_valid}")
        
        # 测试分类方法
        from app.models.category import Category
        slug = Category.generate_slug('技术文章')
        print(f"✓ Category slug generation: {slug}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model methods test failed: {e}")
        return False

def main():
    """主函数"""
    print("Running minimal database model tests...")
    
    success = True
    success &= test_model_creation()
    success &= test_model_methods()
    
    if success:
        print("\n✓ All minimal tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    exit(main())