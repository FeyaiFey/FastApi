from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class Department(BaseModel):
    """部门模型"""
    Id: UUID = Field(..., description="部门ID")
    ParentId: Optional[UUID] = Field(default=None, description="父部门ID")
    DepartmentName: str = Field(..., description="部门名称")
    Status: str = Field(..., description="状态")
    CreatedAt: datetime = Field(..., description="创建时间")
    UpdatedAt: datetime = Field(..., description="更新时间")

class DepartmentTree(BaseModel):
    """部门树模型"""
    Id: UUID = Field(..., description="部门ID")
    DepartmentName: str = Field(..., description="部门名称")
    Children: Optional[List["DepartmentTree"]] = Field(default=None, description="子部门列表")
class DepartmentCreate(BaseModel):
    """部门创建模型"""
    name: str = Field(..., description="部门名称")
    parent_id: Optional[str] = Field(default=None, description="父部门ID")

class DepartmentStatusUpdate(BaseModel):
    """部门状态更新模型"""
    id: UUID = Field(..., description="部门ID")
    status: str = Field(..., description="状态")
