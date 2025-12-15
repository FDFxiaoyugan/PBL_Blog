"""
基础功能测试
Basic Functionality Tests
"""
import pytest
from app import create_app

def test_app_creation():
    """测试应用创建"""
    app = create_app('testing')
    assert app is not None
    assert app.config['TESTING'] is True

def test_app_routes(client):
    """测试基础路由"""
    # 测试首页
    response = client.get('/')
    assert response.status_code == 200
    
    # 测试登录页面
    response = client.get('/auth/login')
    assert response.status_code == 200
    
    # 测试注册页面
    response = client.get('/auth/register')
    assert response.status_code == 200