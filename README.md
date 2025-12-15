# 博客系统 (Blog System)

基于Flask的博客管理系统，支持用户注册、文章发布、评论互动等功能。

## 功能特性

- 用户注册和登录
- 文章发布和管理
- 评论系统
- 管理员功能
- 响应式界面

## 技术栈

- **后端**: Python Flask
- **数据库**: MySQL
- **前端**: HTML + CSS + JavaScript + Bootstrap
- **测试**: pytest + Hypothesis

## 快速开始

### 1. 环境准备

确保已安装以下软件：
- Python 3.8+
- MySQL 5.7+
- Git

### 2. 项目设置

```bash
# 克隆项目
git clone <repository-url>
cd blog-system

# 运行设置脚本
python setup.py

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入数据库配置
```

### 4. 启动应用

```bash
python run.py
```

访问 http://127.0.0.1:5000 查看应用。

## 项目结构

```
blog-system/
├── app/                    # 应用主目录
│   ├── models/            # 数据模型
│   ├── routes/            # 路由处理
│   ├── services/          # 业务逻辑
│   ├── templates/         # HTML模板
│   └── static/            # 静态文件
├── config/                # 配置文件
├── tests/                 # 测试文件
├── venv/                  # 虚拟环境
├── requirements.txt       # 依赖列表
├── run.py                # 启动文件
└── README.md             # 项目说明
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py

# 运行属性测试
pytest tests/test_properties.py
```

### 数据库操作

```bash
# 创建数据库表
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License