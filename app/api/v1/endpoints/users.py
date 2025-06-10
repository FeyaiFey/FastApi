from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserInfo
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