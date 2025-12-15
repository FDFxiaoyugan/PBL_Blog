"""
文章管理路由
Article Management Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models.article import Article
from app.models.category import Category
from app.forms.article import ArticleForm, ArticleSearchForm, ArticleDeleteForm
from app.utils.decorators import active_user_required

# 创建文章蓝图
article_bp = Blueprint('article', __name__)

@article_bp.route('/articles')
def list_articles():
    """
    文章列表页面
    
    实现需求:
    - 6.1: 用户访问首页时显示最新发布的文章列表
    - 6.2: 用户按分类筛选时显示该分类下的所有文章
    - 6.3: 用户搜索关键词时返回标题或内容包含关键词的文章
    - 6.4: 文章列表超过页面容量时提供分页导航功能
    """
    # 获取搜索参数
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10篇文章
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', 0, type=int)
    
    # 构建查询
    query = Article.query.filter_by(status='published')
    
    # 应用搜索条件
    if keyword:
        from sqlalchemy import or_
        search_filter = or_(
            Article.title.contains(keyword),
            Article.content.contains(keyword),
            Article.summary.contains(keyword)
        )
        query = query.filter(search_filter)
    
    if category_id > 0:
        query = query.filter_by(category_id=category_id)
    
    # 按发布时间排序并分页
    articles = query.order_by(Article.published_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 获取搜索表单
    search_form = ArticleSearchForm()
    search_form.keyword.data = keyword
    search_form.category_id.data = category_id
    
    # 获取分类信息
    categories = Category.query.all()
    current_category = Category.query.get(category_id) if category_id > 0 else None
    
    return render_template('article/list.html', 
                         articles=articles, 
                         search_form=search_form,
                         categories=categories,
                         current_category=current_category,
                         keyword=keyword)

@article_bp.route('/articles/<int:id>')
def article_detail(id):
    """
    文章详情页面
    
    实现需求:
    - 6.5: 用户点击文章标题时显示完整的文章内容和评论
    """
    article = Article.query.get_or_404(id)
    
    # 只显示已发布的文章，除非是作者或管理员
    if article.status != 'published':
        if not current_user.is_authenticated or not article.can_edit(current_user):
            abort(404)
    
    # 增加浏览次数
    if article.status == 'published':
        try:
            article.increment_view_count()
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
    
    # 获取评论
    comments = article.get_approved_comments().all()
    
    # 创建评论表单
    from app.forms.comment import CommentForm
    comment_form = CommentForm()
    
    return render_template('article/detail.html', 
                         article=article, 
                         comments=comments,
                         comment_form=comment_form)

@article_bp.route('/articles/create', methods=['GET', 'POST'])
@active_user_required
def create_article():
    """
    创建文章
    
    实现需求:
    - 3.1: 用户创建新文章时保存文章标题、内容、分类和发布时间
    - 3.2: 用户提交空标题或内容时阻止发布并显示错误提示
    - 3.3: 文章成功发布时在文章列表中显示新文章
    """
    form = ArticleForm()
    
    if form.validate_on_submit():
        try:
            # 创建文章对象
            article = Article(
                title=form.title.data.strip(),
                content=form.content.data.strip(),
                summary=form.summary.data.strip() if form.summary.data else None,
                author_id=current_user.id,
                category_id=form.category_id.data if form.category_id.data > 0 else None,
                status=form.status.data
            )
            
            # 如果状态为已发布，设置发布时间
            if article.status == 'published':
                article.publish()
            
            # 保存到数据库
            db.session.add(article)
            db.session.commit()
            
            flash('文章创建成功！', 'success')
            return redirect(url_for('article.article_detail', id=article.id))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('创建文章时发生错误，请重试。', 'error')
    
    return render_template('article/create.html', form=form)

@article_bp.route('/articles/<int:id>/edit', methods=['GET', 'POST'])
@active_user_required
def edit_article(id):
    """
    编辑文章
    
    实现需求:
    - 3.4: 用户编辑自己的文章时更新文章内容并保留修改时间
    """
    article = Article.query.get_or_404(id)
    
    # 检查权限
    if not article.can_edit(current_user):
        flash('您没有权限编辑此文章。', 'error')
        return redirect(url_for('article.article_detail', id=id))
    
    form = ArticleForm(obj=article)
    
    if form.validate_on_submit():
        try:
            # 更新文章信息
            article.title = form.title.data.strip()
            article.content = form.content.data.strip()
            article.summary = form.summary.data.strip() if form.summary.data else None
            article.category_id = form.category_id.data if form.category_id.data > 0 else None
            
            # 处理状态变更
            old_status = article.status
            new_status = form.status.data
            
            if old_status != new_status:
                if new_status == 'published' and old_status != 'published':
                    article.publish()
                elif new_status != 'published' and old_status == 'published':
                    article.status = new_status
                    if new_status == 'draft':
                        article.published_at = None
                else:
                    article.status = new_status
            
            # 重新生成摘要（如果没有手动设置）
            if not article.summary:
                article.generate_summary()
            
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('article.article_detail', id=article.id))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('更新文章时发生错误，请重试。', 'error')
    
    return render_template('article/edit.html', form=form, article=article)

@article_bp.route('/articles/<int:id>/delete', methods=['POST'])
@active_user_required
def delete_article(id):
    """
    删除文章
    
    实现需求:
    - 3.5: 用户删除自己的文章时移除文章及其相关评论
    """
    article = Article.query.get_or_404(id)
    
    # 检查权限
    if not article.can_delete(current_user):
        flash('您没有权限删除此文章。', 'error')
        return redirect(url_for('article.article_detail', id=id))
    
    form = ArticleDeleteForm()
    
    if form.validate_on_submit():
        try:
            # 删除文章（级联删除评论）
            db.session.delete(article)
            db.session.commit()
            
            flash('文章删除成功！', 'success')
            return redirect(url_for('article.list_articles'))
            
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('删除文章时发生错误，请重试。', 'error')
            return redirect(url_for('article.article_detail', id=id))
    
    flash('删除操作无效。', 'error')
    return redirect(url_for('article.article_detail', id=id))

@article_bp.route('/my-articles')
@active_user_required
def my_articles():
    """
    我的文章列表
    
    实现需求:
    - 7.4: 用户查看自己的文章时显示该用户发布的所有文章列表
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    articles = Article.query.filter_by(author_id=current_user.id)\
                          .order_by(Article.created_at.desc())\
                          .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('article/my_articles.html', articles=articles)

