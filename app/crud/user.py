from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime

from app.models.user import User
from app.models.role import Role
from app.models.department import Department
from app.schemas.user import UserRegister, UserCreate, UserUpdate,UserInfo
from app.core.security import get_password_hash
from app.core.logger import get_logger
from app.core.config import settings
from app.exceptions.base import DatabaseError, NotFoundError

logger = get_logger("user.crud")

class CRUDUser:
    async def get_by_id(self, db: Session, id: uuid.UUID, include_relations: bool = False) -> Optional[User]:
        """
        根据ID获取用户
        :param db: 数据库会话
        :param id: 用户ID
        :param include_relations: 是否包含关联信息（角色、部门）
        :return: 用户对象或None
        """
        try:
            query = db.query(User)
            if include_relations:
                query = query.options(
                    joinedload(User.role),
                    joinedload(User.department)
                )
            return query.filter(User.Id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise DatabaseError("查询用户失败")
    
    async def get_by_email(self, db: Session, email: str, include_relations: bool = False) -> Optional[User]:
        """
        根据邮箱获取用户
        :param db: 数据库会话
        :param email: 用户邮箱
        :param include_relations: 是否包含关联信息（角色、部门）
        :return: 用户对象或None
        """
        try:
            query = db.query(User)
            if include_relations:
                query = query.options(
                    joinedload(User.role),
                    joinedload(User.department)
                )
            return query.filter(User.Email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise DatabaseError("查询用户失败")

    async def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        include_relations: bool = False
    ) -> List[User]:
        """
        获取用户列表
        :param db: 数据库会话
        :param skip: 跳过数量
        :param limit: 限制数量
        :param include_relations: 是否包含关联信息（角色、部门）
        :return: 用户列表
        """
        try:
            query = db.query(User)
            if include_relations:
                query = query.options(
                    joinedload(User.role),
                    joinedload(User.department)
                )
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"查询用户列表失败: {str(e)}")
            raise DatabaseError("查询用户列表失败")
    
    async def create(self, db: Session, *, obj_in: UserRegister) -> Optional[User]:
        """
        创建用户
        :param db: 数据库会话
        :param obj_in: 用户创建数据
        :param default_role_id: 默认角色ID
        :return: 创建的用户对象
        """
        try:
            db_obj = User(
                Id=uuid.uuid1(),
                UserName=obj_in.UserName,
                Email=obj_in.Email,
                PasswordHash=await get_password_hash(obj_in.Password),
                DepartmentId=obj_in.DepartmentId,
                RoleId="24EAFD77-81D8-4DB9-8867-BB3F4A823B36",  # 使用传入的角色ID或默认角色ID
                Status="1",  # 默认启用
                AvatarUrl='http://127.0.0.1:8000/static/uploads/avatars/default.png',
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
            db.rollback()
            raise DatabaseError("创建用户失败")

    async def create_user(self, db: Session, *, obj_in: UserCreate) -> Optional[User]:
        """
        创建用户（使用新的UserCreate schema）
        :param db: 数据库会话
        :param obj_in: 用户创建数据
        :return: 创建的用户对象
        """
        try:
            db_obj = User(
                UserName=obj_in.UserName,
                Email=obj_in.Email,
                PasswordHash=await get_password_hash(obj_in.Password),
                DepartmentId=obj_in.DepartmentId,
                RoleId=obj_in.RoleId,
                Status=obj_in.Status,
                AvatarUrl=obj_in.AvatarUrl,
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
            db.rollback()
            raise DatabaseError("创建用户失败")

    async def update(self, db: Session, *, id: uuid.UUID, obj_in: UserUpdate) -> Optional[User]:
        """
        更新用户
        :param db: 数据库会话
        :param id: 用户ID
        :param obj_in: 更新数据
        :return: 更新后的用户对象
        """
        try:
            user = db.query(User).filter(User.Id == id).first()
            if not user:
                raise NotFoundError(f"用户不存在: {id}")
            
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.UpdatedAt = datetime.now()
            db.commit()
            db.refresh(user)
            logger.info(f"用户更新成功: {id}")
            return user
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"更新用户失败: {str(e)}")
            db.rollback()
            raise DatabaseError("更新用户失败")
    
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
                raise NotFoundError(f"用户不存在: {id}")
            db.delete(obj)
            db.commit()
            logger.info(f"用户删除成功: {id}")
            return obj
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"删除用户失败: {str(e)}")
            db.rollback()
            raise DatabaseError("删除用户失败")
    
    async def update_avatar(self, db: Session, *, id: uuid.UUID, avatar_url: str) -> Optional[User]:
        """
        更新用户头像
        :param db: 数据库会话
        :param id: 用户ID
        :param avatar_url: 头像URL
        :return: 更新后的用户对象
        """
        try:
            user = db.query(User).filter(User.Id == id).first()
            if not user:
                raise NotFoundError(f"用户不存在: {id}")
            
            user.AvatarUrl = avatar_url
            user.UpdatedAt = datetime.now()
            db.commit()
            db.refresh(user)
            logger.info(f"用户头像更新成功: {id}")
            return user
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"更新用户头像失败: {str(e)}")
            db.rollback()
            raise DatabaseError("更新用户头像失败")
    
    async def count(self, db: Session) -> int:
        """
        获取用户总数
        :param db: 数据库会话
        :return: 用户总数
        """
        try:
            return db.query(User).count()
        except SQLAlchemyError as e:
            logger.error(f"统计用户数量失败: {str(e)}")
            raise DatabaseError("统计用户数量失败")

user = CRUDUser() 