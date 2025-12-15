#!/usr/bin/env python3
"""
评论系统实现验证脚本
Comment System Implementation Validation Script
"""

def test_comment_model_import():
    """测试评论模型导入"""
    try:
        from app.models.comment import Comment
        print("✓ Comment model imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Comment model: {e}")
        return False

def test_comment_forms_import():
    """测试评论表单导入"""
    try:
        from app.forms.comment import CommentForm, CommentReplyForm, CommentDeleteForm
        print("✓ Comment forms imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Comment forms: {e}")
        return False

def test_comment_routes_import():
    """测试评论路由导入"""
    try:
        from app.routes.comment import comment_bp
        print("✓ Comment routes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Comment routes: {e}")
        return False

def test_comment_validation():
    """测试评论验证功能"""
    try:
        from app.models.comment import Comment
        
        # 测试有效评论
        is_valid, msg = Comment.validate_content("This is a valid comment")
        if is_valid:
            print("✓ Valid comment validation works")
        else:
            print(f"✗ Valid comment validation failed: {msg}")
            return False
        
        # 测试空评论
        is_valid, msg = Comment.validate_content("")
        if not is_valid and "不能为空" in msg:
            print("✓ Empty comment validation works")
        else:
            print(f"✗ Empty comment validation failed: {is_valid}, {msg}")
            return False
        
        # 测试过长评论
        long_comment = "x" * 1001
        is_valid, msg = Comment.validate_content(long_comment)
        if not is_valid and "长度" in msg:
            print("✓ Long comment validation works")
        else:
            print(f"✗ Long comment validation failed: {is_valid}, {msg}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Comment validation test failed: {e}")
        return False

def test_template_files():
    """测试模板文件存在"""
    import os
    
    templates = [
        "app/templates/comment/my_comments.html",
        "app/templates/comment/_comment_list.html",
        "app/templates/admin/comments.html"
    ]
    
    all_exist = True
    for template in templates:
        if os.path.exists(template):
            print(f"✓ Template exists: {template}")
        else:
            print(f"✗ Template missing: {template}")
            all_exist = False
    
    return all_exist

def test_route_registration():
    """测试路由注册"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath('.'))
        
        # 检查 __init__.py 中是否包含评论蓝图注册
        with open('app/__init__.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'comment_bp' in content and 'register_blueprint(comment_bp)' in content:
                print("✓ Comment blueprint registered in __init__.py")
                return True
            else:
                print("✗ Comment blueprint not properly registered")
                return False
    except Exception as e:
        print(f"✗ Route registration test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("评论系统实现验证")
    print("=" * 50)
    
    tests = [
        test_comment_model_import,
        test_comment_forms_import,
        test_comment_routes_import,
        test_comment_validation,
        test_template_files,
        test_route_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！评论系统实现完成。")
        return True
    else:
        print("✗ 部分测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    main()