import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.core.database import get_db, init_db, engine
from app.models.user import User
import uuid
import logging

# 配置日志
logger = logging.getLogger(__name__)

def get_random_username():
    """生成随机用户名"""
    return f"test_user_{uuid.uuid4().hex[:8]}"

@pytest.fixture(autouse=True)
def cleanup_database():
    """清理数据库"""
    try:
        # 在每个测试前初始化数据库
        init_db()
        
        # 使用上下文管理器清理数据
        with get_db() as db:
            db.query(User).delete()
            db.commit()
            logger.info("测试数据已清理")
    except Exception as e:
        logger.error(f"清理数据库失败: {str(e)}")
        raise
    yield

def test_database_connection():
    """测试数据库连接"""
    try:
        # 测试数据库引擎
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            assert result == 1
            logger.info("数据库连接测试成功")
    except SQLAlchemyError as e:
        pytest.fail(f"数据库连接测试失败: {str(e)}")

def test_database_transaction():
    """测试数据库事务管理"""
    username = get_random_username()
    
    with get_db() as db:
        try:
            # 创建用户
            user = User(
                username=username,
                email="test@example.com",
                hashed_password="test_password"
            )
            db.add(user)
            
            # 验证用户在会话中
            db.flush()
            saved_user = db.query(User).filter_by(username=username).first()
            assert saved_user is not None
            assert saved_user.email == "test@example.com"
            
            logger.info("事务测试成功")
            
        except SQLAlchemyError as e:
            pytest.fail(f"事务测试失败: {str(e)}")

def test_database_rollback():
    """测试数据库回滚"""
    username = get_random_username()
    
    # 第一个上下文：尝试创建用户但触发回滚
    try:
        with get_db() as db:
            user = User(
                username=username,
                email="rollback@example.com",
                hashed_password="test_password"
            )
            db.add(user)
            raise SQLAlchemyError("模拟错误触发回滚")
    except SQLAlchemyError:
        logger.info("预期的错误触发回滚")
    
    # 第二个上下文：验证回滚是否成功
    with get_db() as db:
        user = db.query(User).filter_by(username=username).first()
        assert user is None
        logger.info("回滚测试成功")

def test_database_context_manager():
    """测试数据库上下文管理器"""
    username = get_random_username()
    
    # 测试自动提交
    with get_db() as db:
        user = User(
            username=username,
            email="context@example.com",
            hashed_password="test_password"
        )
        db.add(user)
        logger.info("用户已添加到会话")
    
    # 验证提交是否成功
    with get_db() as db:
        saved_user = db.query(User).filter_by(username=username).first()
        assert saved_user is not None
        assert saved_user.email == "context@example.com"
        logger.info("上下文管理器测试成功")

def test_database_error_handling():
    """测试数据库错误处理"""
    username1 = get_random_username()
    username2 = get_random_username()
    
    # 创建第一个用户
    with get_db() as db:
        user1 = User(
            username=username1,
            email="error1@example.com",
            hashed_password="test_password"
        )
        db.add(user1)
    
    # 尝试创建重复的邮箱用户
    try:
        with get_db() as db:
            user2 = User(
                username=username2,
                email="error1@example.com",  # 重复的邮箱
                hashed_password="test_password"
            )
            db.add(user2)
        pytest.fail("应该抛出唯一约束错误")
    except SQLAlchemyError as e:
        logger.info(f"预期的错误被捕获: {str(e)}")
        
        # 验证第一个用户仍然存在
        with get_db() as db:
            user = db.query(User).filter_by(username=username1).first()
            assert user is not None
            assert user.email == "error1@example.com"
            logger.info("错误处理测试成功") 