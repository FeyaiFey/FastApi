from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool
from app.core.config import settings
from app.core.logger import get_logger
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT,
    pool_recycle=settings.POOL_RECYCLE,
    pool_pre_ping=settings.POOL_PRE_PING,
    echo=settings.SQL_DEBUG
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # 防止提交后对象过期
)

# 创建基类
Base = declarative_base()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    数据库会话上下文管理器
    
    使用示例:
    ```python
    with get_db() as db:
        db.add(user)
        db.commit()
    ```
    
    如果发生异常，事务会自动回滚
    """
    session: Optional[Session] = None
    try:
        session = SessionLocal()
        yield session
        session.commit()
        logger.info("数据库事务已提交")
    except SQLAlchemyError as e:
        if session:
            session.rollback()
            logger.error(f"数据库事务已回滚: {str(e)}")
        raise
    except Exception as e:
        if session:
            session.rollback()
            logger.error(f"发生未知错误，数据库事务已回滚: {str(e)}")
        raise
    finally:
        if session:
            session.close()
            logger.debug("数据库会话已关闭")

def init_db() -> None:
    """初始化数据库"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI 依赖注入使用的数据库会话
    
    使用示例:
    ```python
    @app.get("/users/")
    def get_users(db: Session = Depends(get_db_session)):
        return db.query(User).all()
    ```
    """
    with get_db() as session:
        yield session 