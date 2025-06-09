from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import json

from app.crud.role import role as crud_role
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.schemas.role_menu import RouteItem, RouteMeta
from app.models.role_menu import RoleMenu
from app.models.menu import Menu
from app.core.logger import get_logger
from app.exceptions.base import ValidationError, NotFoundError

logger = get_logger("role.service")

class RoleService:
    
    async def create_role(self, db: Session, role_in: RoleCreate) -> Role:
        """创建角色"""
        
        # 检查角色名称或代码是否已存在
        if await crud_role.check_role_exists(db, role_in.RoleName, role_in.RoleCode):
            raise ValidationError("角色名称或代码已存在")
        
        role = await crud_role.create(db, role_in)
        logger.info(f"创建角色成功: {role.RoleName}")
        return role

    async def get_roles(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        status_filter: Optional[str] = None
    ) -> List[Role]:
        """获取角色列表"""
        return await crud_role.get_multi(db, skip=skip, limit=limit, status=status_filter)

    async def get_role_by_id(self, db: Session, role_id: UUID) -> Role:
        """根据ID获取角色"""
        role = await crud_role.get_by_id(db, role_id)
        
        if not role:
            raise NotFoundError("角色不存在")
        
        return role

    async def get_role_by_name(self, db: Session, role_name: str) -> Optional[Role]:
        """根据角色名称获取角色"""
        role = await crud_role.get_by_name(db, role_name)
        
        if not role:
            raise NotFoundError("角色不存在")
        
        return role

    async def get_role_by_code(self, db: Session, role_code: str) -> Optional[Role]:
        """根据角色代码获取角色"""
        role = await crud_role.get_by_code(db, role_code)
        
        if not role:
            raise NotFoundError("角色不存在")
        
        return role

    async def update_role(self, db: Session, role_id: UUID, role_update: RoleUpdate) -> Role:
        """更新角色"""
        role = await crud_role.update(db, role_id, role_update)
        
        # 检查角色是否存在
        role = await crud_role.get_by_id(db, role_id)
        if not role:
            raise NotFoundError("角色不存在")
        
        # 检查角色名称或代码是否已被其他角色使用
        update_data = role_update.model_dump(exclude_unset=True)
        if "RoleName" in update_data or "RoleCode" in update_data:
            role_name = update_data.get("RoleName", role.RoleName)
            role_code = update_data.get("RoleCode", role.RoleCode)
            if await crud_role.check_role_exists(db, role_name, role_code, exclude_id=role_id):
                raise ValidationError("角色名称或代码已被其他角色使用")
        
        updated_role = await crud_role.update(db, role_id, role_update)
        logger.info(f"更新角色成功: {role_id}")
        return updated_role

    async def delete_role(self, db: Session, role_id: UUID) -> None:
        """删除角色"""
        role = await crud_role.get_by_id(db, role_id)
        
        # 检查角色是否存在
        if not role:
            raise NotFoundError("角色不存在")
        
        # TODO: 检查是否有用户使用此角色，如果有则不允许删除
        # 这里可以添加相关逻辑
        # from app.crud.user import user as crud_user
        # users_with_role = await crud_user.get_by_role_id(db, role_id)
        # if users_with_role:
        #     raise ValidationError("该角色下还有用户，无法删除")
        
        success = await crud_role.delete(db, role_id)
        if not success:
            raise NotFoundError("角色不存在")
        
        logger.info(f"删除角色成功: {role_id}")

    async def get_role_count(self, db: Session, status_filter: Optional[str] = None) -> int:
        """获取角色总数"""
        return await crud_role.count(db, status=status_filter)

    async def change_role_status(self, db: Session, role_id: UUID, status: str) -> Role:
        """更改角色状态"""
        if status not in ["0", "1"]:
            raise ValidationError("状态值无效，只能是0（禁用）或1（启用）")
        
        role_update = RoleUpdate(Status=status)
        return await self.update_role(db, role_id, role_update)

    async def get_default_role(self, db: Session) -> Optional[Role]:
        """获取默认角色"""
        # 假设默认角色的代码为 'user' 或者状态为某个特定值
        # 这里需要根据实际业务逻辑调整
        return await crud_role.get_by_code(db, "user")

    async def get_role_menus(self, db: Session, role_id: UUID) -> List[RouteItem]:
        """获取角色的菜单路由"""
        # 检查角色是否存在
        role = await self.get_role_by_id(db, role_id)
        if not role:
            raise NotFoundError("角色不存在")
        
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