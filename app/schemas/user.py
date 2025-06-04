from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid
from datetime import datetime

class RoleInfo(BaseModel):
    """角色信息模型"""
    Id: uuid.UUID
    RoleName: str
    RoleCode: str
    Description: Optional[str] = None

    class Config:
        from_attributes = True

class DepartmentInfo(BaseModel):
    """部门信息模型"""
    Id: uuid.UUID
    DepartmentName: str

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """用户基础模型"""
    UserName: str = Field(..., min_length=1, max_length=50, description="用户名")
    Email: EmailStr = Field(..., description="邮箱")
    DepartmentId: uuid.UUID = Field(..., description="部门ID")
    RoleId: uuid.UUID = Field(..., description="角色ID")
    AvatarUrl: str = Field(..., description="头像URL")
    Status: str = Field("1", description="状态:0-禁用;1-启用")

class UserCreate(UserBase):
    """创建用户模型"""
    Password: str = Field(..., min_length=6, description="密码")

class UserUpdate(BaseModel):
    """更新用户模型"""
    UserName: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    Email: Optional[EmailStr] = Field(None, description="邮箱")
    DepartmentId: Optional[uuid.UUID] = Field(None, description="部门ID")
    RoleId: Optional[uuid.UUID] = Field(None, description="角色ID")
    AvatarUrl: Optional[str] = Field(None, description="头像URL")
    Status: Optional[str] = Field(None, description="状态:0-禁用;1-启用")

class UserInDB(UserBase):
    """数据库中的用户模型"""
    Id: uuid.UUID
    PasswordHash: str
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(BaseModel):
    """用户响应模型"""
    Id: uuid.UUID
    UserName: str
    Email: EmailStr
    DepartmentId: uuid.UUID
    RoleId: uuid.UUID
    AvatarUrl: str
    Status: str
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    # 关联信息
    department: Optional[DepartmentInfo] = None
    role: Optional[RoleInfo] = None

    class Config:
        from_attributes = True
    
class UserLogin(BaseModel):
    """用户登录模型"""
    Email: EmailStr
    Password: str

class UserRegister(UserCreate):
    """用户注册模型"""
    ConfirmPassword: str

class UserInfo(BaseModel):
    """用户信息模型"""
    Id: uuid.UUID
    UserName: str
    Email: EmailStr
    DepartmentName: str
    RoleName: str
    AvatarUrl: str
    
class UserLoginResponse(UserInfo):
    """用户登录响应模型"""
    token: str
