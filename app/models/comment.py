"""
评论数据模型
Comment Data Model
"""
from datetime import datetime
from app import db

class Comment(db.Model):
    """
    评论模型
    
    实现需求:
    - 4.1: 用户对文章发表评论时保存评论内容、作者和时间戳
    - 4.2: 用户提交空评论时阻止提交并显示错误提示
    - 4.3: 评论成功发布时在文章页面显示新评论
    - 4.4: 用户删除自己的评论时移除该评论
    """
    __tablename__ = 'comments'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    content = db.Column(db.Text, nullable=False)
    
    # 关联字段
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), index=True)
    
    # 状态管理
    status = db.Column(db.Enum('approved', 'pending', 'rejected', name='comment_status'), 
                      default='approved', nullable=False, index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 自关联关系（回复评论）
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), 
                             lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, content, author_id, article_id, parent_id=None, status='approved'):
        """
        初始化评论对象
        
        Args:
            content (str): 评论内容
            author_id (int): 作者ID
            article_id (int): 文章ID
            parent_id (int): 父评论ID
            status (str): 评论状态
        """
        self.content = content
        self.author_id = author_id
        self.article_id = article_id
        self.parent_id = parent_id
        self.status = status
    
    def is_approved(self):
        """
        检查评论是否已审核通过
        
        Returns:
            bool: 是否已审核通过
        """
        return self.status == 'approved'
    
    def is_pending(self):
        """
        检查评论是否待审核
        
        Returns:
            bool: 是否待审核
        """
        return self.status == 'pending'
    
    def is_rejected(self):
        """
        检查评论是否被拒绝
        
        Returns:
            bool: 是否被拒绝
        """
        return self.status == 'rejected'
    
    def is_reply(self):
        """
        检查是否为回复评论
        
        Returns:
            bool: 是否为回复评论
        """
        return self.parent_id is not None
    
    def is_top_level(self):
        """
        检查是否为顶级评论
        
        Returns:
            bool: 是否为顶级评论
        """
        return self.parent_id is None
    
    def approve(self):
        """
        审核通过评论
        """
        self.status = 'approved'
    
    def reject(self):
        """
        拒绝评论
        """
        self.status = 'rejected'
    
    def set_pending(self):
        """
        设置为待审核状态
        """
        self.status = 'pending'
    
    def can_edit(self, user):
        """
        检查用户是否可以编辑评论
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否可以编辑
        """
        return user.id == self.author_id or user.is_admin()
    
    def can_delete(self, user):
        """
        检查用户是否可以删除评论
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否可以删除
        """
        return user.id == self.author_id or user.is_admin()
    
    def get_reply_count(self):
        """
        获取回复数量
        
        Returns:
            int: 回复数量
        """
        return self.replies.filter_by(status='approved').count()
    
    def get_approved_replies(self):
        """
        获取已审核的回复
        
        Returns:
            Query: 回复查询对象
        """
        return self.replies.filter_by(status='approved').order_by(Comment.created_at.asc())
    
    def get_depth(self):
        """
        获取评论层级深度
        
        Returns:
            int: 层级深度
        """
        depth = 0
        current = self
        while current.parent_id:
            depth += 1
            current = current.parent
            if depth > 10:  # 防止无限循环
                break
        return depth
    
    def get_thread_root(self):
        """
        获取评论线程的根评论
        
        Returns:
            Comment: 根评论对象
        """
        current = self
        while current.parent_id:
            current = current.parent
        return current
    
    @staticmethod
    def validate_content(content):
        """
        验证评论内容
        
        Args:
            content (str): 评论内容
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not content or not content.strip():
            return False, "评论内容不能为空"
        
        if len(content) > 1000:
            return False, "评论内容长度不能超过1000个字符"
        
        return True, ""
    
    @staticmethod
    def get_article_comments(article_id, status='approved', include_replies=True):
        """
        获取文章的评论
        
        Args:
            article_id (int): 文章ID
            status (str): 评论状态
            include_replies (bool): 是否包含回复
            
        Returns:
            Query: 评论查询对象
        """
        query = Comment.query.filter_by(article_id=article_id, status=status)
        
        if not include_replies:
            query = query.filter_by(parent_id=None)
        
        return query.order_by(Comment.created_at.asc())
    
    @staticmethod
    def get_user_comments(user_id, status=None):
        """
        获取用户的评论
        
        Args:
            user_id (int): 用户ID
            status (str): 评论状态
            
        Returns:
            Query: 评论查询对象
        """
        query = Comment.query.filter_by(author_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Comment.created_at.desc())
    
    @staticmethod
    def get_pending_comments():
        """
        获取待审核的评论
        
        Returns:
            Query: 评论查询对象
        """
        return Comment.query.filter_by(status='pending').order_by(Comment.created_at.asc())
    
    @staticmethod
    def get_recent_comments(limit=10, status='approved'):
        """
        获取最新评论
        
        Args:
            limit (int): 数量限制
            status (str): 评论状态
            
        Returns:
            list: 评论列表
        """
        return Comment.query.filter_by(status=status).order_by(
            Comment.created_at.desc()
        ).limit(limit).all()
    
    def to_dict(self, include_replies=False):
        """
        转换为字典
        
        Args:
            include_replies (bool): 是否包含回复
            
        Returns:
            dict: 评论信息字典
        """
        data = {
            'id': self.id,
            'content': self.content,
            'author_id': self.author_id,
            'author_name': self.author.get_display_name() if self.author else None,
            'article_id': self.article_id,
            'article_title': self.article.title if self.article else None,
            'parent_id': self.parent_id,
            'status': self.status,
            'depth': self.get_depth(),
            'reply_count': self.get_reply_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_replies:
            data['replies'] = [reply.to_dict() for reply in self.get_approved_replies()]
        
        return data
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.author.username if self.author else self.author_id}>'