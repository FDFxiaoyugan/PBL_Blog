"""
用户数据模型
User Data Model
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """
    用户模型
    
    实现需求:
    - 1.1: 用户注册时验证输入信息的完整性和格式正确性
    - 1.2: 用户名或邮箱已存在时显示错误信息并阻止注册
    - 1.3: 注册信息验证通过时加密存储用户密码并创建用户账号
    """
    __tablename__ = 'users'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息 - 必需字段
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 个人信息 - 可选字段
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # 状态字段
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    articles = db.relationship('Article', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    admin = db.relationship('Admin', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password=None, **kwargs):
        """
        初始化用户对象
        
        Args:
            username (str): 用户名
            email (str): 邮箱
            password (str): 明文密码
            **kwargs: 其他字段
        """
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        
        # 设置其他字段
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """
        设置密码（加密存储）
        
        Args:
            password (str): 明文密码
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        验证密码
        
        Args:
            password (str): 明文密码
            
        Returns:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """
        检查用户是否为管理员
        
        Returns:
            bool: 是否为管理员
        """
        return self.admin is not None
    
    def get_display_name(self):
        """
        获取显示名称
        
        Returns:
            str: 昵称或用户名
        """
        return self.nickname or self.username
    
    def get_article_count(self):
        """
        获取用户文章数量
        
        Returns:
            int: 文章数量
        """
        return self.articles.filter_by(status='published').count()
    
    def get_comment_count(self):
        """
        获取用户评论数量
        
        Returns:
            int: 评论数量
        """
        return self.comments.count()
    
    @staticmethod
    def validate_username(username):
        """
        验证用户名
        
        Args:
            username (str): 用户名
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not username:
            return False, "用户名不能为空"
        
        if len(username) < 3:
            return False, "用户名长度至少3个字符"
        
        if len(username) > 50:
            return False, "用户名长度不能超过50个字符"
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return False, "用户名已存在"
        
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """
        验证邮箱
        
        Args:
            email (str): 邮箱地址
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        import re
        
        if not email:
            return False, "邮箱不能为空"
        
        # 简单的邮箱格式验证
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "邮箱格式不正确"
        
        if len(email) > 100:
            return False, "邮箱长度不能超过100个字符"
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return False, "邮箱已存在"
        
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """
        验证密码
        
        Args:
            password (str): 密码
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not password:
            return False, "密码不能为空"
        
        if len(password) < 6:
            return False, "密码长度至少6个字符"
        
        if len(password) > 128:
            return False, "密码长度不能超过128个字符"
        
        return True, ""
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 用户信息字典
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'bio': self.bio,
            'is_active': self.is_active,
            'is_admin': self.is_admin(),
            'article_count': self.get_article_count(),
            'comment_count': self.get_comment_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'