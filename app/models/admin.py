"""
管理员数据模型
Admin Data Model
"""
from datetime import datetime
from app import db
import json

class Admin(db.Model):
    """
    管理员模型
    
    实现需求:
    - 5.1: 管理员访问用户管理页面时显示所有用户列表和管理操作
    - 5.2: 管理员删除用户时移除用户及其所有相关内容
    - 5.3: 管理员管理文章时允许查看、编辑或删除任何文章
    - 5.4: 管理员管理评论时允许查看、编辑或删除任何评论
    - 5.5: 普通用户尝试访问管理功能时拒绝访问并显示权限不足提示
    """
    __tablename__ = 'admins'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 关联用户
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # 角色和权限
    role = db.Column(db.String(20), default='admin', nullable=False)
    permissions = db.Column(db.Text)  # JSON格式存储权限
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, user_id, role='admin', permissions=None):
        """
        初始化管理员对象
        
        Args:
            user_id (int): 用户ID
            role (str): 角色名称
            permissions (dict): 权限字典
        """
        self.user_id = user_id
        self.role = role
        if permissions is None:
            permissions = self.get_default_permissions()
        self.set_permissions(permissions)
    
    def get_default_permissions(self):
        """
        获取默认权限
        
        Returns:
            dict: 默认权限字典
        """
        return {
            'user_management': {
                'view': True,
                'create': True,
                'edit': True,
                'delete': True
            },
            'article_management': {
                'view': True,
                'create': True,
                'edit': True,
                'delete': True,
                'publish': True,
                'unpublish': True
            },
            'comment_management': {
                'view': True,
                'edit': True,
                'delete': True,
                'approve': True,
                'reject': True
            },
            'category_management': {
                'view': True,
                'create': True,
                'edit': True,
                'delete': True
            },
            'system_settings': {
                'view': True,
                'edit': True
            }
        }
    
    def set_permissions(self, permissions):
        """
        设置权限
        
        Args:
            permissions (dict): 权限字典
        """
        self.permissions = json.dumps(permissions, ensure_ascii=False)
    
    def get_permissions(self):
        """
        获取权限
        
        Returns:
            dict: 权限字典
        """
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except json.JSONDecodeError:
                return self.get_default_permissions()
        return self.get_default_permissions()
    
    def has_permission(self, module, action):
        """
        检查是否有特定权限
        
        Args:
            module (str): 模块名称
            action (str): 操作名称
            
        Returns:
            bool: 是否有权限
        """
        permissions = self.get_permissions()
        return permissions.get(module, {}).get(action, False)
    
    def can_manage_users(self):
        """
        检查是否可以管理用户
        
        Returns:
            bool: 是否可以管理用户
        """
        return self.has_permission('user_management', 'view')
    
    def can_delete_users(self):
        """
        检查是否可以删除用户
        
        Returns:
            bool: 是否可以删除用户
        """
        return self.has_permission('user_management', 'delete')
    
    def can_manage_articles(self):
        """
        检查是否可以管理文章
        
        Returns:
            bool: 是否可以管理文章
        """
        return self.has_permission('article_management', 'view')
    
    def can_delete_articles(self):
        """
        检查是否可以删除文章
        
        Returns:
            bool: 是否可以删除文章
        """
        return self.has_permission('article_management', 'delete')
    
    def can_manage_comments(self):
        """
        检查是否可以管理评论
        
        Returns:
            bool: 是否可以管理评论
        """
        return self.has_permission('comment_management', 'view')
    
    def can_delete_comments(self):
        """
        检查是否可以删除评论
        
        Returns:
            bool: 是否可以删除评论
        """
        return self.has_permission('comment_management', 'delete')
    
    def can_manage_categories(self):
        """
        检查是否可以管理分类
        
        Returns:
            bool: 是否可以管理分类
        """
        return self.has_permission('category_management', 'view')
    
    def add_permission(self, module, action):
        """
        添加权限
        
        Args:
            module (str): 模块名称
            action (str): 操作名称
        """
        permissions = self.get_permissions()
        if module not in permissions:
            permissions[module] = {}
        permissions[module][action] = True
        self.set_permissions(permissions)
    
    def remove_permission(self, module, action):
        """
        移除权限
        
        Args:
            module (str): 模块名称
            action (str): 操作名称
        """
        permissions = self.get_permissions()
        if module in permissions and action in permissions[module]:
            permissions[module][action] = False
            self.set_permissions(permissions)
    
    def is_super_admin(self):
        """
        检查是否为超级管理员
        
        Returns:
            bool: 是否为超级管理员
        """
        return self.role == 'super_admin'
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 管理员信息字典
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'permissions': self.get_permissions(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Admin {self.user.username if self.user else self.user_id}>'