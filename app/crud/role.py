from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.models.role import Role
from app.core.logger import get_logger
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    CustomException
)

logger = get_logger("role.crud")

class RoleCRUD:

    async def get_by_id(self, db: Session, role_id: uuid.UUID) -> Optional[Role]:
        """根据ID获取角色"""
        try:
            role = db.query(Role).filter(Role.Id == role_id).first()
            if not role:
                raise NotFoundException(f"角色不存在: {role_id}")
            return role
        except CustomException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"查询角色失败: {str(e)}")
            raise BadRequestException("查询角色失败，请稍后重试")
    
    async def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        try:
            role = db.query(Role).filter(Role.RoleName == name).first()
            if not role:
                raise NotFoundException(f"角色不存在: {name}")
            return role
        except CustomException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"查询角色失败: {str(e)}")
            raise BadRequestException("查询角色失败，请稍后重试")

role = RoleCRUD()