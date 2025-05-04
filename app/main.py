from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.logging import LoggingMiddleware
from app.core.logger import get_logger
from app.core.config import Settings, get_cors_config
from app.exceptions import register_exception_handlers

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

# 注册路由

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

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
