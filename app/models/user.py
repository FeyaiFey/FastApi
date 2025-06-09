from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    """用户模型"""
    __tablename__ = "hUsers"

    UserName = Column(String(50), nullable=False, comment="用户名")
    PasswordHash = Column(String(255), nullable=False, comment="密码哈希")
    Email = Column(String(255), nullable=False, comment="邮箱")
    DepartmentId = Column(ForeignKey("hDepartments.Id"), nullable=False, comment="部门ID")
    RoleId = Column(ForeignKey("hRoles.Id"), nullable=False, comment="角色ID")
    AvatarUrl = Column(String(255), nullable=False, comment="头像url")
    Status = Column(String(50), nullable=False, comment="状态:0-禁用;1-启用")

    # 关系
    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    email_config = relationship("EmailConfig", back_populates="user", uselist=False)

    