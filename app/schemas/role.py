from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class RoleBase(BaseModel):
    """角色基础模型"""
    RoleName: str = Field(..., min_length=1, max_length=50, description="角色名称")
    RoleCode: str = Field(..., min_length=1, max_length=50, description="角色代码")
    Description: Optional[str] = Field(None, description="角色描述")
    Status: str = Field("1", description="状态:0-禁用;1-启用")

class RoleCreate(RoleBase):
    """创建角色模型"""
    pass

class RoleUpdate(BaseModel):
    """更新角色模型"""
    RoleName: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    RoleCode: Optional[str] = Field(None, min_length=1, max_length=50, description="角色代码")
    Description: Optional[str] = Field(None, description="角色描述")
    Status: Optional[str] = Field(None, description="状态:0-禁用;1-启用")

class RoleInDB(RoleBase):
    """数据库中的角色模型"""
    Id: uuid.UUID
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class Role(RoleInDB):
    """角色响应模型"""
    pass 