@article_bp.route('/articles/<int:id>/publish', methods=['POST'])
@active_user_required
def publish_article(id):
    """
    发布文章
    """
    article = Article.query.get_or_404(id)
    
    # 检查权限
    if not article.can_edit(current_user):
        return jsonify({'success': False, 'message': '您没有权限发布此文章。'}), 403
    
    try:
        article.publish()
        db.session.commit()
        return jsonify({'success': True, 'message': '文章发布成功！'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'success': False, 'message': '发布文章时发生错误。'}), 500

@article_bp.route('/articles/<int:id>/unpublish', methods=['POST'])
@active_user_required
def unpublish_article(id):
    """
    取消发布文章
    """
    article = Article.query.get_or_404(id)
    
    # 检查权限
    if not article.can_edit(current_user):
        return jsonify({'success': False, 'message': '您没有权限操作此文章。'}), 403
    
    try:
        article.unpublish()
        db.session.commit()
        return jsonify({'success': True, 'message': '文章已转为草稿！'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试。'}), 500

@article_bp.route('/articles/<int:id>/archive', methods=['POST'])
@active_user_required
def archive_article(id):
    """
    归档文章
    """
    article = Article.query.get_or_404(id)
    
    # 检查权限
    if not article.can_edit(current_user):
        return jsonify({'success': False, 'message': '您没有权限操作此文章。'}), 403
    
    try:
        article.archive()
        db.session.commit()
        return jsonify({'success': True, 'message': '文章已归档！'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试。'}), 500