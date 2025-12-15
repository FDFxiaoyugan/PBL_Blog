"""
分类数据模型
Category Data Model
"""
from datetime import datetime
from app import db
import re

class Category(db.Model):
    """
    分类模型
    
    实现需求:
    - 6.2: 用户按分类筛选时显示该分类下的所有文章
    """
    __tablename__ = 'categories'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    articles = db.relationship('Article', backref='category', lazy='dynamic')
    
    def __init__(self, name, description=None, slug=None):
        """
        初始化分类对象
        
        Args:
            name (str): 分类名称
            description (str): 分类描述
            slug (str): URL友好的标识符
        """
        self.name = name
        self.description = description
        self.slug = slug or self.generate_slug(name)
    
    @staticmethod
    def generate_slug(name):
        """
        生成URL友好的slug
        
        Args:
            name (str): 分类名称
            
        Returns:
            str: slug
        """
        # 移除特殊字符，转换为小写，用连字符替换空格
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def get_article_count(self):
        """
        获取分类下的文章数量
        
        Returns:
            int: 文章数量
        """
        return self.articles.filter_by(status='published').count()
    
    def get_published_articles(self):
        """
        获取分类下已发布的文章
        
        Returns:
            Query: 文章查询对象
        """
        return self.articles.filter_by(status='published').order_by(
            self.articles.property.mapper.class_.created_at.desc()
        )
    
    @staticmethod
    def validate_name(name):
        """
        验证分类名称
        
        Args:
            name (str): 分类名称
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not name:
            return False, "分类名称不能为空"
        
        if len(name) < 2:
            return False, "分类名称长度至少2个字符"
        
        if len(name) > 50:
            return False, "分类名称长度不能超过50个字符"
        
        # 检查分类名称是否已存在
        if Category.query.filter_by(name=name).first():
            return False, "分类名称已存在"
        
        return True, ""
    
    @staticmethod
    def validate_slug(slug):
        """
        验证slug
        
        Args:
            slug (str): slug
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not slug:
            return False, "Slug不能为空"
        
        if len(slug) > 50:
            return False, "Slug长度不能超过50个字符"
        
        # 检查slug格式（只允许字母、数字、连字符）
        if not re.match(r'^[a-z0-9-]+$', slug):
            return False, "Slug只能包含小写字母、数字和连字符"
        
        # 检查slug是否已存在
        if Category.query.filter_by(slug=slug).first():
            return False, "Slug已存在"
        
        return True, ""
    
    def update_slug(self):
        """
        根据名称更新slug
        """
        new_slug = self.generate_slug(self.name)
        # 如果新slug与现有不同且不冲突，则更新
        if new_slug != self.slug:
            existing = Category.query.filter_by(slug=new_slug).first()
            if not existing or existing.id == self.id:
                self.slug = new_slug
    
    def can_delete(self):
        """
        检查是否可以删除分类
        
        Returns:
            tuple: (是否可以删除, 原因)
        """
        article_count = self.get_article_count()
        if article_count > 0:
            return False, f"分类下还有 {article_count} 篇文章，无法删除"
        return True, ""
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 分类信息字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'article_count': self.get_article_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'