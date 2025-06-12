from datetime import timedelta
from sqlalchemy.orm import Session
from aioredis.exceptions import RedisError

from app.models.user import User
from app.schemas.user import UserLogin, UserLoginResponse, UserInfo
from app.crud.auth import auth_crud
from app.crud.department import department_crud
from app.crud.role import role_crud
from app.core.security import create_access_token, revoke_all_tokens, get_token_expire_minutes
from app.core.logger import get_logger
from app.core.token import token_manager
from app.core.exceptions import (
    BusinessException,
    DatabaseException
)

logger = get_logger("auth.service")

class AuthService:
    async def authenticate(self, db: Session, login_data: UserLogin) -> User:
        """
        验证用户登录
        :raises: AuthenticationException, DatabaseException
        """
        return await auth_crud.authenticate(
            db, 
            email=login_data.Email, 
            password=login_data.Password
        )
    
    async def create_access_token(self, user: User) -> dict:
        """创建访问令牌"""
        try:
            access_token_expires = timedelta(minutes=get_token_expire_minutes())
            access_token = await create_access_token(
                subject=str(user.Id),
                expires_delta=access_token_expires
            )
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        except Exception as e:
            logger.error(f"创建访问令牌失败: {str(e)}")
            raise BusinessException("创建访问令牌失败")
    
    async def login(self, db: Session, login_data: UserLogin) -> UserLoginResponse:
        """
        用户登录
        :raises: AuthenticationException, DatabaseException, BusinessException
        """
        # 验证用户
        user = await self.authenticate(db, login_data)
        
        try:
            # 撤销之前的令牌
            await revoke_all_tokens(user.Id)
            
            # 创建访问令牌
            token_data = await self.create_access_token(user)
            
            try:
                # 存储token到Redis
                await token_manager.store_token(
                    str(user.Id),
                    token_data["access_token"]
                )
            except RedisError as e:
                logger.error(f"存储token失败: {str(e)}")
                raise BusinessException("存储token失败")

            # 获取用户部门和角色
            department = await department_crud.get_by_id(db, user.DepartmentId)
            role = await role_crud.get_by_id(db, user.RoleId)

            if not department or not role:
                raise BusinessException("获取用户信息失败")

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
            
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"登录过程中发生错误: {str(e)}")
            raise BusinessException("登录失败，请稍后重试")

    async def logout(self, user_id: str) -> None:
        """
        用户登出
        :raises: BusinessException
        """
        try:
            await token_manager.revoke_token(user_id)
            logger.info(f"用户登出成功: {user_id}")
        except Exception as e:
            logger.error(f"用户登出失败: {str(e)}")
            raise BusinessException("登出失败，请稍后重试")

    async def validate_token(self, user_id: str, token: str) -> bool:
        """验证token是否有效"""
        try:
            return await token_manager.validate_token(user_id, token)
        except Exception as e:
            logger.error(f"Token验证失败: {str(e)}")
            return False

auth_service = AuthService()