from fastapi import APIRouter, Depends, Form, Body
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserInfo, UserPasswordUpdateRequest, UserInfoUpdateRequest
from app.schemas.response import ResponseModel, ResponseHandler
from app.services.user import user_service
from app.core.logger import get_logger
from app.core.exceptions import (
    CustomException
)

router = APIRouter()
logger = get_logger(__name__)

@router.get("/current", response_model=ResponseModel[UserInfo])
async def get_current_user(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[UserInfo]:
    """
    获取当前用户信息
    """
    try:
        logger.info(f"获取当前用户信息: {current_user}")
        user_info = await user_service.get_current_user_info(db, current_user.Id)
        return ResponseHandler.success(data=user_info, message="获取当前用户信息成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"获取当前用户信息失败: {str(e)}")
        raise CustomException(message="获取当前用户信息失败")

@router.put("/{user_id}/password", response_model=ResponseModel[UserInfo])
async def update_user_password(
    user_id: UUID,
    password_update_request: UserPasswordUpdateRequest = Form(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[UserInfo]:
    """
    更新用户密码
    """
    try:
        user_info = await user_service.update_user_password(db, user_id, password_update_request)
        return ResponseHandler.success(data=user_info, message="更新用户密码成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"更新用户密码失败: {str(e)}")
        raise CustomException(message="更新用户密码失败")

@router.put("/{user_id}/info", response_model=ResponseModel[UserInfo])
async def update_user_info(
    user_id: UUID,
    user_info_update_request: UserInfoUpdateRequest = Form(...),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[UserInfo]:
    """
    更新用户信息
    """
    try:
        user_info = await user_service.update_user_info(db, user_id, user_info_update_request)
        return ResponseHandler.success(data=user_info, message="更新用户信息成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"更新用户信息失败: {str(e)}")
        raise CustomException(message="更新用户信息失败")

@router.post("/{user_id}/avatar", response_model=ResponseModel[UserInfo])
async def update_user_avatar(
    user_id: UUID,
    avatar_data: dict,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[UserInfo]:
    """
    更新用户头像
    
    表单参数:
    - avatar_data: base64字符串或URL
    """
    try:
        user_info = await user_service.update_user_avatar(db, user_id, avatar_data["avatar_data"])
        return ResponseHandler.success(data=user_info, message="更新用户头像成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"更新用户头像失败: {str(e)}")
        raise CustomException(message="更新用户头像失败")
