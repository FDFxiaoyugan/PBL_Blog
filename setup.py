#!/usr/bin/env python3
"""
博客系统安装脚本
Blog System Setup Script
"""

import os
import subprocess
import sys

def create_virtual_environment():
    """创建虚拟环境"""
    if not os.path.exists('venv'):
        print("创建虚拟环境...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
        print("虚拟环境创建完成")
    else:
        print("虚拟环境已存在")

def install_dependencies():
    """安装依赖"""
    print("安装项目依赖...")
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # Unix/Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'])
    print("依赖安装完成")

def main():
    """主函数"""
    print("博客系统环境设置")
    print("=" * 30)
    
    create_virtual_environment()
    install_dependencies()
    
    print("\n设置完成！")
    print("激活虚拟环境:")
    if os.name == 'nt':
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")

if __name__ == '__main__':
    main()