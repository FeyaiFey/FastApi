from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import json

from app.models.role import Role
from app.crud.role import role_crud
from app.schemas.roleMenu import RouteItem, RouteMeta
from app.models.role_menu import RoleMenu
from app.models.menu import Menu
from app.core.logger import get_logger
from app.core.exceptions import (
    BusinessException
)

logger = get_logger("role.service")

class RoleService:
    async def get_role_by_id(self, db: Session, role_id: UUID) -> Optional[Role]:
        """根据ID获取角色"""
        return await role_crud.get_by_id(db, role_id)
    
    async def get_role_menus(self, db: Session, role_id: UUID) -> List[RouteItem]:
        """获取角色的菜单路由"""
        # 检查角色是否存在
        role = await self.get_role_by_id(db, role_id)
        if not role:
            raise BusinessException("角色不存在")
        
        # 查询角色关联的菜单
        role_menus = db.query(RoleMenu).filter(
            RoleMenu.RoleId == role_id,
            RoleMenu.IsEnabled == True
        ).all()
        
        if not role_menus:
            return []
        
        # 获取菜单ID列表
        menu_ids = [rm.MenuId for rm in role_menus]
        
        # 查询菜单详情
        menus = db.query(Menu).filter(
            Menu.MenuId.in_(menu_ids),
            Menu.Hidden == False  # 只获取非隐藏菜单
        ).order_by(Menu.MenuOrder).all()
        
        # 构建路由树
        routes = self._build_route_tree(menus)
        
        logger.info(f"获取角色 {role_id} 的菜单路由成功，共 {len(routes)} 个根路由")
        return routes

    def _build_route_tree(self, menus: List[Menu]) -> List[RouteItem]:
        """构建路由树"""
        menu_map = {menu.MenuId: menu for menu in menus}
        root_routes = []
        
        # 先找出所有根菜单
        for menu in menus:
            if menu.ParentId is None:
                route = self._menu_to_route(menu, menu_map)
                root_routes.append(route)
        
        return root_routes

    def _menu_to_route(self, menu: Menu, menu_map: dict) -> RouteItem:
        """将菜单转换为路由项"""
        # 解析权限
        permissions = []
        if menu.Permission:
            try:
                permissions = json.loads(menu.Permission) if isinstance(menu.Permission, str) else menu.Permission
            except (json.JSONDecodeError, TypeError):
                permissions = []
        
        # 构建路由元数据
        meta = RouteMeta(
            title=menu.Title,
            icon=menu.Icon,
            alwaysShow=menu.AlwaysShow,
            noCache=menu.NoCache,
            affix=menu.Affix,
            hidden=menu.Hidden,
            noTagsView=menu.NoTagsView,
            canTo=menu.CanTo,
            permission=permissions if permissions else None,
            activeMenu=menu.ActiveMenu
        )
        
        # 查找子菜单
        children = []
        for child_menu in menu_map.values():
            if child_menu.ParentId == menu.MenuId:
                child_route = self._menu_to_route(child_menu, menu_map)
                children.append(child_route)
        
        # 按MenuOrder排序子菜单
        children.sort(key=lambda x: getattr(menu_map.get(self._get_menu_id_by_name(x.name, menu_map), Menu()), 'MenuOrder', 0))
        
        # 构建路由项
        route = RouteItem(
            path=menu.Path,
            component=menu.Component,
            redirect=menu.Redirect,
            name=menu.Name,
            meta=meta,
            children=children if children else None
        )
        
        return route

    def _get_menu_id_by_name(self, name: str, menu_map: dict) -> Optional[int]:
        """根据路由名称获取菜单ID"""
        for menu_id, menu in menu_map.items():
            if menu.Name == name:
                return menu_id
        return None

role_service = RoleService() 