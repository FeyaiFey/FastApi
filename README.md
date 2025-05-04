# FastAPI 项目

这是一个基于 FastAPI 框架开发的现代化 Web 应用程序，采用了最佳实践和清晰的架构设计。

## 🚀 功能特点

- 基于 FastAPI 框架，提供高性能的异步 API
- 完整的项目结构，遵循最佳实践
- 集成了日志系统
- 支持 CORS 跨域请求
- 异常处理机制
- 数据库集成（SQLAlchemy）
- 支持 Celery 任务队列
- 完整的测试框架

## 📁 项目结构

```
.
├── alembic/          # 数据库迁移文件
├── app/             # 主应用目录
│   ├── api/         # API 路由
│   ├── core/        # 核心配置
│   ├── exceptions/  # 异常处理
│   ├── middlewares/ # 中间件
│   ├── models/      # 数据模型
│   ├── schemas/     # Pydantic 模型
│   ├── services/    # 业务逻辑
│   └── utils/       # 工具函数
├── logs/            # 日志文件
├── tests/           # 测试文件
└── requirements.txt # 项目依赖
```

## 🛠️ 技术栈

- FastAPI 0.115.12
- SQLAlchemy 2.0.40
- Pydantic 2.10.6
- Celery 5.5.2
- Redis 6.0.0
- Uvicorn 0.33.0
- Pytest 8.3.5

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

4. 运行应用
```bash
python -m app.main
```

## 📝 API 文档

启动应用后，可以通过以下地址访问 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 运行测试

```bash
pytest
```

## 🔧 环境变量

项目使用 `.env` 文件进行配置，主要配置项包括：
- `PROJECT_NAME`: 项目名称
- `VERSION`: 项目版本
- `DEBUG`: 调试模式
- `HOST`: 主机地址
- `PORT`: 端口号
- `API_V1_STR`: API 版本前缀

## 📄 许可证

[添加许可证信息]

## 👥 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

[添加联系方式]
