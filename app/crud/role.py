from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from app.core.logger import get_logger
from app.exceptions.base import DatabaseError, NotFoundError

logger = get_logger("role.crud")

class RoleCRUD:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, role: RoleCreate) -> Role:
        """创建角色"""
        try:
            db_role = Role(**role.model_dump())
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
            logger.info(f"角色创建成功: {db_role.RoleName}")
            return db_role
        except SQLAlchemyError as e:
            logger.error(f"创建角色失败: {str(e)}")
            self.db.rollback()
            raise DatabaseError("创建角色失败")

    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """根据ID获取角色"""
        try:
            return self.db.query(Role).filter(Role.Id == role_id).first()
        except SQLAlchemyError as e:
            logger.error(f"查询角色失败: {str(e)}")
            raise DatabaseError("查询角色失败")

    async def get_by_name(self, role_name: str) -> Optional[Role]:
        """根据角色名称获取角色"""
        try:
            return self.db.query(Role).filter(Role.RoleName == role_name).first()
        except SQLAlchemyError as e:
            logger.error(f"查询角色失败: {str(e)}")
            raise DatabaseError("查询角色失败")

    async def get_by_code(self, role_code: str) -> Optional[Role]:
        """根据角色代码获取角色"""
        try:
            return self.db.query(Role).filter(Role.RoleCode == role_code).first()
        except SQLAlchemyError as e:
            logger.error(f"查询角色失败: {str(e)}")
            raise DatabaseError("查询角色失败")

    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[str] = None
    ) -> List[Role]:
        """获取角色列表"""
        try:
            query = self.db.query(Role)
            
            if status is not None:
                query = query.filter(Role.Status == status)
                
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"查询角色列表失败: {str(e)}")
            raise DatabaseError("查询角色列表失败")

    async def count(self, status: Optional[str] = None) -> int:
        """获取角色总数"""
        try:
            query = self.db.query(Role)
            
            if status is not None:
                query = query.filter(Role.Status == status)
                
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"统计角色数量失败: {str(e)}")
            raise DatabaseError("统计角色数量失败")

    async def update(self, role_id: uuid.UUID, role_update: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        try:
            db_role = await self.get_by_id(role_id)
            if not db_role:
                return None
                
            update_data = role_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_role, field, value)
                
            self.db.commit()
            self.db.refresh(db_role)
            logger.info(f"角色更新成功: {role_id}")
            return db_role
        except SQLAlchemyError as e:
            logger.error(f"更新角色失败: {str(e)}")
            self.db.rollback()
            raise DatabaseError("更新角色失败")

    async def delete(self, role_id: uuid.UUID) -> bool:
        """删除角色"""
        try:
            db_role = await self.get_by_id(role_id)
            if not db_role:
                return False
                
            self.db.delete(db_role)
            self.db.commit()
            logger.info(f"角色删除成功: {role_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"删除角色失败: {str(e)}")
            self.db.rollback()
            raise DatabaseError("删除角色失败")

    async def check_role_exists(self, role_name: str, role_code: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """检查角色名称或代码是否已存在"""
        try:
            query = self.db.query(Role).filter(
                and_(
                    (Role.RoleName == role_name) | (Role.RoleCode == role_code)
                )
            )
            
            if exclude_id:
                query = query.filter(Role.Id != exclude_id)
                
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"检查角色是否存在失败: {str(e)}")
            raise DatabaseError("检查角色失败")

def get_role_crud(db: Session) -> RoleCRUD:
    """获取角色CRUD实例"""
    return RoleCRUD(db) 