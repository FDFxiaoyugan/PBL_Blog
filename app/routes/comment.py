"""
评论管理路由
Comment Management Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.comment import Comment
from app.models.article import Article
from app.forms.comment import CommentForm, CommentReplyForm, CommentDeleteForm, CommentModerationForm
from app.utils.decorators import active_user_required, admin_required

# 创建评论蓝图
comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/articles/<int:article_id>/comments', methods=['POST'])
@active_user_required
def create_comment(article_id):
    """
    创建评论
    
    实现需求:
    - 4.1: 用户对文章发表评论时保存评论内容、作者和时间戳
    - 4.2: 用户提交空评论时阻止提交并显示错误提示
    - 4.3: 评论成功发布时在文章页面显示新评论
    """
    article = Article.query.get_or_404(article_id)
    
    # 只能对已发布的文章评论
    if article.status != 'published':
        flash('无法对未发布的文章发表评论。', 'error')
        return redirect(url_for('article.article_detail', id=article_id))
    
    form = CommentForm()
    
    if form.validate_on_submit():
        try:
            # 验证评论内容
            is_valid, error_msg = Comment.validate_content(form.content.data)
            if not is_valid:
                flash(error_msg, 'error')
                return redirect(url_for('article.article_detail', id=article_id))
            
            # 创建评论对象
            comment = Comment(
                content=form.content.data.strip(),
                author_id=current_user.id,
                article_id=article_id,
                parent_id=form.parent_id.data if form.parent_id.data else None,
                status='approved'  # 默认审核通过，可根据需要修改为待审核
            )
            
            # 保存到数据库
            db.session.add(comment)
            db.session.commit()
            
            flash('评论发表成功！', 'success')
            return redirect(url_for('article.article_detail', id=article_id) + f'#comment-{comment.id}')
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('发表评论时发生错误，请重试。', 'error')
    else:
        # 显示表单验证错误
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'error')
    
    return redirect(url_for('article.article_detail', id=article_id))

@comment_bp.route('/comments/<int:comment_id>/reply', methods=['POST'])
@active_user_required
def reply_comment(comment_id):
    """
    回复评论
    
    实现需求:
    - 4.1: 用户对文章发表评论时保存评论内容、作者和时间戳
    - 4.3: 评论成功发布时在文章页面显示新评论
    """
    parent_comment = Comment.query.get_or_404(comment_id)
    article = parent_comment.article
    
    # 只能对已发布文章的已审核评论进行回复
    if article.status != 'published' or not parent_comment.is_approved():
        flash('无法回复此评论。', 'error')
        return redirect(url_for('article.article_detail', id=article.id))
    
    form = CommentReplyForm()
    
    if form.validate_on_submit():
        try:
            # 验证回复内容
            is_valid, error_msg = Comment.validate_content(form.content.data)
            if not is_valid:
                flash(error_msg, 'error')
                return redirect(url_for('article.article_detail', id=article.id))
            
            # 创建回复评论
            reply = Comment(
                content=form.content.data.strip(),
                author_id=current_user.id,
                article_id=article.id,
                parent_id=parent_comment.id,
                status='approved'
            )
            
            # 保存到数据库
            db.session.add(reply)
            db.session.commit()
            
            flash('回复发表成功！', 'success')
            return redirect(url_for('article.article_detail', id=article.id) + f'#comment-{reply.id}')
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('发表回复时发生错误，请重试。', 'error')
    else:
        # 显示表单验证错误
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'error')
    
    return redirect(url_for('article.article_detail', id=article.id))

@comment_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@active_user_required
def delete_comment(comment_id):
    """
    删除评论
    
    实现需求:
    - 4.4: 用户删除自己的评论时移除该评论
    """
    comment = Comment.query.get_or_404(comment_id)
    article_id = comment.article_id
    
    # 检查权限
    if not comment.can_delete(current_user):
        flash('您没有权限删除此评论。', 'error')
        return redirect(url_for('article.article_detail', id=article_id))
    
    form = CommentDeleteForm()
    
    if form.validate_on_submit():
        try:
            # 删除评论（级联删除回复）
            db.session.delete(comment)
            db.session.commit()
            
            flash('评论删除成功！', 'success')
            return redirect(url_for('article.article_detail', id=article_id))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('删除评论时发生错误，请重试。', 'error')
    
    return redirect(url_for('article.article_detail', id=article_id))

@comment_bp.route('/comments/<int:comment_id>/approve', methods=['POST'])
@admin_required
def approve_comment(comment_id):
    """
    审核通过评论（管理员功能）
    """
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.approve()
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': '评论已审核通过'})
        else:
            flash('评论已审核通过！', 'success')
            return redirect(request.referrer or url_for('admin.manage_comments'))
            
    except SQLAlchemyError:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': '操作失败'}), 500
        else:
            flash('操作失败，请重试。', 'error')
            return redirect(request.referrer or url_for('admin.manage_comments'))

@comment_bp.route('/comments/<int:comment_id>/reject', methods=['POST'])
@admin_required
def reject_comment(comment_id):
    """
    拒绝评论（管理员功能）
    """
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.reject()
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': '评论已被拒绝'})
        else:
            flash('评论已被拒绝！', 'success')
            return redirect(request.referrer or url_for('admin.manage_comments'))
            
    except SQLAlchemyError:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': '操作失败'}), 500
        else:
            flash('操作失败，请重试。', 'error')
            return redirect(request.referrer or url_for('admin.manage_comments'))

@comment_bp.route('/comments/<int:comment_id>/pending', methods=['POST'])
@admin_required
def set_comment_pending(comment_id):
    """
    设置评论为待审核状态（管理员功能）
    """
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.set_pending()
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': '评论已设为待审核'})
        else:
            flash('评论已设为待审核！', 'success')
            return redirect(request.referrer or url_for('admin.manage_comments'))
            
    except SQLAlchemyError:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': '操作失败'}), 500
        else:
            flash('操作失败，请重试。', 'error')
            return redirect(request.referrer or url_for('admin.manage_comments'))

@comment_bp.route('/my-comments')
@active_user_required
def my_comments():
    """
    我的评论列表
    
    实现需求:
    - 7.5: 用户查看自己的评论时显示该用户发表的所有评论列表
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    comments = Comment.get_user_comments(current_user.id)\
                     .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('comment/my_comments.html', comments=comments)

@comment_bp.route('/api/comments/<int:comment_id>')
def get_comment_api(comment_id):
    """
    获取评论信息API
    """
    comment = Comment.query.get_or_404(comment_id)
    
    # 只返回已审核的评论信息
    if not comment.is_approved():
        abort(404)
    
    return jsonify(comment.to_dict(include_replies=True))

@comment_bp.route('/api/articles/<int:article_id>/comments')
def get_article_comments_api(article_id):
    """
    获取文章评论API
    """
    article = Article.query.get_or_404(article_id)
    
    # 只返回已发布文章的已审核评论
    if article.status != 'published':
        abort(404)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    include_replies = request.args.get('include_replies', 'true').lower() == 'true'
    
    # 获取顶级评论
    comments_query = Comment.get_article_comments(article_id, status='approved', include_replies=False)
    comments = comments_query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = {
        'comments': [comment.to_dict(include_replies=include_replies) for comment in comments.items],
        'pagination': {
            'page': comments.page,
            'pages': comments.pages,
            'per_page': comments.per_page,
            'total': comments.total,
            'has_next': comments.has_next,
            'has_prev': comments.has_prev
        }
    }
    
    return jsonify(result)