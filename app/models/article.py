"""
文章数据模型
Article Data Model
"""
from datetime import datetime
from app import db
from sqlalchemy import or_

class Article(db.Model):
    """
    文章模型
    
    实现需求:
    - 3.1: 用户创建新文章时保存文章标题、内容、分类和发布时间
    - 3.2: 用户提交空标题或内容时阻止发布并显示错误提示
    - 3.3: 文章成功发布时在文章列表中显示新文章
    - 3.4: 用户编辑自己的文章时更新文章内容并保留修改时间
    - 3.5: 用户删除自己的文章时移除文章及其相关评论
    """
    __tablename__ = 'articles'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))
    
    # 关联字段
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), index=True)
    
    # 状态管理
    status = db.Column(db.Enum('draft', 'published', 'archived', name='article_status'), 
                      default='draft', nullable=False, index=True)
    
    # 统计信息
    view_count = db.Column(db.Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = db.Column(db.DateTime, index=True)
    
    # 关系
    comments = db.relationship('Comment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title, content, author_id, category_id=None, status='draft', **kwargs):
        """
        初始化文章对象
        
        Args:
            title (str): 文章标题
            content (str): 文章内容
            author_id (int): 作者ID
            category_id (int): 分类ID
            status (str): 文章状态
            **kwargs: 其他字段
        """
        self.title = title
        self.content = content
        self.author_id = author_id
        self.category_id = category_id
        self.status = status
        
        # 设置其他字段
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 生成摘要
        if not self.summary:
            self.generate_summary()
    
    def generate_summary(self, length=200):
        """
        生成文章摘要
        
        Args:
            length (int): 摘要长度
        """
        if self.content:
            # 移除HTML标签（简单处理）
            import re
            clean_content = re.sub(r'<[^>]+>', '', self.content)
            self.summary = clean_content[:length] + ('...' if len(clean_content) > length else '')
    
    def publish(self):
        """
        发布文章
        """
        self.status = 'published'
        self.published_at = datetime.utcnow()
    
    def unpublish(self):
        """
        取消发布文章
        """
        self.status = 'draft'
        self.published_at = None
    
    def archive(self):
        """
        归档文章
        """
        self.status = 'archived'
    
    def increment_view_count(self):
        """
        增加浏览次数
        """
        self.view_count += 1
    
    def is_published(self):
        """
        检查文章是否已发布
        
        Returns:
            bool: 是否已发布
        """
        return self.status == 'published'
    
    def is_draft(self):
        """
        检查文章是否为草稿
        
        Returns:
            bool: 是否为草稿
        """
        return self.status == 'draft'
    
    def is_archived(self):
        """
        检查文章是否已归档
        
        Returns:
            bool: 是否已归档
        """
        return self.status == 'archived'
    
    def can_edit(self, user):
        """
        检查用户是否可以编辑文章
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否可以编辑
        """
        return user.id == self.author_id or user.is_admin()
    
    def can_delete(self, user):
        """
        检查用户是否可以删除文章
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 是否可以删除
        """
        return user.id == self.author_id or user.is_admin()
    
    def get_comment_count(self):
        """
        获取文章评论数量
        
        Returns:
            int: 评论数量
        """
        return self.comments.count()
    
    def get_approved_comments(self):
        """
        获取已审核的评论
        
        Returns:
            Query: 评论查询对象
        """
        return self.comments.filter_by(status='approved').order_by(
            self.comments.property.mapper.class_.created_at.asc()
        )
    
    @staticmethod
    def validate_title(title):
        """
        验证文章标题
        
        Args:
            title (str): 文章标题
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not title or not title.strip():
            return False, "文章标题不能为空"
        
        if len(title) > 200:
            return False, "文章标题长度不能超过200个字符"
        
        return True, ""
    
    @staticmethod
    def validate_content(content):
        """
        验证文章内容
        
        Args:
            content (str): 文章内容
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not content or not content.strip():
            return False, "文章内容不能为空"
        
        return True, ""
    
    @staticmethod
    def search(keyword, category_id=None, status='published'):
        """
        搜索文章
        
        Args:
            keyword (str): 搜索关键词
            category_id (int): 分类ID
            status (str): 文章状态
            
        Returns:
            Query: 文章查询对象
        """
        query = Article.query.filter_by(status=status)
        
        if keyword:
            search_filter = or_(
                Article.title.contains(keyword),
                Article.content.contains(keyword),
                Article.summary.contains(keyword)
            )
            query = query.filter(search_filter)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        return query.order_by(Article.created_at.desc())
    
    @staticmethod
    def get_published_articles():
        """
        获取已发布的文章
        
        Returns:
            Query: 文章查询对象
        """
        return Article.query.filter_by(status='published').order_by(Article.published_at.desc())
    
    @staticmethod
    def get_recent_articles(limit=10):
        """
        获取最新文章
        
        Args:
            limit (int): 数量限制
            
        Returns:
            list: 文章列表
        """
        return Article.get_published_articles().limit(limit).all()
    
    def to_dict(self, include_content=False):
        """
        转换为字典
        
        Args:
            include_content (bool): 是否包含文章内容
            
        Returns:
            dict: 文章信息字典
        """
        data = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'author_id': self.author_id,
            'author_name': self.author.get_display_name() if self.author else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'status': self.status,
            'view_count': self.view_count,
            'comment_count': self.get_comment_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
        
        if include_content:
            data['content'] = self.content
        
        return data
    
    def __repr__(self):
        return f'<Article {self.title}>'