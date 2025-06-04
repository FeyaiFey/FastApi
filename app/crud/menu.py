from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.models.menu import Menu
from app.schemas.menu import MenuCreate, MenuUpdate, MenuTree
from app.core.logger import get_logger
from app.exceptions.base import DatabaseError

logger = get_logger("menu.crud")

class MenuCRUD:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, menu: MenuCreate) -> Menu:
        """创建菜单"""
        try:
            db_menu = Menu(**menu.model_dump())
            self.db.add(db_menu)
            self.db.commit()
            self.db.refresh(db_menu)
            logger.info(f"菜单创建成功: {db_menu.Name}")
            return db_menu
        except SQLAlchemyError as e:
            logger.error(f"创建菜单失败: {str(e)}")
            self.db.rollback()
            raise DatabaseError("菜单创建失败")

    async def get_by_id(self, menu_id: uuid.UUID) -> Optional[Menu]:
        """根据ID获取菜单"""
        try:
            return self.db.query(Menu).filter(Menu.Id == menu_id).first()
        except SQLAlchemyError as e:
            logger.error(f"查询菜单失败: {str(e)}")
            raise DatabaseError("查询菜单失败")

    async def get_by_menu_id(self, menu_id: int) -> Optional[Menu]:
        """根据MenuId获取菜单"""
        try:
            return self.db.query(Menu).filter(Menu.MenuId == menu_id).first()
        except SQLAlchemyError as e:
            logger.error(f"查询菜单失败: {str(e)}")
            raise DatabaseError("查询菜单失败")

    async def get_by_name(self, name: str) -> Optional[Menu]:
        """根据名称获取菜单"""
        try:
            return self.db.query(Menu).filter(Menu.Name == name).first()
        except SQLAlchemyError as e:
            logger.error(f"查询菜单失败: {str(e)}")
            raise DatabaseError("查询菜单失败")

    async def get_by_path(self, path: str) -> Optional[Menu]:
        """根据路径获取菜单"""
        try:
            return self.db.query(Menu).filter(Menu.Path == path).first()
        except SQLAlchemyError as e:
            logger.error(f"查询菜单失败: {str(e)}")
            raise DatabaseError("查询菜单失败")

    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        hidden: Optional[bool] = None,
        parent_id: Optional[int] = None
    ) -> List[Menu]:
        """获取菜单列表"""
        try:
            query = self.db.query(Menu)
            
            if hidden is not None:
                query = query.filter(Menu.Hidden == hidden)
                
            if parent_id is not None:
                query = query.filter(Menu.ParentId == parent_id)
                
            return query.order_by(asc(Menu.MenuOrder), asc(Menu.MenuId)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"查询菜单列表失败: {str(e)}")
            raise DatabaseError("查询菜单列表失败")

    async def get_all_ordered(self) -> List[Menu]:
        """获取所有菜单并按顺序排列"""
        try:
            return self.db.query(Menu).order_by(asc(Menu.MenuOrder), asc(Menu.MenuId)).all()
        except SQLAlchemyError as e:
            logger.error(f"查询菜单列表失败: {str(e)}")
            raise DatabaseError("查询菜单列表失败")

    async def get_root_menus(self) -> List[Menu]:
        """获取根菜单（没有父菜单的菜单）"""
        try:
            return self.db.query(Menu).filter(Menu.ParentId.is_(None)).order_by(asc(Menu.MenuOrder), asc(Menu.MenuId)).all()
        except SQLAlchemyError as e:
            logger.error(f"查询根菜单失败: {str(e)}")
            raise DatabaseError("查询根菜单失败")

    async def get_children(self, parent_menu_id: int) -> List[Menu]:
        """获取指定菜单的子菜单"""
        try:
            return self.db.query(Menu).filter(Menu.ParentId == parent_menu_id).order_by(asc(Menu.MenuOrder), asc(Menu.MenuId)).all()
        except SQLAlchemyError as e:
            logger.error(f"查询子菜单失败: {str(e)}")
            raise DatabaseError("查询子菜单失败")

    async def count(self, hidden: Optional[bool] = None) -> int:
        """获取菜单总数"""
        try:
            query = self.db.query(Menu)
            
            if hidden is not None:
                query = query.filter(Menu.Hidden == hidden)
                
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"统计菜单数量失败: {str(e)}")
            raise DatabaseError("统计菜单数量失败")

    async def update(self, menu_id: uuid.UUID, menu_update: MenuUpdate) -> Optional[Menu]:
        """更新菜单"""
        try:
            db_menu = await self.get_by_id(menu_id)
            if not db_menu:
                return None
                
            update_data = menu_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_menu, field, value)
                
            self.db.commit()
            self.db.refresh(db_menu)
            logger.info(f"菜单更新成功: {menu_id}")
            return db_menu
        except SQLAlchemyError as e:
            logger.error(f"更新菜单失败: {str(e)}")
            self.db.rollback()
            raise DatabaseError("更新菜单失败")

    async def delete(self, menu_id: uuid.UUID) -> bool:
        """删除菜单"""
        try:
            db_menu = await self.get_by_id(menu_id)
            if not db_menu:
                return False
                
            self.db.delete(db_menu)
            self.db.commit()
            logger.info(f"菜单删除成功: {menu_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"删除菜单失败: {str(e)}")
            self.db.rollback()
            raise DatabaseError("删除菜单失败")

    async def check_menu_id_exists(self, menu_id: int, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """检查MenuId是否已存在"""
        try:
            query = self.db.query(Menu).filter(Menu.MenuId == menu_id)
            
            if exclude_id:
                query = query.filter(Menu.Id != exclude_id)
                
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"检查菜单ID是否存在失败: {str(e)}")
            raise DatabaseError("检查菜单ID失败")

    async def check_name_exists(self, name: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """检查菜单名称是否已存在"""
        try:
            query = self.db.query(Menu).filter(Menu.Name == name)
            
            if exclude_id:
                query = query.filter(Menu.Id != exclude_id)
                
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"检查菜单名称是否存在失败: {str(e)}")
            raise DatabaseError("检查菜单名称失败")

    async def check_path_exists(self, path: str, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """检查路径是否已存在"""
        try:
            query = self.db.query(Menu).filter(Menu.Path == path)
            
            if exclude_id:
                query = query.filter(Menu.Id != exclude_id)
                
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"检查菜单路径是否存在失败: {str(e)}")
            raise DatabaseError("检查菜单路径失败")

    async def get_next_menu_id(self) -> int:
        """获取下一个可用的MenuId（从1000开始）"""
        try:
            max_menu_id = self.db.query(Menu.MenuId).order_by(desc(Menu.MenuId)).first()
            if max_menu_id and max_menu_id[0] >= 1000:
                return max_menu_id[0] + 1
            return 1000
        except SQLAlchemyError as e:
            logger.error(f"获取下一个菜单ID失败: {str(e)}")
            raise DatabaseError("获取下一个菜单ID失败")

    async def build_menu_tree(self, menus: List[Menu], parent_id: Optional[int] = None) -> List[MenuTree]:
        """构建菜单树"""
        tree = []
        for menu in menus:
            if menu.ParentId == parent_id:
                menu_tree = MenuTree(
                    Id=menu.Id,
                    MenuId=menu.MenuId,
                    ParentId=menu.ParentId,
                    Path=menu.Path,
                    Component=menu.Component,
                    Redirect=menu.Redirect,
                    Name=menu.Name,
                    Title=menu.Title,
                    Icon=menu.Icon,
                    AlwaysShow=menu.AlwaysShow,
                    NoCache=menu.NoCache,
                    Affix=menu.Affix,
                    Hidden=menu.Hidden,
                    ExternalLink=menu.ExternalLink,
                    Permission=menu.Permission,
                    MenuOrder=menu.MenuOrder,
                    CreatedAt=menu.CreatedAt,
                    UpdatedAt=menu.UpdatedAt,
                    children=await self.build_menu_tree(menus, menu.MenuId)
                )
                tree.append(menu_tree)
        return tree

    async def get_menu_tree(self, show_hidden: bool = False) -> List[MenuTree]:
        """获取完整的菜单树"""
        try:
            if show_hidden:
                menus = await self.get_all_ordered()
            else:
                menus = self.db.query(Menu).filter(Menu.Hidden == False).order_by(asc(Menu.MenuOrder), asc(Menu.MenuId)).all()
            
            return await self.build_menu_tree(menus)
        except SQLAlchemyError as e:
            logger.error(f"构建菜单树失败: {str(e)}")
            raise DatabaseError("构建菜单树失败")

def get_menu_crud(db: Session) -> MenuCRUD:
    """获取菜单CRUD实例"""
    return MenuCRUD(db) 