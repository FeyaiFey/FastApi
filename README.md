# FastAPI 项目

这是一个基于 FastAPI 框架开发的现代化 Web 应用程序，采用了最佳实践和清晰的架构设计。

## 🚀 功能特点

- 基于 FastAPI 框架，提供高性能的异步 API
- 完整的项目结构，遵循最佳实践
- 集成了日志系统（使用 loguru）
- 支持 CORS 跨域请求
- 完善的异常处理机制
- 数据库集成（SQLAlchemy）
- 支持 Celery 任务队列
- 完整的测试框架（Pytest）
- 支持 JWT 认证
- 支持文件上传
- 支持数据库迁移（Alembic）

## 📁 项目结构

```
.
├── alembic/          # 数据库迁移文件
├── app/             # 主应用目录
│   ├── api/         # API 路由
│   ├── core/        # 核心配置
│   ├── crud/        # 数据库操作
│   ├── exceptions/  # 异常处理
│   ├── middlewares/ # 中间件
│   ├── models/      # 数据模型
│   ├── schemas/     # Pydantic 模型
│   ├── services/    # 业务逻辑
│   └── utils/       # 工具函数
├── static/          # 静态文件
├── tests/           # 测试文件
├── .env            # 环境变量
├── .gitignore      # Git 忽略文件
└── requirements.txt # 项目依赖
```

## 🛠️ 技术栈

- FastAPI 0.115.12
- SQLAlchemy 2.0.40
- Pydantic 2.10.6
- Celery 5.5.2
- Redis 2.0.1
- Uvicorn 0.33.0
- Pytest 8.3.5
- Loguru 0.7.3
- Python-jose 3.4.0 (JWT)
- Passlib 1.7.4 (密码哈希)
- Email-validator 2.2.0
- Python-multipart 0.0.20 (文件上传)

## 🚀 快速开始

1. 克隆项目
```bash
git clone [项目地址]
cd [项目目录]
```

2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

5. 运行数据库迁移
```bash
alembic upgrade head
```

6. 运行应用
```bash
python -m app.main
```

## 📝 API 文档

启动应用后，可以通过以下地址访问 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_file.py

# 运行带详细输出的测试
pytest -v
```

## 🔧 环境变量

项目使用 `.env` 文件进行配置，主要配置项包括：

```env
# 项目基本信息
PROJECT_NAME=FastAPI项目
VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000
API_V1_STR=/api/v1

# JWT配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=sqlite:///./sql_app.db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
```

配置说明：
- `PROJECT_NAME`: 项目名称
- `VERSION`: 项目版本
- `DEBUG`: 调试模式（True/False）
- `HOST`: 主机地址（0.0.0.0 表示允许所有IP访问）
- `PORT`: 端口号
- `API_V1_STR`: API 版本前缀
- `SECRET_KEY`: JWT 密钥（建议使用随机生成的强密钥）
- `ALGORITHM`: JWT 算法（推荐使用 HS256）
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 访问令牌过期时间（分钟）
- `DATABASE_URL`: 数据库连接 URL（支持 SQLite、PostgreSQL、MySQL 等）
- `REDIS_URL`: Redis 连接 URL
- `CELERY_BROKER_URL`: Celery 消息代理 URL

注意：
1. 请确保将敏感信息（如密钥、密码等）替换为您自己的值
2. 生产环境中建议将 `DEBUG` 设置为 `False`
3. 生产环境中建议使用更安全的数据库（如 PostgreSQL）而不是 SQLite

## 📄 许可证

MIT License

## 👥 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📞 联系方式

如有问题，请提交 Issue 或 Pull Request。
