from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime

from app.models.email_config import EmailConfig
from app.schemas.email import EmailPasswordUpdateRequest
from app.core.logger import get_logger
from app.core.exceptions import (
    BusinessException
)

logger = get_logger("user.crud")

class CRUDEmail:
    async def get_by_user_id(self, db: Session, user_id: uuid.UUID) -> Optional[EmailConfig]:
        """根据用户ID获取邮箱配置"""
        try:
            return db.query(EmailConfig).filter(EmailConfig.UserId == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"查询邮箱配置失败: {str(e)}")
            raise BusinessException("查询邮箱配置失败，请稍后重试")
    
    async def update_password(self, db: Session, user_id: uuid.UUID, new_password: EmailPasswordUpdateRequest) -> Optional[EmailConfig]:
        """更新邮箱密码"""
        try:
            email_config = db.query(EmailConfig).filter(EmailConfig.UserId == user_id).first()
            if not email_config:
                raise BusinessException("邮箱配置不存在")
            email_config.SpecialPassword = new_password.SpecialPassword
            db.commit()
            return email_config
        except SQLAlchemyError as e:
            logger.error(f"更新邮箱密码失败: {str(e)}")
            raise BusinessException("更新邮箱密码失败，请稍后重试")

email_crud = CRUDEmail()