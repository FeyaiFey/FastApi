from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import secrets

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """项目配置类"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # 允许额外的字段
    )
    
    # 项目基本信息
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}"
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_RETENTION: str = "30 days"
    LOG_ROTATION: str = "00:00"
    LOG_COMPRESSION: str = "zip"
    
    # 数据库配置
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_SERVER: str = "localhost"
    DB_DATABASE: str = "E10"
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DATABASE_ECHO: bool = False
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    POOL_PRE_PING: bool = True
    SQL_DEBUG: bool = False
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # WebSocket配置
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    # JWT配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    @property
    def DATABASE_URL(self) -> str:
        """构建数据库连接URL"""
        conn_str = (
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER};"
            f"DATABASE={self.DB_DATABASE};"
            f"UID={self.DB_USER};"
            f"PWD={self.DB_PASSWORD};"
            f"TrustServerCertificate=yes"
        )
        return f"mssql+pyodbc:///?odbc_connect={conn_str}"

# 创建全局配置对象
settings = Settings()

# 日志配置字典
def get_logging_config() -> Dict[str, Any]:
    """获取日志配置"""
    return {
        "handlers": [
            # 控制台输出
            {
                "sink": "sys.stdout",
                "format": settings.LOG_FORMAT,
                "level": settings.LOG_LEVEL,
            },
            # 文件输出
            {
                "sink": str(settings.LOG_DIR / f"fastapi_{settings.LOG_LEVEL.lower()}.log"),
                "format": settings.LOG_FORMAT,
                "level": settings.LOG_LEVEL,
                "rotation": settings.LOG_ROTATION,
                "retention": settings.LOG_RETENTION,
                "compression": settings.LOG_COMPRESSION,
            },
        ],
    }

# 数据库配置
def get_database_url() -> str:
    """获取数据库URL"""
    return settings.DATABASE_URL

# CORS配置
def get_cors_config() -> Dict[str, Any]:
    """获取CORS配置"""
    return {
        "allow_origins": settings.CORS_ORIGINS,
        "allow_credentials": settings.CORS_CREDENTIALS,
        "allow_methods": settings.CORS_METHODS,
        "allow_headers": settings.CORS_HEADERS,
    } 