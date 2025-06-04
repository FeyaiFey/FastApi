from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User
from app.core.security import verify_password
from app.crud.user import user as crud_user
from app.core.database import get_db
from app.core.logger import get_logger
from app.exceptions.base import DatabaseError

logger = get_logger("auth.crud")

class CRUDAuth:
    async def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        验证用户
        :param db: 数据库会话
        :param email: 用户邮箱
        :param password: 用户密码
        :return: 用户对象或None
        """
        try:
            user = await crud_user.get_by_email(db, email=email)
            if not user:
                logger.warning(f"用户邮箱不存在: {email}")
                return None
            if not await verify_password(password, user.PasswordHash):
                logger.warning(f"用户密码错误: {email}")
                return None
            return user
        except SQLAlchemyError as e:
            logger.error(f"认证时数据库查询错误: {str(e)}")
            raise DatabaseError("认证失败")
    
    async def is_active(self, user: User) -> bool:
        """
        检查用户是否激活
        :param user: 用户对象
        :return: 是否激活
        """
        return user.Status == "1"

auth = CRUDAuth() 