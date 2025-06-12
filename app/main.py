import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from app.middlewares.logging import LoggingMiddleware
from app.core.logger import get_logger
from app.core.exceptions import (
    CustomException,
    custom_exception_handler,
    validation_exception_handler,
    internal_exception_handler
)
from app.schemas.response import ResponseHandler
from app.api.v1.endpoints import auth, departments, roles, users, email

# 创建logger实例
logger = get_logger(name="main")

# 创建FastAPI应用
app = FastAPI(
    title=os.getenv('PROJECT_NAME', "华芯微FastAPI后台管理系统"),
    description="华芯微FastAPI后台管理项目,结合内外部数据,实现数据分析和处理",
    version=os.getenv('VERSION', "1.0.0"),
    debug=os.getenv('DEBUG', False),
    openapi_url=f"{os.getenv('API_V1_STR', '/api/v1')}/openapi.json"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['Content-Disposition']
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 注册异常处理器
app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth.router, prefix=f"{os.getenv('API_V1_STR', '/api/v1')}/auth", tags=["认证"])
app.include_router(users.router, prefix=f"{os.getenv('API_V1_STR', '/api/v1')}/users", tags=["用户"])
app.include_router(departments.router, prefix=f"{os.getenv('API_V1_STR', '/api/v1')}/departments", tags=["部门"])
app.include_router(roles.router, prefix=f"{os.getenv('API_V1_STR', '/api/v1')}/roles", tags=["角色"])
app.include_router(email.router, prefix=f"{os.getenv('API_V1_STR', '/api/v1')}/email", tags=["邮箱"])

@app.get("/")
async def read_root():
    """健康检查接口"""
    return ResponseHandler.success(data={"status": "ok"}, message="服务正在运行")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv('HOST', "0.0.0.0"),
        port=int(os.getenv('PORT', 8000)),
        reload=os.getenv('DEBUG', False)
    )