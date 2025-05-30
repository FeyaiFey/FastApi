from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.middlewares.logging import LoggingMiddleware
from app.core.logger import get_logger
from app.core.config import Settings, get_cors_config
from app.exceptions import register_exception_handlers
from app.api.v1.endpoints import auth, users, departments

# 创建logger实例
logger = get_logger(name="main")

settings = Settings()

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Application",
    version=settings.VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 注册异常处理器
register_exception_handlers(app)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    **get_cors_config()
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=settings.STATIC_ROOT), name="static")

def register_routers() -> None:
    """注册所有路由"""
    # API v1 路由
    app.include_router(
        auth.router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["认证"]
    )
    app.include_router(
        users.router,
        prefix=f"{settings.API_V1_STR}/users",
        tags=["用户"]
    )
    app.include_router(
        departments.router,
        prefix=f"{settings.API_V1_STR}/departments",
        tags=["部门"]
    )

# 注册路由
register_routers()

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/hello/{name}")
async def say_hello(name: str):
    logger.info(f"Hello endpoint called with name: {name}")
    return {"message": f"Hello {name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
