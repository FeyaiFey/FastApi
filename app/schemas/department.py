from pydantic import BaseModel, Field
from typing import Optional, List
from pydantic.types import UUID4
from datetime import datetime

class Department(BaseModel):
    """部门模型"""
    Id: UUID4 = Field(..., description="部门ID")
    ParentId: Optional[UUID4] = Field(default=None, description="父部门ID")
    DepartmentName: str = Field(..., description="部门名称")
    Status: str = Field(..., description="状态")
    CreatedAt: datetime = Field(..., description="创建时间")
    UpdatedAt: datetime = Field(..., description="更新时间")

class DepartmentTree(BaseModel):
    """部门树模型"""
    Id: UUID4 = Field(..., description="部门ID")
    DepartmentName: str = Field(..., description="部门名称")
    Children: Optional[List["DepartmentTree"]] = Field(default=None, description="子部门列表")