# 博客系统设计文档

## 概述

博客系统是一个基于Web的内容管理平台，支持用户注册、文章发布、评论互动和管理员管理功能。系统采用MVC架构模式，前后端分离设计，确保良好的可维护性和扩展性。

## 架构

### 系统架构
- **前端**: HTML + CSS + JavaScript (可选Vue.js/React)
- **后端**: Python Flask / Node.js Express / PHP Laravel
- **数据库**: MySQL
- **会话管理**: Session/JWT Token
- **密码加密**: bcrypt

### 技术栈选择
- **开发语言**: Python (推荐) / JavaScript / PHP
- **Web框架**: Flask (轻量级，适合学习)
- **数据库**: MySQL (符合评分要求)
- **前端框架**: Bootstrap (响应式UI)
- **版本控制**: Git + GitHub

## 组件和接口

### 核心组件

#### 1. 用户认证模块 (AuthModule)
- **注册服务** (RegistrationService)
  - 输入验证
  - 密码加密
  - 用户创建
- **登录服务** (LoginService)
  - 凭据验证
  - 会话管理
  - 权限检查

#### 2. 文章管理模块 (ArticleModule)
- **文章服务** (ArticleService)
  - CRUD操作
  - 分类管理
  - 搜索功能
- **评论服务** (CommentService)
  - 评论CRUD
  - 关联管理

#### 3. 用户管理模块 (UserModule)
- **用户服务** (UserService)
  - 个人资料管理
  - 用户统计
- **管理员服务** (AdminService)
  - 用户管理
  - 内容审核

#### 4. 权限控制模块 (AuthorizationModule)
- **角色验证** (RoleValidator)
- **访问控制** (AccessController)

### API接口设计

#### 用户认证接口
```
POST /api/register - 用户注册
POST /api/login - 用户登录
POST /api/logout - 用户登出
GET /api/profile - 获取用户信息
PUT /api/profile - 更新用户信息
```

#### 文章管理接口
```
GET /api/articles - 获取文章列表
POST /api/articles - 创建文章
GET /api/articles/:id - 获取文章详情
PUT /api/articles/:id - 更新文章
DELETE /api/articles/:id - 删除文章
```

#### 评论管理接口
```
GET /api/articles/:id/comments - 获取文章评论
POST /api/articles/:id/comments - 添加评论
DELETE /api/comments/:id - 删除评论
```

#### 管理员接口
```
GET /api/admin/users - 获取用户列表
DELETE /api/admin/users/:id - 删除用户
GET /api/admin/articles - 管理文章
GET /api/admin/comments - 管理评论
```

## 数据模型

### 数据库表设计

#### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 2. 管理员表 (admins)
```sql
CREATE TABLE admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 3. 分类表 (categories)
```sql
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    slug VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. 文章表 (articles)
```sql
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    summary VARCHAR(500),
    author_id INT NOT NULL,
    category_id INT,
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_author (author_id),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_published (published_at)
);
```

#### 5. 评论表 (comments)
```sql
CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content TEXT NOT NULL,
    author_id INT NOT NULL,
    article_id INT NOT NULL,
    parent_id INT NULL,
    status ENUM('approved', 'pending', 'rejected') DEFAULT 'approved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
    INDEX idx_article (article_id),
    INDEX idx_author (author_id),
    INDEX idx_parent (parent_id)
);
```

### 数据关系
- 用户 (1:N) 文章
- 用户 (1:N) 评论
- 文章 (1:N) 评论
- 分类 (1:N) 文章
- 用户 (1:1) 管理员 (可选)
- 评论 (1:N) 子评论 (自关联)

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的正式声明。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性反思

在分析所有可测试属性后，我识别出以下可以合并或优化的冗余属性：
- 多个访问控制属性可以合并为统一的权限验证属性
- 类似的CRUD操作可以合并为通用的数据操作属性
- 输入验证属性可以统一处理

### 核心正确性属性

**属性 1: 用户注册数据完整性**
*对于任何* 有效的注册数据，系统应该验证所有必需字段，加密存储密码，并创建唯一的用户账号
**验证: 需求 1.1, 1.3**

**属性 2: 重复数据防护**
*对于任何* 已存在的用户名或邮箱，系统应该阻止重复注册并返回适当的错误信息
**验证: 需求 1.2**

**属性 3: 登录凭据验证**
*对于任何* 用户凭据，系统应该正确验证用户名/密码组合，成功时创建会话，失败时返回错误
**验证: 需求 2.1, 2.2**

**属性 4: 会话管理一致性**
*对于任何* 过期或无效会话，系统应该自动注销用户并重定向到登录页面
**验证: 需求 2.4, 2.5**

**属性 5: 文章数据完整性**
*对于任何* 有效的文章数据，系统应该保存所有必需字段（标题、内容、作者、时间戳）并正确关联分类
**验证: 需求 3.1**

**属性 6: 输入验证一致性**
*对于任何* 空或无效的输入（文章标题、内容、评论），系统应该阻止提交并显示相应错误信息
**验证: 需求 3.2, 4.2**

**属性 7: 内容可见性规则**
*对于任何* 成功发布的内容（文章或评论），系统应该在相应的列表或页面中立即显示该内容
**验证: 需求 3.3, 4.3**

**属性 8: 级联删除一致性**
*对于任何* 删除操作（文章或用户），系统应该移除主体及其所有相关联的从属数据
**验证: 需求 3.5, 5.2**

**属性 9: 权限控制严格性**
*对于任何* 需要特定权限的操作，系统应该验证用户权限，允许授权用户访问，拒绝未授权用户并重定向
**验证: 需求 4.5, 5.5**

**属性 10: 管理员权限完整性**
*对于任何* 管理员用户，系统应该允许对所有用户内容（文章、评论、用户）进行完整的CRUD操作
**验证: 需求 5.3, 5.4**

**属性 11: 搜索结果准确性**
*对于任何* 搜索查询或分类筛选，系统应该返回所有匹配条件的结果且仅返回匹配的结果
**验证: 需求 6.2, 6.3**

**属性 12: 分页功能一致性**
*对于任何* 超过页面容量的数据列表，系统应该提供分页导航并正确分割数据
**验证: 需求 6.4**

**属性 13: 用户数据更新完整性**
*对于任何* 用户信息修改操作，系统应该验证输入、更新数据库记录并保持数据一致性
**验证: 需求 7.2, 7.3**

**属性 14: 用户内容关联正确性**
*对于任何* 用户，查看其个人内容时应该显示且仅显示该用户创建的文章和评论
**验证: 需求 7.4, 7.5**

## 错误处理

### 错误类型和处理策略

#### 1. 输入验证错误
- **空值错误**: 必填字段为空
- **格式错误**: 邮箱格式、密码强度等
- **长度错误**: 字段超出限制
- **处理**: 返回具体错误信息，保持用户输入状态

#### 2. 业务逻辑错误
- **重复数据**: 用户名、邮箱已存在
- **权限不足**: 访问未授权资源
- **资源不存在**: 访问不存在的文章或用户
- **处理**: 返回友好错误提示，记录日志

#### 3. 系统错误
- **数据库连接失败**
- **文件操作失败**
- **网络超时**
- **处理**: 显示通用错误页面，记录详细日志，通知管理员

#### 4. 安全错误
- **SQL注入尝试**
- **XSS攻击**
- **CSRF攻击**
- **处理**: 阻止请求，记录安全日志，可能的IP封禁

### 错误响应格式
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "用户输入验证失败",
        "details": {
            "email": "邮箱格式不正确",
            "password": "密码长度至少8位"
        }
    }
}
```

## 测试策略

### 双重测试方法

本项目采用单元测试和基于属性的测试相结合的方法：

#### 单元测试
- **目的**: 验证具体示例、边缘情况和错误条件
- **覆盖范围**: 
  - 特定功能的正确行为示例
  - 组件间集成点
  - 重要边缘情况（空输入、边界值）
- **工具**: pytest (Python) / Jest (JavaScript) / PHPUnit (PHP)

#### 基于属性的测试
- **目的**: 验证应该在所有输入中保持的通用属性
- **覆盖范围**:
  - 数据完整性属性
  - 业务规则一致性
  - 权限控制正确性
- **工具**: Hypothesis (Python) / fast-check (JavaScript) / QuickCheck (PHP)
- **配置**: 每个属性测试运行最少100次迭代
- **标记格式**: `**Feature: blog-system, Property {number}: {property_text}**`

#### 测试要求
- 每个正确性属性必须由单个基于属性的测试实现
- 每个基于属性的测试必须明确引用设计文档中的正确性属性
- 单元测试和属性测试是互补的：单元测试捕获具体错误，属性测试验证通用正确性
- 属性测试应该尽可能避免使用模拟，以保持简单性
- 测试生成器应该智能地约束到输入空间

### 测试分类
1. **功能测试**: 验证核心业务功能
2. **集成测试**: 验证组件间交互
3. **安全测试**: 验证权限控制和安全措施
4. **性能测试**: 验证响应时间和并发处理
5. **用户界面测试**: 验证前端交互和显示

### 测试数据管理
- 使用测试数据库，与生产环境隔离
- 每次测试前重置数据状态
- 使用工厂模式生成测试数据
- 覆盖正常数据、边界数据和异常数据