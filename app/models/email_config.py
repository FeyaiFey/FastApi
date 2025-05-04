from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class EmailConfig(BaseModel):
    """邮件配置模型"""
    __tablename__ = "hEmailConfigs"

    UserId = Column(ForeignKey("hUsers.Id"), nullable=True, comment="用户ID")
    ImapServer = Column(String(100), nullable=True, comment="IMAP服务器")
    ImapPort = Column(Integer, nullable=True, comment="IMAP端口")
    ImapUseSsl = Column(Boolean, nullable=True, comment="IMAP是否使用SSL")
    SmtpServer = Column(String(100), nullable=True, comment="SMTP服务器")
    SmtpPort = Column(Integer, nullable=True, comment="SMTP端口")
    SmtpUseSsl = Column(Boolean, nullable=True, comment="SMTP是否使用SSL")

    # 关系
    user = relationship("User", back_populates="email_config") 