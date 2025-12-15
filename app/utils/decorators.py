"""
权限控制装饰器
Permission Control Decorators
"""
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """
    管理员权限验证装饰器
    
    实现需求:
    - 5.5: 普通用户尝试访问管理功能时拒绝访问并显示权限不足提示
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录以访问此页面。', 'info')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('您没有权限访问此页面。', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def owner_required(model_class, id_param='id', user_field='author_id'):
    """
    资源所有者权限验证装饰器
    
    实现需求:
    - 4.5: 未登录用户尝试评论时重定向到登录页面
    - 确保用户只能操作自己的资源
    
    Args:
        model_class: 模型类
        id_param: URL参数中的ID字段名
        user_field: 模型中的用户ID字段名
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录以访问此页面。', 'info')
                return redirect(url_for('auth.login'))
            
            # 获取资源ID
            resource_id = kwargs.get(id_param)
            if not resource_id:
                abort(404)
            
            # 查找资源
            resource = model_class.query.get_or_404(resource_id)
            
            # 检查权限：管理员或资源所有者
            if not (current_user.is_admin() or 
                    getattr(resource, user_field) == current_user.id):
                flash('您没有权限操作此资源。', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def active_user_required(f):
    """
    激活用户验证装饰器
    
    实现需求:
    - 2.5: 未登录用户访问受保护页面时重定向到登录页面
    - 确保只有激活的用户才能访问
    
    Args:
        f: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录以访问此页面。', 'info')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_active:
            flash('您的账号已被禁用，请联系管理员。', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function