from sqlalchemy import Column, String, ForeignKey, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime
from datetime import timezone

class EmailConfig(BaseModel):
    """邮箱配置模型"""
    __tablename__ = "hEmailConfigs"

    UserId = Column(ForeignKey("hUsers.Id"), nullable=True, comment="用户ID")
    ImapServer = Column(String(100), nullable=True, comment="IMAP服务器")
    ImapPort = Column(Integer, nullable=True, comment="IMAP端口")
    ImapUseSsl = Column(Integer, nullable=True, comment="IMAP是否使用SSL")
    SmtpServer = Column(String(100), nullable=True, comment="SMTP服务器")
    SmtpPort = Column(Integer, nullable=True, comment="SMTP端口")
    SmtpUseSsl = Column(Integer, nullable=True, comment="SMTP是否使用SSL")
    SpecialPassword = Column(String(100), nullable=True, comment="独立密码")
    CreatedAt = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), comment="创建时间")
    UpdatedAt = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="email_config") 