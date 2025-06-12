from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.email_config import EmailConfig
from app.crud.email import email_crud
from app.schemas.email import EmailPasswordUpdateRequest
from app.core.logger import get_logger
from app.core.exceptions import (
    BusinessException
)

logger = get_logger("email.service")

class EmailService:
    async def get_email_config_by_user_id(self, db: Session, user_id: UUID) -> Optional[EmailConfig]:
        """根据用户ID获取邮箱配置"""
        return await email_crud.get_by_user_id(db, user_id)
    
    async def update_email_password(self, db: Session, user_id: UUID, new_password: EmailPasswordUpdateRequest) -> Optional[EmailConfig]:
        """更新邮箱密码"""
        return await email_crud.update_password(db, user_id, new_password)

email_service = EmailService()