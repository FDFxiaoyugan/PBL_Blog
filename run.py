#!/usr/bin/env python3
"""
博客系统启动文件
Blog System Entry Point
"""
import os
from app import create_app

# 获取配置环境
config_name = os.environ.get('FLASK_ENV') or 'development'

# 创建应用实例
app = create_app(config_name)

if __name__ == '__main__':
    # 开发环境下启动应用
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )