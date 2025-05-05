from typing import Optional, List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegister
from app.crud.user import user as crud_user
from app.utils.file_handler import FileHandler
from app.core.logger import get_logger

logger = get_logger(__name__)

class UserService:
    async def get_user(self, db: Session, user_id: str) -> Optional[User]:
        """获取用户信息"""
        return await crud_user.get_by_id(db, id=user_id)
    
    async def create_user(self, db: Session, user_in: UserRegister) -> str:
        """创建用户"""
        # 检查邮箱是否已存在
        if await crud_user.get_by_email(db, email=user_in.Email):
            raise ValueError("邮箱已被注册")
        
        return await crud_user.create(db, obj_in=user_in)
    
    async def update_avatar(self, db: Session, user_id: str, file: UploadFile) -> User:
        """更新用户头像"""
        user = await crud_user.get_by_id(db, id=user_id)
        if not user:
            raise ValueError("用户不存在")
        
        try:
            # 保存新头像
            avatar_path = await FileHandler.save_avatar(file, user_id)
            
            # 更新用户头像
            user = await crud_user.update_avatar(db, db_obj=user, avatar_url=avatar_path)
            logger.info(f"用户 {user_id} 更新头像成功")
            
            return user
        except Exception as e:
            logger.error(f"用户 {user_id} 更新头像失败: {str(e)}")
            raise
    
    async def delete_user(self, db: Session, user_id: str) -> User:
        """删除用户"""
        user = await crud_user.get_by_id(db, id=user_id)
        if not user:
            raise ValueError("用户不存在")
        
        return await crud_user.delete(db, id=user_id)

user_service = UserService() 