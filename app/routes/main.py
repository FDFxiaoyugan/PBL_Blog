"""
主要页面路由
Main Page Routes
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.decorators import active_user_required

# 创建主页面蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    首页
    
    实现需求:
    - 6.1: 用户访问首页时显示最新发布的文章列表
    """
    from app.models.article import Article
    # 获取最新的5篇文章
    recent_articles = Article.get_recent_articles(limit=5)
    return render_template('main/index.html', recent_articles=recent_articles)

@main_bp.route('/profile')
@active_user_required
def profile():
    """
    用户个人中心
    
    实现需求:
    - 2.5: 未登录用户访问受保护页面时重定向到登录页面
    - 7.1: 用户访问个人中心时显示用户的基本信息和统计数据
    """
    return render_template('main/profile.html')

