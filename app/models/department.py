from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Department(BaseModel):
    """部门模型"""
    __tablename__ = "hDepartments"

    ParentId = Column(ForeignKey("hDepartments.Id"), nullable=True, comment="父部门ID")
    DepartmentName = Column(String(50), nullable=False, comment="部门名称")
    Status = Column(String(50), nullable=False, comment="状态:0-禁用;1-启用")

    # 关系
    parent = relationship("Department", remote_side="Department.Id", backref="children")
    users = relationship("User", back_populates="department") 