"""
评论表单
Comment Forms
"""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    """
    评论表单
    
    实现需求:
    - 4.1: 用户对文章发表评论时保存评论内容、作者和时间戳
    - 4.2: 用户提交空评论时阻止提交并显示错误提示
    """
    content = TextAreaField('评论内容', 
                           validators=[
                               DataRequired(message='评论内容不能为空'),
                               Length(min=1, max=1000, message='评论内容长度必须在1-1000个字符之间')
                           ],
                           render_kw={
                               'placeholder': '请输入您的评论...',
                               'rows': 4,
                               'class': 'form-control'
                           })
    
    article_id = HiddenField('文章ID', validators=[DataRequired()])
    parent_id = HiddenField('父评论ID')  # 用于回复评论
    
    submit = SubmitField('发表评论', render_kw={'class': 'btn btn-primary'})

class CommentReplyForm(FlaskForm):
    """
    回复评论表单
    """
    content = TextAreaField('回复内容', 
                           validators=[
                               DataRequired(message='回复内容不能为空'),
                               Length(min=1, max=1000, message='回复内容长度必须在1-1000个字符之间')
                           ],
                           render_kw={
                               'placeholder': '请输入您的回复...',
                               'rows': 3,
                               'class': 'form-control'
                           })
    
    article_id = HiddenField('文章ID', validators=[DataRequired()])
    parent_id = HiddenField('父评论ID', validators=[DataRequired()])
    
    submit = SubmitField('发表回复', render_kw={'class': 'btn btn-sm btn-primary'})

class CommentDeleteForm(FlaskForm):
    """
    删除评论表单
    
    实现需求:
    - 4.4: 用户删除自己的评论时移除该评论
    """
    submit = SubmitField('确认删除', render_kw={'class': 'btn btn-sm btn-danger'})

class CommentModerationForm(FlaskForm):
    """
    评论审核表单（管理员使用）
    """
    action = HiddenField('操作', validators=[DataRequired()])
    submit = SubmitField('执行操作', render_kw={'class': 'btn btn-sm btn-primary'})