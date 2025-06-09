from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Menu(BaseModel):
    """菜单模型"""
    __tablename__ = "hMenu"

    MenuId = Column(Integer, nullable=False, unique=True, index=True, comment="菜单ID，从1000开始递增")
    ParentId = Column(Integer, ForeignKey("hMenu.MenuId"), nullable=True, comment="父菜单ID")
    
    # 路由基本信息 (对应 AppCustomRouteRecordRaw)
    Path = Column(String(255), nullable=False, comment="路由路径")
    Component = Column(String(255), nullable=True, comment="组件路径")
    Redirect = Column(String(255), nullable=True, comment="重定向路径")
    Name = Column(String(100), nullable=False, comment="路由名称")
    
    # Meta 信息 (对应 RouteMetaCustom)
    Title = Column(String(255), nullable=True, comment="菜单标题")
    Icon = Column(String(255), nullable=True, comment="菜单图标")
    Hidden = Column(Boolean, default=False, nullable=True, comment="是否隐藏")
    AlwaysShow = Column(Boolean, default=False, nullable=True, comment="是否总是显示")
    NoCache = Column(Boolean, default=False, nullable=True, comment="是否不缓存")
    Breadcrumb = Column(Boolean, default=True, nullable=True, comment="是否显示面包屑")
    Affix = Column(Boolean, default=False, nullable=True, comment="是否固定标签")
    ActiveMenu = Column(String(255), nullable=True, comment="激活菜单路径")
    NoTagsView = Column(Boolean, default=False, nullable=True, comment="是否不显示标签视图")
    CanTo = Column(Boolean, default=True, nullable=True, comment="是否可以跳转")
    Permission = Column(JSON, nullable=True, comment="权限标识数组")
    
    # 额外的数据库字段
    ExternalLink = Column(String(255), nullable=True, comment="外部链接")
    MenuOrder = Column(Integer, default=0, nullable=True, comment="菜单排序")

    # 关系
    parent = relationship("Menu", remote_side="Menu.MenuId", backref="children")
    
    # 多对多关系：菜单可以分配给多个角色
    roles = relationship(
        "Role", 
        secondary="hRoleMenu", 
        back_populates="menus",
        primaryjoin="Menu.MenuId == RoleMenu.MenuId",
        secondaryjoin="Role.Id == RoleMenu.RoleId",
        viewonly=True
    )

    # 索引
    __table_args__ = (
        Index('ix_hmenu_parent_id', 'ParentId'),
        Index('ix_hmenu_menu_order', 'MenuOrder'),
        Index('ix_hmenu_menu_id', 'MenuId'),
    ) 