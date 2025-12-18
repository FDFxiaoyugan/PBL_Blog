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
    用户管理列表
    
    实现需求:
    - 5.1: 管理员访问用户管理页面时显示所有用户列表和管理操作
    """
    from app.models.user import User
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    per_page = 20
    
    # 构建查询
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search),
                User.nickname.contains(search)
            )
        )
    
    # 按创建时间倒序排列并分页
    users_pagination = query.order_by(User.created_at.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', 
                         users=users_pagination,
                         search=search)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """
    用户详情
    
    实现需求:
    - 5.1: 管理员访问用户管理页面时显示所有用户列表和管理操作
    """
    from app.models.user import User
    
    user = User.query.get_or_404(user_id)
    
    # 获取用户统计信息
    article_count = user.articles.count()
    published_article_count = user.articles.filter_by(status='published').count()
    comment_count = user.comments.count()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         article_count=article_count,
                         published_article_count=published_article_count,
                         comment_count=comment_count)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """
    编辑用户信息
    
    实现需求:
    - 5.1: 管理员访问用户管理页面时显示所有用户列表和管理操作
    """
    from app.models.user import User
    from app.forms.auth import EditUserForm
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            # 更新用户信息
            user.nickname = request.form.get('nickname', '').strip()
            user.bio = request.form.get('bio', '').strip()
            user.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            flash('用户信息更新成功。', 'success')
            return redirect(url_for('admin.user_detail', user_id=user.id))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'更新用户信息失败: {str(e)}', 'error')
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    删除用户
    
    实现需求:
    - 5.2: 管理员删除用户时移除用户及其所有相关内容
    """
    from app.models.user import User
    from flask_login import current_user
    
    user = User.query.get_or_404(user_id)
    
    # 防止删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账号。', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        username = user.username
        # 删除用户（级联删除相关内容）
        db.session.delete(user)
        db.session.commit()
        flash(f'用户 {username} 及其所有相关内容已删除。', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'删除用户失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """
    切换用户激活状态
    
    实现需求:
    - 5.1: 管理员访问用户管理页面时显示所有用户列表和管理操作
    """
    from app.models.user import User
    from flask_login import current_user
    
    user = User.query.get_or_404(user_id)
    
    # 防止禁用自己
    if user.id == current_user.id:
        flash('不能禁用自己的账号。', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status_text = '激活' if user.is_active else '禁用'
        flash(f'用户 {user.username} 已{status_text}。', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'更新用户状态失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/articles')
@login_required
@admin_required
def articles():
    """
    文章管理列表
    
    实现需求:
    - 5.3: 管理员管理文章时允许查看、编辑或删除任何文章
    """
    from app.models.article import Article
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    per_page = 20
    
    # 构建查询
    query = Article.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            db.or_(
                Article.title.contains(search),
                Article.content.contains(search)
            )
        )
    
    # 按创建时间倒序排列并分页
    articles_pagination = query.order_by(Article.created_at.desc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/articles.html',
                         articles=articles_pagination,
                         current_status=status,
                         search=search)

@admin_bp.route('/articles/<int:article_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_article(article_id):
    """
    删除文章
    
    实现需求:
    - 5.3: 管理员管理文章时允许查看、编辑或删除任何文章
    """
    from app.models.article import Article
    
    article = Article.query.get_or_404(article_id)
    
    try:
        title = article.title
        # 删除文章（级联删除相关评论）
        db.session.delete(article)
        db.session.commit()
        flash(f'文章《{title}》及其所有评论已删除。', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'删除文章失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.articles'))

@admin_bp.route('/articles/<int:article_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_article_status(article_id):
    """
    切换文章状态
    
    实现需求:
    - 5.3: 管理员管理文章时允许查看、编辑或删除任何文章
    """
    from app.models.article import Article
    
    article = Article.query.get_or_404(article_id)
    new_status = request.form.get('status')
    
    if new_status not in ['draft', 'published', 'archived']:
        flash('无效的文章状态。', 'error')
        return redirect(url_for('admin.articles'))
    
    try:
        article.status = new_status
        if new_status == 'published' and not article.published_at:
            article.publish()
        elif new_status == 'draft':
            article.unpublish()
        elif new_status == 'archived':
            article.archive()
        
        db.session.commit()
        flash(f'文章状态已更新为 {new_status}。', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'更新文章状态失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.articles'))

@admin_bp.route('/comments')
@login_required
@admin_required
def manage_comments():
    """
    评论管理列表
    
    实现需求:
    - 5.4: 管理员管理评论时允许查看、编辑或删除任何评论
    """
    from app.models.comment import Comment
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    per_page = 20
    
    # 构建查询
    query = Comment.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(Comment.content.contains(search))
    
    # 按创建时间倒序排列并分页
    comments = query.order_by(Comment.created_at.desc())\
                   .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/comments.html', 
                         comments=comments, 
                         current_status=status,
                         search=search)

@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_comment(comment_id):
    """
    删除评论
    
    实现需求:
    - 5.4: 管理员管理评论时允许查看、编辑或删除任何评论
    """
    from app.models.comment import Comment
    
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        # 删除评论（级联删除回复）
        db.session.delete(comment)
        db.session.commit()
        flash('评论已删除。', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'删除评论失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_comments'))

@admin_bp.route('/comments/<int:comment_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_comment(comment_id):
    """
    审核通过评论
    
    实现需求:
    - 5.4: 管理员管理评论时允许查看、编辑或删除任何评论
    """
    from app.models.comment import Comment
    
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.approve()
        db.session.commit()
        flash('评论已审核通过。', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'审核评论失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_comments'))

@admin_bp.route('/comments/<int:comment_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_comment(comment_id):
    """
    拒绝评论
    
    实现需求:
    - 5.4: 管理员管理评论时允许查看、编辑或删除任何评论
    """
    from app.models.comment import Comment
    
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.reject()
        db.session.commit()
        flash('评论已被拒绝。', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'拒绝评论失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_comments'))

@admin_bp.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_comment(comment_id):
    """
    编辑评论
    
    实现需求:
    - 5.4: 管理员管理评论时允许查看、编辑或删除任何评论
    """
    from app.models.comment import Comment
    
    comment = Comment.query.get_or_404(comment_id)
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        
        # 验证内容
        is_valid, error_msg = Comment.validate_content(content)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('admin/edit_comment.html', comment=comment)
        
        try:
            comment.content = content
            db.session.commit()
            flash('评论已更新。', 'success')
            return redirect(url_for('admin.manage_comments'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'更新评论失败: {str(e)}', 'error')
    
    return render_template('admin/edit_comment.html', comment=comment)