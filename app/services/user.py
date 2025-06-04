from typing import Optional, List
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserRegister, UserCreate, UserUpdate, User as UserSchema
from app.crud.user import user as crud_user
from app.services.role import role_service
from app.utils.file_handler import FileHandler
from app.core.logger import get_logger
from app.exceptions.base import ValidationError, NotFoundError

logger = get_logger(__name__)

class UserService:
    
    async def get_user(self, db: Session, user_id: UUID, include_relations: bool = False) -> Optional[User]:
        """获取用户信息"""
        return await crud_user.get_by_id(db, id=user_id, include_relations=include_relations)
    
    async def get_user_by_email(self, db: Session, email: str, include_relations: bool = False) -> Optional[User]:
        """根据邮箱获取用户"""
        return await crud_user.get_by_email(db, email=email, include_relations=include_relations)
    
    async def get_users(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        include_relations: bool = False
    ) -> List[User]:
        """获取用户列表"""
        return await crud_user.get_multi(
            db, 
            skip=skip, 
            limit=limit, 
            include_relations=include_relations
        )
    
    async def create_user(self, db: Session, user_in: UserRegister) -> User:
        """创建用户（注册用）"""
        # 检查邮箱是否已存在
        if await crud_user.get_by_email(db, email=user_in.Email):
            raise ValidationError("邮箱已被注册")
        
        # 检查密码确认
        if user_in.Password != user_in.ConfirmPassword:
            raise ValidationError("密码与确认密码不一致")
        
        # 获取默认角色
        default_role = await role_service.get_default_role(db)
        if not default_role:
            # 如果没有默认角色，可以创建一个或者抛出异常
            raise ValidationError("系统未配置默认角色，请联系管理员")
        
        user = await crud_user.create(db, obj_in=user_in, default_role_id=default_role.Id)
        logger.info(f"用户创建成功: {user.UserName}")
        return user

    async def create_user_admin(self, db: Session, user_in: UserCreate) -> User:
        """创建用户（管理员用）"""
        # 检查邮箱是否已存在
        existing_user = await crud_user.get_by_email(db, email=user_in.Email)
        if existing_user:
            raise ValidationError("邮箱已被注册")
        
        # 检查角色是否存在
        role = await role_service.get_role_by_id(db, user_in.RoleId)
        if not role:
            raise ValidationError("指定的角色不存在")
        
        user = await crud_user.create_user(db, obj_in=user_in)
        logger.info(f"管理员创建用户成功: {user.UserName}")
        return user

    async def update_user(self, db: Session, user_id: UUID, user_update: UserUpdate) -> User:
        """更新用户信息"""
        # 检查用户是否存在
        existing_user = await crud_user.get_by_id(db, id=user_id)
        if not existing_user:
            raise NotFoundError("用户不存在")
        
        # 如果更新邮箱，检查邮箱是否被其他用户使用
        if user_update.Email:
            user_with_email = await crud_user.get_by_email(db, email=user_update.Email)
            if user_with_email and user_with_email.Id != user_id:
                raise ValidationError("邮箱已被其他用户使用")
        
        # 如果更新角色，检查角色是否存在
        if user_update.RoleId:
            role = await role_service.get_role_by_id(db, user_update.RoleId)
            if not role:
                raise ValidationError("指定的角色不存在")
        
        user = await crud_user.update(db, id=user_id, obj_in=user_update)
        logger.info(f"用户更新成功: {user_id}")
        return user
    
    async def update_avatar(self, db: Session, user_id: UUID, file: UploadFile) -> User:
        """更新用户头像"""
        user = await crud_user.get_by_id(db, id=user_id)
        if not user:
            raise NotFoundError("用户不存在")
        
        # 保存新头像
        avatar_path = await FileHandler.save_avatar(file, str(user_id))
        
        # 更新用户头像
        user = await crud_user.update_avatar(db, id=user_id, avatar_url=avatar_path)
        logger.info(f"用户 {user_id} 更新头像成功")
        
        return user
    
    async def delete_user(self, db: Session, user_id: UUID) -> User:
        """删除用户"""
        user = await crud_user.get_by_id(db, id=user_id)
        if not user:
            raise NotFoundError("用户不存在")
        
        deleted_user = await crud_user.delete(db, id=user_id)
        logger.info(f"用户删除成功: {user_id}")
        return deleted_user
    
    async def change_user_status(self, db: Session, user_id: UUID, status: str) -> User:
        """更改用户状态"""
        user = await crud_user.get_by_id(db, id=user_id)
        if not user:
            raise NotFoundError("用户不存在")
        
        user_update = UserUpdate(Status=status)
        return await self.update_user(db, user_id, user_update)
    
    async def change_user_role(self, db: Session, user_id: UUID, role_id: UUID) -> User:
        """更改用户角色"""
        user = await crud_user.get_by_id(db, id=user_id)
        if not user:
            raise NotFoundError("用户不存在")
        
        # 检查角色是否存在
        role = await role_service.get_role_by_id(db, role_id)
        if not role:
            raise ValidationError("指定的角色不存在")
        
        user_update = UserUpdate(RoleId=role_id)
        return await self.update_user(db, user_id, user_update)

user_service = UserService() 