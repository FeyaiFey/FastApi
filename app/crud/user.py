from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import get_password_hash
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("user.crud")

class CRUDUser:
    async def get_by_id(self, db: Session, id: uuid.UUID) -> Optional[User]:
        """
        根据ID获取用户
        :param db: 数据库会话
        :param id: 用户ID
        :return: 用户对象或None
        """
        try:
            return db.query(User).get(id)
        except SQLAlchemyError as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise
    
    async def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        :param db: 数据库会话
        :param email: 用户邮箱
        :return: 用户对象或None
        """
        try:
            return db.query(User).filter(User.Email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise
    
    async def create(self, db: Session, *, obj_in: UserRegister) -> Optional[User]:
        """
        创建用户
        :param db: 数据库会话
        :param obj_in: 用户创建数据
        :return: 创建的用户对象
        """
        try:
            db_obj = User(
                Id=uuid.uuid1(),
                UserName=obj_in.UserName,
                Email=obj_in.Email,
                PasswordHash=await get_password_hash(obj_in.Password),
                DepartmentId=obj_in.DepartmentId,
                Role="普通用户",
                Status="1",  # 默认启用
                AvatarUrl=settings.HOST + '/static/uploads/avatars/default.png',
                CreatedAt=datetime.now(),
                UpdatedAt=datetime.now()
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"用户创建成功: {db_obj.UserName}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"创建用户失败: {str(e)}")
            raise
    
    async def delete(self, db: Session, *, id: uuid.UUID) -> Optional[User]:
        """
        删除用户
        :param db: 数据库会话
        :param id: 用户ID
        :return: 被删除的用户对象
        """
        try:
            obj = db.query(User).get(id)
            if not obj:
                raise ValueError(f"用户不存在: {id}")
            db.delete(obj)
            db.commit()
            logger.info(f"用户删除成功: {id}")
            return obj
        except SQLAlchemyError as e:
            logger.error(f"删除用户失败: {str(e)}")
            raise
    
    async def update_avatar(self, db: Session, *, id: uuid.UUID, avatar_url: str) -> Optional[User]:
        """
        更新用户头像
        :param db: 数据库会话
        :param id: 用户ID
        :param avatar_url: 新头像URL
        :return: 更新后的用户对象
        """
        try:
            user = db.query(User).get(id)
            if not user:
                raise ValueError(f"用户不存在: {id}")
            user.AvatarUrl = avatar_url
            db.commit()
            db.refresh(user)
            logger.info(f"用户头像更新成功: {id}")
            return user
        except SQLAlchemyError as e:
            logger.error(f"更新用户头像失败: {str(e)}")
            raise

user = CRUDUser() 