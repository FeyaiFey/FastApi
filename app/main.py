from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.middlewares.logging import LoggingMiddleware
from app.core.logger import get_logger
from app.core.config import Settings
from app.core.response import response_manager
from app.exceptions import register_exception_handlers
from app.api.v1.endpoints import auth, users, departments, roles, menus
from app.schemas.response import SuccessResponse

# 创建logger实例
logger = get_logger(name="main")

settings = Settings()

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="华芯微FastAPI后台管理项目,结合内外部数据,实现数据分析和处理",
    version=settings.VERSION,
    debug=settings.DEBUG,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 注册异常处理器
register_exception_handlers(app)

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
    app.include_router(
        roles.router,
        prefix=f"{settings.API_V1_STR}/roles",
        tags=["角色"]
    )
    app.include_router(
        menus.router,
        prefix=f"{settings.API_V1_STR}/menus",
        tags=["菜单"]
    )

# 注册路由
register_routers()

@app.get("/", response_model=SuccessResponse[dict])
async def root():
    """根路径，返回API信息"""
    return response_manager.success(
        data={
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        },
        message="API服务运行正常"
    )

@app.get("/hello/{name}", response_model=SuccessResponse[dict])
async def say_hello(name: str):
    logger.info(f"Hello endpoint called with name: {name}")
    return response_manager.success(
        data={"message": f"Hello {name}"},
        message="问候成功"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
