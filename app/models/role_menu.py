from sqlalchemy import Column, Integer, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.models.base import BaseModel

class RoleMenu(BaseModel):
    """角色菜单关联表"""
    __tablename__ = "hRoleMenu"

    RoleId = Column(
        UNIQUEIDENTIFIER, 
        ForeignKey("hRoles.Id"), 
        nullable=False, 
        comment="角色ID"
    )
    MenuId = Column(
        Integer, 
        ForeignKey("hMenu.MenuId"), 
        nullable=False, 
        comment="菜单ID"
    )
    IsEnabled = Column(
        Boolean, 
        default=True, 
        nullable=False, 
        comment="是否启用：True-启用，False-禁用"
    )

    # 关系
    role = relationship("Role", backref="role_menus")
    menu = relationship("Menu", backref="role_menus")

    # 索引和约束
    __table_args__ = (
        # 联合唯一索引，确保同一角色不能重复分配同一菜单
        Index('ix_role_menu_unique', 'RoleId', 'MenuId', unique=True),
        # 单独索引，提高查询性能
        Index('ix_role_menu_role_id', 'RoleId'),
        Index('ix_role_menu_menu_id', 'MenuId'),
        Index('ix_role_menu_enabled', 'IsEnabled'),
    )

    def __repr__(self):
        return f"<RoleMenu(RoleId={self.RoleId}, MenuId={self.MenuId}, IsEnabled={self.IsEnabled})>" 