from typing import Optional, List
from pydantic import BaseModel, Field

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