from typing import Any
from fastapi import APIRouter, Depends,Form
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.deps import get_current_user,oauth2_scheme
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserLoginResponse, UserBase
from app.services.auth import auth_service
from app.crud.user import user as crud_user
from app.core.logger import get_logger
from app.core.exceptions import (
    BadRequestException,
    CustomException
)
from app.schemas.response import ResponseModel, ResponseHandler

router = APIRouter() 
logger = get_logger(__name__)

@router.post("/register", response_model=ResponseModel[UserBase])
async def register(
    *,
    db: Session = Depends(get_db_session),
    user_in: UserRegister = Form(...)
) -> ResponseModel[UserBase]:
    """
    用户注册
    """
    try:
        # 检查邮箱是否已存在
        user = await crud_user.get_by_email(db, email=user_in.Email)
        if user:
            logger.warning(f"注册失败: 邮箱已存在 - {user_in.Email}")
            raise BadRequestException("该邮箱已被注册")
        
        # 创建用户
        user = await crud_user.create(db, obj_in=user_in)
        logger.info(f"用户注册成功: {user.UserName}")
        return ResponseHandler.success(
            data=user,
            message="用户注册成功"
        )
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"注册过程中发生未知错误: {str(e)}")
        return ResponseHandler.error(message="注册失败，请稍后重试")

@router.post("/login", response_model=ResponseModel[UserLoginResponse])
async def login(
    *,
    db: Session = Depends(get_db_session),
    login_data: UserLogin = Form(...)
) -> ResponseModel[UserLoginResponse]:
    """
    用户登录
    - 验证用户凭据
    - 生成访问令牌
    - 撤销之前的令牌
    """
    try:
        # 使用auth_service处理登录逻辑
        login_response = await auth_service.login(db, login_data)
        
        return ResponseHandler.success(
            data=login_response,
            message="登录成功"
        )
    except CustomException as e:
        raise
    except Exception as e:
        logger.error(f"登录过程中发生未知错误: {str(e)}")
        return ResponseHandler.error(message="登录失败，请稍后重试")

@router.post("/logout", response_model=ResponseModel[None])
async def logout(
    current_user: User = Depends(get_current_user)
) -> ResponseModel[None]:
    """
    用户登出
    - 撤销当前用户的所有令牌
    """
    try:
        await auth_service.logout(current_user.Id)
        return ResponseHandler.success(message="登出成功")
    except CustomException as e:
        raise
    except Exception as e:
        logger.error(f"登出过程中发生未知错误: {str(e)}")
        return ResponseHandler.error(message="登出失败，请稍后重试") 