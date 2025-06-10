from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

class UserBase(BaseModel):
    """用户基础模型"""
    UserName: str = Field(..., min_length=1, max_length=50, description="用户名")
    Email: EmailStr = Field(..., description="邮箱")
    DepartmentId: UUID = Field(..., description="部门ID")
    RoleId: Optional[UUID] = Field(None, description="角色ID")
    AvatarUrl: Optional[str] = Field(None, description="头像URL")
    Status: Optional[str] = Field("1", description="状态:0-禁用;1-启用")

class UserCreate(UserBase):
    """创建用户模型"""
    Password: str = Field(..., min_length=6, description="密码")

class UserLogin(BaseModel):
    """用户登录模型"""
    Email: EmailStr
    Password: str = Field(..., min_length=6, max_length=50)

class UserRegister(UserCreate):
    """用户注册模型"""
    ConfirmPassword: str = Field(..., min_length=6, max_length=50)

class UserInfo(BaseModel):
    """用户信息模型"""
    Id: UUID = Field(..., description="用户ID")
    UserName: str = Field(..., min_length=1, max_length=50, description="用户名")
    Email: EmailStr
    DepartmentId: UUID = Field(..., description="部门ID")
    RoleId: UUID = Field(..., description="角色ID")
    DepartmentName: str = Field(..., description="部门名称")
    RoleName: str = Field(..., description="角色名称")
    AvatarUrl: str = Field(..., description="头像URL")
    
class UserLoginResponse(BaseModel):
    """用户登录响应模型"""
    userInfo: UserInfo
    token: str = Field(..., description="访问令牌")

class UserUpdate(BaseModel):
    """更新用户模型"""
    UserName: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    Email: Optional[EmailStr] = Field(None, description="邮箱")
    DepartmentId: Optional[UUID] = Field(None, description="部门ID")
    RoleId: Optional[UUID] = Field(None, description="角色ID")
    AvatarUrl: Optional[str] = Field(None, description="头像URL")
    Status: Optional[str] = Field(None, description="状态:0-禁用;1-启用")

    class Config:
        from_attributes = True