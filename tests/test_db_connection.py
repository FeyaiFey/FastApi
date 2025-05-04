import pytest
from sqlalchemy import text
from app.core.database import get_db, init_db
from app.core.config import settings

def test_database_connection():
    """测试数据库连接"""
    try:
        # 初始化数据库
        init_db()
        
        # 测试连接
        with get_db() as db:
            # 执行简单查询
            result = db.execute(text("SELECT 1")).scalar()
            assert result == 1
            
            # 测试数据库名称
            db_name = db.execute(text("SELECT DB_NAME()")).scalar()
            assert db_name == settings.DB_DATABASE
            
            print(f"成功连接到数据库: {settings.DB_DATABASE}")
            print(f"服务器: {settings.DB_SERVER}")
            print(f"驱动: {settings.DB_DRIVER}")
            
    except Exception as e:
        pytest.fail(f"数据库连接测试失败: {str(e)}")

if __name__ == "__main__":
    test_database_connection() 