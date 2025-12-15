#!/usr/bin/env python3
"""
验证模型结构
Verify Model Structure
"""
import ast
import os

def analyze_model_file(filepath):
    """
    分析模型文件结构
    
    Args:
        filepath (str): 文件路径
        
    Returns:
        dict: 分析结果
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    classes = []
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(item.name)
            classes.append({
                'name': node.name,
                'methods': methods
            })
        elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
            functions.append(node.name)
    
    return {
        'classes': classes,
        'functions': functions
    }

def verify_user_model():
    """验证用户模型"""
    print("Verifying User model...")
    result = analyze_model_file('app/models/user.py')
    
    user_class = next((c for c in result['classes'] if c['name'] == 'User'), None)
    if not user_class:
        print("✗ User class not found")
        return False
    
    required_methods = [
        '__init__', 'set_password', 'check_password', 'is_admin',
        'validate_username', 'validate_email', 'validate_password'
    ]
    
    missing_methods = [m for m in required_methods if m not in user_class['methods']]
    if missing_methods:
        print(f"✗ Missing methods: {missing_methods}")
        return False
    
    print("✓ User model structure OK")
    return True

def verify_admin_model():
    """验证管理员模型"""
    print("Verifying Admin model...")
    result = analyze_model_file('app/models/admin.py')
    
    admin_class = next((c for c in result['classes'] if c['name'] == 'Admin'), None)
    if not admin_class:
        print("✗ Admin class not found")
        return False
    
    required_methods = [
        '__init__', 'get_permissions', 'set_permissions', 'has_permission',
        'can_manage_users', 'can_manage_articles', 'can_manage_comments'
    ]
    
    missing_methods = [m for m in required_methods if m not in admin_class['methods']]
    if missing_methods:
        print(f"✗ Missing methods: {missing_methods}")
        return False
    
    print("✓ Admin model structure OK")
    return True

def verify_category_model():
    """验证分类模型"""
    print("Verifying Category model...")
    result = analyze_model_file('app/models/category.py')
    
    category_class = next((c for c in result['classes'] if c['name'] == 'Category'), None)
    if not category_class:
        print("✗ Category class not found")
        return False
    
    required_methods = [
        '__init__', 'generate_slug', 'get_article_count',
        'validate_name', 'validate_slug'
    ]
    
    missing_methods = [m for m in required_methods if m not in category_class['methods']]
    if missing_methods:
        print(f"✗ Missing methods: {missing_methods}")
        return False
    
    print("✓ Category model structure OK")
    return True

def verify_article_model():
    """验证文章模型"""
    print("Verifying Article model...")
    result = analyze_model_file('app/models/article.py')
    
    article_class = next((c for c in result['classes'] if c['name'] == 'Article'), None)
    if not article_class:
        print("✗ Article class not found")
        return False
    
    required_methods = [
        '__init__', 'publish', 'unpublish', 'can_edit', 'can_delete',
        'validate_title', 'validate_content', 'search'
    ]
    
    missing_methods = [m for m in required_methods if m not in article_class['methods']]
    if missing_methods:
        print(f"✗ Missing methods: {missing_methods}")
        return False
    
    print("✓ Article model structure OK")
    return True

def verify_comment_model():
    """验证评论模型"""
    print("Verifying Comment model...")
    result = analyze_model_file('app/models/comment.py')
    
    comment_class = next((c for c in result['classes'] if c['name'] == 'Comment'), None)
    if not comment_class:
        print("✗ Comment class not found")
        return False
    
    required_methods = [
        '__init__', 'approve', 'reject', 'can_edit', 'can_delete',
        'validate_content', 'get_article_comments'
    ]
    
    missing_methods = [m for m in required_methods if m not in comment_class['methods']]
    if missing_methods:
        print(f"✗ Missing methods: {missing_methods}")
        return False
    
    print("✓ Comment model structure OK")
    return True

def main():
    """主函数"""
    print("Verifying model structures...\n")
    
    success = True
    success &= verify_user_model()
    success &= verify_admin_model()
    success &= verify_category_model()
    success &= verify_article_model()
    success &= verify_comment_model()
    
    if success:
        print("\n✓ All model structures verified successfully!")
        print("\nModel Summary:")
        print("- User: Authentication, validation, relationships")
        print("- Admin: Permissions, role management")
        print("- Category: Article categorization, slug generation")
        print("- Article: Content management, status handling, search")
        print("- Comment: Threaded comments, moderation")
        return 0
    else:
        print("\n✗ Some model structures have issues!")
        return 1

if __name__ == '__main__':
    exit(main())