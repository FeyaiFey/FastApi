from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserInfo
from app.services.user import user_service
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    - 验证文件类型和大小
    - 保存头像文件
    - 更新用户头像URL
    """
    try:
        return await user_service.update_avatar(db, current_user.Id, file)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"头像上传失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="头像上传失败，请稍后重试"
        )