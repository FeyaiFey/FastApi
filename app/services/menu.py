from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.crud.menu import get_menu_crud
from app.schemas.menu import Menu, MenuCreate, MenuUpdate, MenuTree
from app.core.logger import get_logger
from app.exceptions.base import NotFoundError, ValidationError

logger = get_logger("menu.service")

class MenuService:
    
    async def create_menu(self, db: Session, menu_in: MenuCreate) -> Menu:
        """创建菜单"""
        menu_crud = get_menu_crud(db)
        
        # 检查MenuId是否已存在
        if await menu_crud.check_menu_id_exists(menu_in.MenuId):
            raise ValidationError(f"菜单ID {menu_in.MenuId} 已存在")
        
        # 检查菜单名称是否已存在
        if await menu_crud.check_name_exists(menu_in.Name):
            raise ValidationError(f"菜单名称 {menu_in.Name} 已存在")
        
        # 检查路径是否已存在
        if await menu_crud.check_path_exists(menu_in.Path):
            raise ValidationError(f"路由路径 {menu_in.Path} 已存在")
        
        # 如果指定了父菜单，检查父菜单是否存在
        if menu_in.ParentId:
            parent_menu = await menu_crud.get_by_menu_id(menu_in.ParentId)
            if not parent_menu:
                raise ValidationError(f"父菜单 {menu_in.ParentId} 不存在")
        
        menu = await menu_crud.create(menu_in)
        logger.info(f"创建菜单成功: {menu.Name}")
        return menu

    async def get_menus(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        hidden: Optional[bool] = None,
        parent_id: Optional[int] = None
    ) -> List[Menu]:
        """获取菜单列表"""
        menu_crud = get_menu_crud(db)
        return await menu_crud.get_multi(skip=skip, limit=limit, hidden=hidden, parent_id=parent_id)

    async def get_menu_by_id(self, db: Session, menu_id: UUID) -> Menu:
        """根据ID获取菜单"""
        menu_crud = get_menu_crud(db)
        menu = await menu_crud.get_by_id(menu_id)
        
        if not menu:
            raise NotFoundError("菜单不存在")
        
        return menu

    async def get_menu_by_menu_id(self, db: Session, menu_id: int) -> Optional[Menu]:
        """根据MenuId获取菜单"""
        menu_crud = get_menu_crud(db)
        return await menu_crud.get_by_menu_id(menu_id)

    async def update_menu(self, db: Session, menu_id: UUID, menu_update: MenuUpdate) -> Menu:
        """更新菜单"""
        menu_crud = get_menu_crud(db)
        
        # 检查菜单是否存在
        menu = await menu_crud.get_by_id(menu_id)
        if not menu:
            raise NotFoundError("菜单不存在")
        
        # 检查更新数据
        update_data = menu_update.model_dump(exclude_unset=True)
        
        # 检查菜单名称是否被其他菜单使用
        if "Name" in update_data:
            if await menu_crud.check_name_exists(update_data["Name"], exclude_id=menu_id):
                raise ValidationError(f"菜单名称 {update_data['Name']} 已被其他菜单使用")
        
        # 检查路径是否被其他菜单使用
        if "Path" in update_data:
            if await menu_crud.check_path_exists(update_data["Path"], exclude_id=menu_id):
                raise ValidationError(f"路由路径 {update_data['Path']} 已被其他菜单使用")
        
        # 检查父菜单是否存在
        if "ParentId" in update_data and update_data["ParentId"]:
            parent_menu = await menu_crud.get_by_menu_id(update_data["ParentId"])
            if not parent_menu:
                raise ValidationError(f"父菜单 {update_data['ParentId']} 不存在")
            
            # 防止将菜单设置为自己的子菜单
            if update_data["ParentId"] == menu.MenuId:
                raise ValidationError("不能将菜单设置为自己的子菜单")
        
        updated_menu = await menu_crud.update(menu_id, menu_update)
        logger.info(f"更新菜单成功: {menu_id}")
        return updated_menu

    async def delete_menu(self, db: Session, menu_id: UUID) -> None:
        """删除菜单"""
        menu_crud = get_menu_crud(db)
        
        # 检查菜单是否存在
        menu = await menu_crud.get_by_id(menu_id)
        if not menu:
            raise NotFoundError("菜单不存在")
        
        # 检查是否有子菜单
        children = await menu_crud.get_children(menu.MenuId)
        if children:
            raise ValidationError("该菜单下还有子菜单，无法删除")
        
        success = await menu_crud.delete(menu_id)
        if not success:
            raise NotFoundError("菜单不存在")
        
        logger.info(f"删除菜单成功: {menu_id}")

    async def get_menu_tree(self, db: Session, show_hidden: bool = False) -> List[MenuTree]:
        """获取菜单树"""
        menu_crud = get_menu_crud(db)
        return await menu_crud.get_menu_tree(show_hidden=show_hidden)

    async def get_menu_count(self, db: Session, hidden: Optional[bool] = None) -> int:
        """获取菜单总数"""
        menu_crud = get_menu_crud(db)
        return await menu_crud.count(hidden=hidden)

    async def get_next_menu_id(self, db: Session) -> int:
        """获取下一个可用的MenuId"""
        menu_crud = get_menu_crud(db)
        return await menu_crud.get_next_menu_id()

    async def toggle_menu_visibility(self, db: Session, menu_id: UUID) -> Menu:
        """切换菜单显示/隐藏状态"""
        menu_crud = get_menu_crud(db)
        menu = await menu_crud.get_by_id(menu_id)
        
        if not menu:
            raise NotFoundError("菜单不存在")
        
        menu_update = MenuUpdate(Hidden=not menu.Hidden)
        return await self.update_menu(db, menu_id, menu_update)

menu_service = MenuService() 