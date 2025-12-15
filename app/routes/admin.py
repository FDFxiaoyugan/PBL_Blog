"""
管理员路由
Admin Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.utils.decorators import admin_required

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    管理员仪表板
    
    实现需求:
    - 5.1: 管理员访问用户管理页面时显示所有用户列表和管理操作
    - 5.5: 普通用户尝试访问管理功能时拒绝访问并显示权限不足提示
    """
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """
    用户管理
    
    实现需求:
    - 5.1: 管理员访问用户管理页面时显示所有用户列表和管理操作
    - 5.2: 管理员删除用户时移除用户及其所有相关内容
    """
    return "用户管理 - 待实现"

@admin_bp.route('/articles')
@login_required
@admin_required
def articles():
    """
    文章管理
    
    实现需求:
    - 5.3: 管理员管理文章时允许查看、编辑或删除任何文章
    """
    return "文章管理 - 待实现"

@admin_bp.route('/comments')
@login_required
@admin_required
def manage_comments():
    """
    评论管理
    
    实现需求:
    - 5.4: 管理员管理评论时允许查看、编辑或删除任何评论
    """
    from flask import request
    from app.models.comment import Comment
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    per_page = 20
    
    # 构建查询
    query = Comment.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    # 按创建时间倒序排列并分页
    comments = query.order_by(Comment.created_at.desc())\
                   .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/comments.html', 
                         comments=comments, 
                         current_status=status)