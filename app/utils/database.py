"""
数据库工具函数
Database Utility Functions
"""
from app import db
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

def safe_commit():
    """
    安全提交数据库事务
    
    Returns:
        bool: 提交是否成功
    """
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database commit failed: {e}")
        return False

def safe_delete(obj):
    """
    安全删除数据库对象
    
    Args:
        obj: 要删除的数据库对象
        
    Returns:
        bool: 删除是否成功
    """
    try:
        db.session.delete(obj)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database delete failed: {e}")
        return False

def get_or_create(model, **kwargs):
    """
    获取或创建数据库对象
    
    Args:
        model: 数据库模型类
        **kwargs: 查询条件
        
    Returns:
        tuple: (对象实例, 是否新创建)
    """
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        if safe_commit():
            return instance, True
        else:
            return None, False

def paginate_query(query, page=1, per_page=10):
    """
    分页查询
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码
        per_page: 每页数量
        
    Returns:
        Pagination: 分页对象
    """
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )