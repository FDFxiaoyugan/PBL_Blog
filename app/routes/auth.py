"""
用户认证路由
Authentication Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms.auth import RegistrationForm, LoginForm

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册功能
    
    实现需求:
    - 1.1: 验证用户输入信息的完整性和格式正确性
    - 1.2: 用户名或邮箱已存在时显示错误信息并阻止注册
    - 1.3: 注册信息验证通过时加密存储用户密码并创建用户账号
    - 1.4: 用户成功注册时自动跳转到登录页面
    - 1.5: 用户输入无效邮箱格式时显示邮箱格式错误提示
    """
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # 创建新用户
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                nickname=form.nickname.data or None
            )
            
            # 保存到数据库
            db.session.add(user)
            db.session.commit()
            
            flash('注册成功！请登录您的账号。', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后重试。', 'error')
            # 在开发环境下显示详细错误信息
            if current_app.debug:
                flash(f'错误详情: {str(e)}', 'error')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录功能
    
    实现需求:
    - 2.1: 用户输入正确的用户名和密码时验证凭据并创建用户会话
    - 2.2: 用户输入错误的登录信息时显示登录失败提示
    - 2.3: 用户成功登录时重定向到用户仪表板
    """
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(username=form.username.data).first()
        
        # 验证用户存在且密码正确
        if user and user.check_password(form.password.data):
            # 检查用户是否激活
            if not user.is_active:
                flash('您的账号已被禁用，请联系管理员。', 'error')
                return render_template('auth/login.html', form=form)
            
            # 登录用户
            login_user(user, remember=form.remember_me.data)
            flash(f'欢迎回来，{user.get_display_name()}！', 'success')
            
            # 重定向到用户想要访问的页面或首页
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误。', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    用户登出功能
    
    实现需求:
    - 2.4: 用户会话过期时自动注销用户并重定向到登录页面
    """
    logout_user()
    flash('您已成功登出。', 'info')
    return redirect(url_for('main.index'))