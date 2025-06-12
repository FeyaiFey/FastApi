from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.email import EmailConfigBase, EmailPasswordUpdateRequest
from app.services.email import email_service
from app.core.logger import get_logger
from app.core.exceptions import (
    CustomException
)
from app.schemas.response import ResponseModel, ResponseHandler

router = APIRouter()
logger = get_logger("email.api")

@router.get("/{user_id}/config", response_model=ResponseModel[EmailConfigBase])
async def get_email_config(
    user_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[EmailConfigBase]:
    """
    获取当前用户邮箱配置
    """
    try:
        email_config = await email_service.get_email_config_by_user_id(db, user_id)
        return ResponseHandler.success(data=email_config, message="获取当前用户邮箱配置成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"获取当前用户邮箱配置失败: {str(e)}")
        return ResponseHandler.error(500, "获取当前用户邮箱配置失败")

@router.put("/{user_id}/password", response_model=ResponseModel[EmailConfigBase])
async def update_email_password(
    user_id: UUID,
    new_password: EmailPasswordUpdateRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> ResponseModel[EmailConfigBase]:
    """
    更新当前用户邮箱密码
    """
    try:
        email_config = await email_service.update_email_password(db, user_id, new_password)
        return ResponseHandler.success(data=email_config, message="更新当前用户邮箱密码成功")
    except CustomException as e:
        # 自定义异常会被全局异常处理器捕获并处理
        raise
    except Exception as e:
        logger.error(f"更新当前用户邮箱密码失败: {str(e)}")
        return ResponseHandler.error(500, "更新当前用户邮箱密码失败")