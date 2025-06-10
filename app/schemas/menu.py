from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class MenuBase(BaseModel):
    """菜单基础模型"""
    MenuId: int = Field(..., ge=1000, description="菜单ID，从1000开始")
    ParentId: Optional[int] = Field(None, description="父菜单ID")
    Path: str = Field(..., min_length=1, max_length=255, description="路由路径")
    Component: Optional[str] = Field(None, max_length=255, description="组件路径")
    Redirect: Optional[str] = Field(None, max_length=255, description="重定向路径")
    Name: str = Field(..., min_length=1, max_length=100, description="路由名称")
    Title: Optional[str] = Field(None, max_length=255, description="菜单标题")
    Icon: Optional[str] = Field(None, max_length=255, description="菜单图标")
    Hidden: Optional[bool] = Field(False, description="是否隐藏")
    AlwaysShow: Optional[bool] = Field(False, description="是否总是显示")
    NoCache: Optional[bool] = Field(False, description="是否不缓存")
    Breadcrumb: Optional[bool] = Field(True, description="是否显示面包屑")
    Affix: Optional[bool] = Field(False, description="是否固定标签")
    ActiveMenu: Optional[str] = Field(None, max_length=255, description="激活菜单路径")
    NoTagsView: Optional[bool] = Field(False, description="是否不显示标签视图")
    CanTo: Optional[bool] = Field(True, description="是否可以跳转")
    Permission: Optional[List[str]] = Field(None, description="权限标识数组")
    ExternalLink: Optional[str] = Field(None, max_length=255, description="外部链接")
    MenuOrder: Optional[int] = Field(0, description="菜单排序")

class MenuCreate(BaseModel):
    """创建菜单模型"""
    MenuId: int = Field(..., ge=1000, description="菜单ID，从1000开始")
    ParentId: Optional[int] = Field(None, description="父菜单ID")
    Path: str = Field(..., min_length=1, max_length=255, description="路由路径")
    Component: Optional[str] = Field(None, max_length=255, description="组件路径")
    Redirect: Optional[str] = Field(None, max_length=255, description="重定向路径")
    Name: str = Field(..., min_length=1, max_length=100, description="路由名称")
    Title: Optional[str] = Field(None, max_length=255, description="菜单标题")
    Icon: Optional[str] = Field(None, max_length=255, description="菜单图标")
    Hidden: Optional[bool] = Field(False, description="是否隐藏")
    AlwaysShow: Optional[bool] = Field(False, description="是否总是显示")
    NoCache: Optional[bool] = Field(False, description="是否不缓存")
    Breadcrumb: Optional[bool] = Field(True, description="是否显示面包屑")
    Affix: Optional[bool] = Field(False, description="是否固定标签")
    ActiveMenu: Optional[str] = Field(None, max_length=255, description="激活菜单路径")
    NoTagsView: Optional[bool] = Field(False, description="是否不显示标签视图")
    CanTo: Optional[bool] = Field(True, description="是否可以跳转")
    Permission: Optional[List[str]] = Field(None, description="权限标识数组")
    ExternalLink: Optional[str] = Field(None, max_length=255, description="外部链接")
    MenuOrder: Optional[int] = Field(0, description="菜单排序")

class MenuUpdate(BaseModel):
    """更新菜单模型"""
    ParentId: Optional[int] = Field(None, description="父菜单ID")
    Path: Optional[str] = Field(None, min_length=1, max_length=255, description="路由路径")
    Component: Optional[str] = Field(None, max_length=255, description="组件路径")
    Redirect: Optional[str] = Field(None, max_length=255, description="重定向路径")
    Name: Optional[str] = Field(None, min_length=1, max_length=100, description="路由名称")
    Title: Optional[str] = Field(None, max_length=255, description="菜单标题")
    Icon: Optional[str] = Field(None, max_length=255, description="菜单图标")
    Hidden: Optional[bool] = Field(None, description="是否隐藏")
    AlwaysShow: Optional[bool] = Field(None, description="是否总是显示")
    NoCache: Optional[bool] = Field(None, description="是否不缓存")
    Breadcrumb: Optional[bool] = Field(None, description="是否显示面包屑")
    Affix: Optional[bool] = Field(None, description="是否固定标签")
    ActiveMenu: Optional[str] = Field(None, max_length=255, description="激活菜单路径")
    NoTagsView: Optional[bool] = Field(None, description="是否不显示标签视图")
    CanTo: Optional[bool] = Field(None, description="是否可以跳转")
    Permission: Optional[List[str]] = Field(None, description="权限标识数组")
    ExternalLink: Optional[str] = Field(None, max_length=255, description="外部链接")
    MenuOrder: Optional[int] = Field(None, description="菜单排序")

class MenuInDB(MenuBase):
    """数据库中的菜单模型"""
    Id: UUID
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class Menu(MenuInDB):
    """菜单响应模型"""
    pass

class MenuTree(BaseModel):
    """菜单树形结构模型"""
    Id: UUID
    MenuId: int
    ParentId: Optional[int] = None
    Path: str
    Component: Optional[str] = None
    Redirect: Optional[str] = None
    Name: str
    Title: Optional[str] = None
    Icon: Optional[str] = None
    Hidden: Optional[bool] = False
    AlwaysShow: Optional[bool] = False
    NoCache: Optional[bool] = False
    Breadcrumb: Optional[bool] = True
    Affix: Optional[bool] = False
    ActiveMenu: Optional[str] = None
    NoTagsView: Optional[bool] = False
    CanTo: Optional[bool] = True
    Permission: Optional[List[str]] = None
    ExternalLink: Optional[str] = None
    MenuOrder: Optional[int] = 0
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    children: Optional[List['MenuTree']] = []

    class Config:
        from_attributes = True

# 为了支持递归引用，需要更新模型
MenuTree.model_rebuild() 