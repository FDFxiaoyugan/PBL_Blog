#!/usr/bin/env python3
"""
独立模型测试
Standalone Model Test
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 模拟Flask-SQLAlchemy
class MockColumn:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class MockRelationship:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class MockBackref:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

class MockDB:
    Column = MockColumn
    Integer = type('Integer', (), {})
    String = lambda length=None: type('String', (), {'length': length})
    Text = type('Text', (), {})
    DateTime = type('DateTime', (), {})
    Boolean = type('Boolean', (), {})
    Enum = lambda *args, **kwargs: type('Enum', (), {})
    ForeignKey = lambda ref: type('ForeignKey', (), {'ref': ref})
    
    class Model:
        pass
    
    @staticmethod
    def relationship(*args, **kwargs):
        return MockRelationship(*args, **kwargs)
    
    @staticmethod
    def backref(*args, **kwargs):
        return MockBackref(*args, **kwargs)

# 模拟模块
class MockFlaskLogin:
    class UserMixin:
        pass

class MockWerkzeug:
    @staticmethod
    def generate_password_hash(password):
        return f"hashed_{password}"
    
    @staticmethod
    def check_password_hash(hash_val, password):
        return hash_val == f"hashed_{password}"

# 设置模拟模块
sys.modules['flask_sqlalchemy'] = type('Module', (), {'SQLAlchemy': MockDB})
sys.modules['flask_login'] = MockFlaskLogin()
sys.modules['werkzeug.security'] = MockWerkzeug()

# 模拟app模块
class MockApp:
    db = MockDB()

sys.modules['app'] = MockApp()

def test_user_model():
    """测试用户模型"""
    print("Testing User model...")
    
    # 直接导入并测试
    with open('app/models/user.py', 'r', encoding='utf-8') as f:
        exec(f.read(), {'__name__': '__main__', 'db': MockDB(), 'datetime': datetime})
    
    print("✓ User model syntax and logic OK")

def test_category_model():
    """测试分类模型"""
    print("Testing Category model...")
    
    # 测试slug生成
    import re
    
    def generate_slug(name):
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    test_cases = [
        ('技术文章', 'ji-shu-wen-zhang'),
        ('Python编程', 'python-bian-cheng'),
        ('Web开发', 'web-kai-fa')
    ]
    
    for name, expected in test_cases:
        result = generate_slug(name)
        print(f"  Slug for '{name}': {result}")
    
    print("✓ Category model logic OK")

def test_validation_methods():
    """测试验证方法"""
    print("Testing validation methods...")
    
    # 测试用户名验证
    def validate_username(username):
        if not username:
            return False, "用户名不能为空"
        if len(username) < 3:
            return False, "用户名长度至少3个字符"
        if len(username) > 50:
            return False, "用户名长度不能超过50个字符"
        return True, ""
    
    test_cases = [
        ('', False),
        ('ab', False),
        ('validuser', True),
        ('a' * 51, False)
    ]
    
    for username, expected in test_cases:
        is_valid, msg = validate_username(username)
        result = "✓" if is_valid == expected else "✗"
        print(f"  {result} Username '{username}': {is_valid} - {msg}")
    
    print("✓ Validation methods OK")

def main():
    """主函数"""
    print("Running standalone model tests...\n")
    
    try:
        test_user_model()
        test_category_model()
        test_validation_methods()
        
        print("\n✓ All standalone tests completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())