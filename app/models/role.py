from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Role(BaseModel):
    """角色模型"""
    __tablename__ = "hRoles"

    RoleName = Column(String(50), nullable=False, unique=True, comment="角色名称")
    RoleCode = Column(String(50), nullable=False, unique=True, comment="角色代码")
    Description = Column(Text, nullable=True, comment="角色描述")
    Status = Column(String(50), nullable=False, default="1", comment="状态:0-禁用;1-启用")

    # 关系
    users = relationship("User", back_populates="role") 