from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class RoleMenuBase(BaseModel):
    """角色菜单基础模型"""
    RoleId: uuid.UUID = Field(..., description="角色ID")
    MenuId: int = Field(..., description="菜单ID")
    IsEnabled: bool = Field(True, description="是否启用")

class RoleMenuCreate(RoleMenuBase):
    """创建角色菜单模型"""
    pass

class RoleMenuUpdate(BaseModel):
    """更新角色菜单模型"""
    IsEnabled: Optional[bool] = Field(None, description="是否启用")

class RoleMenuBatchCreate(BaseModel):
    """批量创建角色菜单关联"""
    RoleId: uuid.UUID = Field(..., description="角色ID")
    MenuIds: List[int] = Field(..., description="菜单ID列表")
    IsEnabled: Optional[bool] = Field(True, description="是否启用")

class RoleMenuBatchUpdate(BaseModel):
    """批量更新角色菜单关联"""
    RoleId: uuid.UUID = Field(..., description="角色ID")
    MenuIds: List[int] = Field(..., description="菜单ID列表")
    IsEnabled: Optional[bool] = Field(True, description="是否启用")

class RoleMenuInDB(RoleMenuBase):
    """数据库中的角色菜单模型"""
    Id: uuid.UUID
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class RoleMenu(RoleMenuInDB):
    """角色菜单响应模型"""
    pass

class RoleMenuWithDetails(BaseModel):
    """带详情的角色菜单模型"""
    Id: uuid.UUID
    RoleId: uuid.UUID
    MenuId: int
    IsEnabled: bool
    CreatedAt: datetime
    UpdatedAt: Optional[datetime] = None
    
    # 关联信息
    RoleName: Optional[str] = Field(None, description="角色名称")
    MenuName: Optional[str] = Field(None, description="菜单名称")
    MenuTitle: Optional[str] = Field(None, description="菜单标题")
    MenuPath: Optional[str] = Field(None, description="菜单路径")

    class Config:
        from_attributes = True

class RoleMenuQuery(BaseModel):
    """角色菜单查询参数"""
    RoleId: Optional[uuid.UUID] = Field(None, description="角色ID筛选")
    MenuId: Optional[int] = Field(None, description="菜单ID筛选")
    IsEnabled: Optional[bool] = Field(None, description="启用状态筛选")
    RoleName: Optional[str] = Field(None, description="角色名称筛选")
    MenuName: Optional[str] = Field(None, description="菜单名称筛选")

# 前端路由结构模型
class RouteMeta(BaseModel):
    """路由元数据模型"""
    title: Optional[str] = Field(None, description="菜单标题")
    icon: Optional[str] = Field(None, description="菜单图标")
    alwaysShow: Optional[bool] = Field(None, description="是否总是显示")
    noCache: Optional[bool] = Field(None, description="是否不缓存")
    affix: Optional[bool] = Field(None, description="是否固定标签")
    hidden: Optional[bool] = Field(None, description="是否隐藏")
    noTagsView: Optional[bool] = Field(None, description="是否不显示标签视图")
    canTo: Optional[bool] = Field(None, description="是否可以跳转")
    permission: Optional[List[str]] = Field(None, description="权限标识")
    activeMenu: Optional[str] = Field(None, description="激活菜单路径")
    showMainRoute: Optional[bool] = Field(None, description="是否显示主路由")

class RouteItem(BaseModel):
    """路由项模型"""
    path: str = Field(..., description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    redirect: Optional[str] = Field(None, description="重定向路径")
    name: str = Field(..., description="路由名称")
    meta: RouteMeta = Field(default_factory=RouteMeta, description="路由元数据")
    children: Optional[List['RouteItem']] = Field(None, description="子路由")

# 为了支持自引用，需要更新模型
RouteItem.model_rebuild() 