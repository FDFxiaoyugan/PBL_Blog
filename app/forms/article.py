"""
文章表单
Article Forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models.category import Category

class ArticleForm(FlaskForm):
    """
    文章创建/编辑表单
    
    实现需求:
    - 3.1: 用户创建新文章时保存文章标题、内容、分类和发布时间
    - 3.2: 用户提交空标题或内容时阻止发布并显示错误提示
    - 3.4: 用户编辑自己的文章时更新文章内容并保留修改时间
    """
    title = StringField('文章标题', validators=[
        DataRequired(message='文章标题不能为空'),
        Length(min=1, max=200, message='文章标题长度必须在1-200个字符之间')
    ])
    
    content = TextAreaField('文章内容', validators=[
        DataRequired(message='文章内容不能为空')
    ])
    
    summary = TextAreaField('文章摘要', validators=[
        Optional(),
        Length(max=500, message='文章摘要长度不能超过500个字符')
    ])
    
    category_id = SelectField('文章分类', coerce=int, validators=[Optional()])
    
    status = SelectField('发布状态', choices=[
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档')
    ], default='draft')
    
    submit = SubmitField('保存文章')
    
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        # 动态加载分类选项
        self.category_id.choices = [(0, '请选择分类')] + [
            (category.id, category.name) for category in Category.query.all()
        ]
    
    def validate_category_id(self, field):
        """验证分类ID"""
        if field.data and field.data > 0:
            category = Category.query.get(field.data)
            if not category:
                raise ValidationError('选择的分类不存在')

class ArticleSearchForm(FlaskForm):
    """
    文章搜索表单
    
    实现需求:
    - 6.2: 用户按分类筛选时显示该分类下的所有文章
    - 6.3: 用户搜索关键词时返回标题或内容包含关键词的文章
    """
    keyword = StringField('搜索关键词', validators=[
        Optional(),
        Length(max=100, message='搜索关键词长度不能超过100个字符')
    ])
    
    category_id = SelectField('分类筛选', coerce=int, validators=[Optional()])
    
    submit = SubmitField('搜索')
    
    def __init__(self, *args, **kwargs):
        super(ArticleSearchForm, self).__init__(*args, **kwargs)
        # 动态加载分类选项
        self.category_id.choices = [(0, '所有分类')] + [
            (category.id, category.name) for category in Category.query.all()
        ]

class ArticleDeleteForm(FlaskForm):
    """
    文章删除确认表单
    
    实现需求:
    - 3.5: 用户删除自己的文章时移除文章及其相关评论
    """
    article_id = HiddenField('文章ID', validators=[DataRequired()])
    submit = SubmitField('确认删除')