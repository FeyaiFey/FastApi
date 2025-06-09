from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserLogin, UserLoginResponse, UserInfo
from app.crud.auth import auth as crud_auth
from app.crud.department import department as crud_department
from app.crud.role import role as crud_role
from app.core.security import create_access_token,revoke_all_tokens
from app.core.config import settings
from app.core.logger import get_logger
from app.core.token_manager import token_manager
from app.exceptions.base import AuthenticationError

logger = get_logger("auth.service")

class AuthService:
    async def authenticate(self, db: Session, login_data: UserLogin) -> Optional[User]:
        """验证用户登录"""
        user = await crud_auth.authenticate(db, email=login_data.Email, password=login_data.Password)
        if not user:
            logger.warning(f"用户登录失败: 邮箱或密码错误 - {login_data.Email}")
            raise AuthenticationError("邮箱或密码错误")
        
        if not await crud_auth.is_active(user):
            logger.warning(f"用户登录失败: 用户已被禁用 - {login_data.Email}")
            raise AuthenticationError("用户已被禁用")
        
        return user
    
    async def create_access_token(self, user: User) -> dict:
        """创建访问令牌"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            subject=str(user.Id),
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def login(self, db: Session, login_data: UserLogin) -> UserLoginResponse:
        """用户登录"""
        # 验证用户
        user = await self.authenticate(db, login_data)
        
        # 撤销之前的令牌
        await revoke_all_tokens(user.Id)
        
        # 创建访问令牌
        token_data = await self.create_access_token(user)
        
        # 存储token到Redis
        await token_manager.store_token(
            str(user.Id),
            token_data["access_token"]
        )

        # 获取用户部门
        department = await crud_department.get_by_id(db, user.DepartmentId)
        
        # 获取用户角色
        role = await crud_role.get_by_id(db, user.RoleId)

        # 创建用户信息对象
        user_info = UserInfo(
            Id=user.Id,
            UserName=user.UserName,
            Email=user.Email,
            DepartmentId=user.DepartmentId,
            RoleId=user.RoleId,
            DepartmentName=department.DepartmentName,
            RoleName=role.RoleName,
            AvatarUrl=user.AvatarUrl
        )

        # 创建登录响应
        response = UserLoginResponse(
            userInfo=user_info,
            token=token_data["access_token"]
        )

        logger.info(f"用户登录成功: {user.UserName}")
        return response

    async def logout(self, user_id: str) -> None:
        """用户登出"""
        await token_manager.revoke_token(user_id)
        logger.info(f"用户登出成功: {user_id}")

    async def validate_token(self, user_id: str, token: str) -> bool:
        """验证token是否有效"""
        return await token_manager.validate_token(user_id, token)

auth_service = AuthService()