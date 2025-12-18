"""
测试前端模板渲染
Test Frontend Template Rendering
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_template_files_exist():
    """测试所有模板文件是否存在"""
    
    templates_dir = 'app/templates'
    
    # 必需的模板文件列表
    required_templates = [
        # 基础模板
        'base.html',
        
        # 认证模板
        'auth/login.html',
        'auth/register.html',
        
        # 主页面模板
        'main/index.html',
        'main/profile.html',
        'main/edit_profile.html',
        'main/change_password.html',
        
        # 文章模板
        'article/list.html',
        'article/detail.html',
        'article/create.html',
        'article/edit.html',
        'article/my_articles.html',
        
        # 评论模板
        'comment/_comment_list.html',
        'comment/my_comments.html',
        
        # 管理员模板
        'admin/dashboard.html',
        'admin/users.html',
        'admin/user_detail.html',
        'admin/edit_user.html',
        'admin/articles.html',
        'admin/comments.html',
        'admin/edit_comment.html',
        
        # 错误页面
        'errors/403.html',
        'errors/404.html',
    ]
    
    print("检查模板文件...")
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if not os.path.exists(template_path):
            missing_templates.append(template)
            print(f"❌ 缺失: {template}")
        else:
            print(f"✅ 存在: {template}")
    
    if missing_templates:
        print(f"\n❌ 发现 {len(missing_templates)} 个缺失的模板文件")
        return False
    else:
        print(f"\n✅ 所有 {len(required_templates)} 个模板文件都存在")
        return True

def test_static_files_exist():
    """测试静态文件是否存在"""
    
    static_files = [
        'app/static/css/style.css',
        'app/static/js/main.js',
    ]
    
    print("\n检查静态文件...")
    missing_files = []
    
    for file_path in static_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"❌ 缺失: {file_path}")
        else:
            print(f"✅ 存在: {file_path}")
    
    if missing_files:
        print(f"\n❌ 发现 {len(missing_files)} 个缺失的静态文件")
        return False
    else:
        print(f"\n✅ 所有 {len(static_files)} 个静态文件都存在")
        return True

def test_base_template_structure():
    """测试基础模板结构"""
    
    print("\n检查基础模板结构...")
    base_template_path = 'app/templates/base.html'
    
    if not os.path.exists(base_template_path):
        print("❌ 基础模板不存在")
        return False
    
    with open(base_template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需的元素
    required_elements = [
        'bootstrap',  # Bootstrap CSS
        'font-awesome',  # 图标库
        'navbar',  # 导航栏
        'container',  # 容器
        'block content',  # 内容块
        'footer',  # 页脚
        'style.css',  # 自定义CSS
        'main.js',  # 自定义JS
    ]
    
    missing_elements = []
    for element in required_elements:
        if element.lower() not in content.lower():
            missing_elements.append(element)
            print(f"❌ 缺失元素: {element}")
        else:
            print(f"✅ 包含元素: {element}")
    
    if missing_elements:
        print(f"\n❌ 基础模板缺少 {len(missing_elements)} 个必需元素")
        return False
    else:
        print(f"\n✅ 基础模板包含所有必需元素")
        return True

def test_css_file_content():
    """测试CSS文件内容"""
    
    print("\n检查CSS文件内容...")
    css_file_path = 'app/static/css/style.css'
    
    if not os.path.exists(css_file_path):
        print("❌ CSS文件不存在")
        return False
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键样式类
    required_styles = [
        '.card',
        '.article-content',
        '.comment',
        '.navbar',
        '@media',  # 响应式设计
    ]
    
    missing_styles = []
    for style in required_styles:
        if style not in content:
            missing_styles.append(style)
            print(f"❌ 缺失样式: {style}")
        else:
            print(f"✅ 包含样式: {style}")
    
    if missing_styles:
        print(f"\n❌ CSS文件缺少 {len(missing_styles)} 个关键样式")
        return False
    else:
        print(f"\n✅ CSS文件包含所有关键样式")
        return True

def test_js_file_content():
    """测试JavaScript文件内容"""
    
    print("\n检查JavaScript文件内容...")
    js_file_path = 'app/static/js/main.js'
    
    if not os.path.exists(js_file_path):
        print("❌ JavaScript文件不存在")
        return False
    
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键功能
    required_functions = [
        'initTooltips',
        'initAlertAutoClose',
        'initFormValidation',
        'initBackToTop',
        'showToast',
        'ajaxRequest',
    ]
    
    missing_functions = []
    for func in required_functions:
        if func not in content:
            missing_functions.append(func)
            print(f"❌ 缺失函数: {func}")
        else:
            print(f"✅ 包含函数: {func}")
    
    if missing_functions:
        print(f"\n❌ JavaScript文件缺少 {len(missing_functions)} 个关键函数")
        return False
    else:
        print(f"\n✅ JavaScript文件包含所有关键函数")
        return True

def main():
    """运行所有测试"""
    
    print("=" * 60)
    print("前端模板验证测试")
    print("=" * 60)
    
    tests = [
        ("模板文件存在性", test_template_files_exist),
        ("静态文件存在性", test_static_files_exist),
        ("基础模板结构", test_base_template_structure),
        ("CSS文件内容", test_css_file_content),
        ("JavaScript文件内容", test_js_file_content),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 执行失败: {str(e)}")
            results.append((test_name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有前端模板验证测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
