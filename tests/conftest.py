import pytest
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base, get_db, SessionLocal, init_db
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# 测试数据库URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("E10", "E10_test")

def create_test_database():
    """创建测试数据库"""
    try:
        # 连接到master数据库
        master_engine = create_engine(
            settings.DATABASE_URL.replace("E10", "master"),
            echo=settings.DATABASE_ECHO
        )
        with master_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text("SELECT database_id FROM sys.databases WHERE Name = 'E10_test'"))
            if not result.scalar():
                # 创建测试数据库
                conn.execute(text("CREATE DATABASE E10_test"))
                logger.info("测试数据库创建成功")
    except SQLAlchemyError as e:
        logger.error(f"创建测试数据库失败: {str(e)}")
        raise

@pytest.fixture(scope="session")
def api_url():
    """返回API的基础URL"""
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def test_data():
    """测试数据"""
    return {
        "test_user": "test",
        "expected_message": "Hello test"
    }

@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    try:
        create_test_database()
        engine = create_engine(
            TEST_DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        return engine
    except SQLAlchemyError as e:
        logger.error(f"创建测试数据库引擎失败: {str(e)}")
        raise

@pytest.fixture(scope="session")
def test_db(test_engine):
    """创建测试数据库表"""
    try:
        Base.metadata.create_all(bind=test_engine)
        logger.info("测试数据库表创建成功")
        yield test_engine
        Base.metadata.drop_all(bind=test_engine)
        logger.info("测试数据库表清理成功")
    except SQLAlchemyError as e:
        logger.error(f"测试数据库操作失败: {str(e)}")
        raise

@pytest.fixture(scope="function")
def db_session():
    """创建数据库会话的 fixture"""
    # 初始化数据库
    init_db()
    
    # 创建会话
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close() 