#!/usr/bin/env python3
"""
验证模型语法
Validate Model Syntax
"""
import ast
import os

def validate_python_file(filepath):
    """
    验证Python文件语法
    
    Args:
        filepath (str): 文件路径
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析AST
        ast.parse(content)
        return True, ""
    
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """主函数"""
    model_files = [
        'app/models/user.py',
        'app/models/admin.py',
        'app/models/category.py',
        'app/models/article.py',
        'app/models/comment.py'
    ]
    
    print("Validating model files...")
    all_valid = True
    
    for filepath in model_files:
        if os.path.exists(filepath):
            is_valid, error = validate_python_file(filepath)
            if is_valid:
                print(f"✓ {filepath} - Syntax OK")
            else:
                print(f"✗ {filepath} - {error}")
                all_valid = False
        else:
            print(f"✗ {filepath} - File not found")
            all_valid = False
    
    if all_valid:
        print("\n✓ All model files have valid syntax!")
        return 0
    else:
        print("\n✗ Some model files have syntax errors!")
        return 1

if __name__ == '__main__':
    exit(main())