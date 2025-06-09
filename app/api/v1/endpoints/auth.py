from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from aioredis.exceptions import RedisError

from app.core.database import get_db_session
from app.core.deps import get_current_user,oauth2_scheme
from app.core.response import response_manager
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserLoginResponse, UserBase, LogoutRequest
from app.schemas.response import SuccessResponse
from app.services.auth import auth_service
from app.crud.user import user as crud_user
from app.core.security import revoke_all_tokens
from app.core.logger import get_logger
from app.exceptions.base import ValidationError

router = APIRouter() 
logger = get_logger(__name__)

@router.post("/register", response_model=SuccessResponse[UserBase])
async def register(
    *,
    db: Session = Depends(get_db_session),
    user_in: UserRegister
) -> SuccessResponse[UserBase]:
    """
    用户注册
    """
    # 检查邮箱是否已存在
    user = await crud_user.get_by_email(db, email=user_in.Email)
    if user:
        logger.warning(f"注册失败: 邮箱已存在 - {user_in.Email}")
        raise ValidationError("该邮箱已被注册")
    
    # 创建用户
    user = await crud_user.create(db, obj_in=user_in)
    logger.info(f"用户注册成功: {user.UserName}")
    return response_manager.created(data=user, message="用户注册成功")

@router.post("/login", response_model=SuccessResponse[UserLoginResponse])
async def login(
    *,
    db: Session = Depends(get_db_session),
    login_data: UserLogin
) -> SuccessResponse[UserLoginResponse]:
    """
    用户登录
    - 验证用户凭据
    - 生成访问令牌
    - 撤销之前的令牌
    """
    # 使用auth_service处理登录逻辑
    login_response = await auth_service.login(db, login_data)
    
    # 撤销之前的令牌
    user = await auth_service.authenticate(db, login_data)
    await revoke_all_tokens(user.Id)
    
    return response_manager.success(data=login_response, message="登录成功")

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    用户登出
    - 撤销当前用户的所有令牌
    """
    await revoke_all_tokens(current_user.Id)
    logger.info(f"用户 {current_user.Email} 登出成功")
    return {"message": "登出成功"} 