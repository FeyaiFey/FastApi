from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

class EmailConfigBase(BaseModel):
    """角色基础模型"""
    UserId: UUID = Field(..., description="用户ID")
    ImapServer: str = Field(..., min_length=1, max_length=50, description="IMAP服务器")
    ImapPort: int = Field(..., description="IMAP端口")
    ImapUseSsl: bool = Field(..., description="IMAP是否使用SSL")
    SmtpServer: str = Field(..., min_length=1, max_length=50, description="SMTP服务器")
    SmtpPort: int = Field(..., description="SMTP端口")
    SmtpUseSsl: bool = Field(..., description="SMTP是否使用SSL")
    SpecialPassword: Optional[str] = Field(..., description="独立密码")

class EmailPasswordUpdateRequest(BaseModel):
    """邮箱密码更新请求"""
    SpecialPassword: Optional[str] = Field(..., description="独立密码")
