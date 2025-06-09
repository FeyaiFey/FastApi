# 角色菜单关联表使用指南

## 📋 概述

`RoleMenu` 模型用于实现角色和菜单的多对多关系，支持为不同角色分配不同的菜单权限。

## 🎯 数据库表结构

### hRoleMenu 表
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| Id | UNIQUEIDENTIFIER | 主键 | PK, 自动生成 |
| RoleId | UNIQUEIDENTIFIER | 角色ID | FK -> hRoles.Id |
| MenuId | INTEGER | 菜单ID | FK -> hMenu.MenuId |
| IsEnabled | BOOLEAN | 是否启用 | 默认 TRUE |
| CreatedAt | DATETIME | 创建时间 | 自动生成 |
| UpdatedAt | DATETIME | 更新时间 | 自动更新 |

### 索引设计
- `ix_role_menu_unique`: RoleId + MenuId 联合唯一索引
- `ix_role_menu_role_id`: RoleId 索引（提高查询性能）
- `ix_role_menu_menu_id`: MenuId 索引（提高查询性能）
- `ix_role_menu_enabled`: IsEnabled 索引（状态筛选）

## 🔗 模型关系

### 多对多关系
```python
# 角色可以拥有多个菜单
role.menus  # 获取角色的所有菜单

# 菜单可以分配给多个角色
menu.roles  # 获取拥有此菜单的所有角色

# 直接访问关联表
role.role_menus  # 获取角色的菜单关联记录
menu.role_menus  # 获取菜单的角色关联记录
```

## 📝 常用操作示例

### 1. 为角色分配菜单
```python
from app.models import RoleMenu
from sqlalchemy.orm import Session

# 单个分配
role_menu = RoleMenu(
    RoleId="role-uuid-here",
    MenuId=1001,
    IsEnabled=True
)
db.add(role_menu)
db.commit()

# 批量分配
menu_ids = [1001, 1002, 1003]
role_id = "role-uuid-here"

for menu_id in menu_ids:
    role_menu = RoleMenu(
        RoleId=role_id,
        MenuId=menu_id,
        IsEnabled=True
    )
    db.add(role_menu)
db.commit()
```

### 2. 查询角色的菜单
```python
from app.models import Role, Menu, RoleMenu
from sqlalchemy import and_

# 方法1：通过关系查询
role = db.query(Role).filter(Role.Id == role_id).first()
menus = role.menus  # 所有分配给该角色的菜单

# 方法2：通过关联表查询
role_menus = db.query(RoleMenu).filter(
    and_(
        RoleMenu.RoleId == role_id,
        RoleMenu.IsEnabled == True
    )
).all()

# 方法3：联表查询获取详细信息
query = db.query(
    RoleMenu,
    Role.RoleName,
    Menu.Name.label("MenuName"),
    Menu.Title.label("MenuTitle"),
    Menu.Path.label("MenuPath")
).join(Role, RoleMenu.RoleId == Role.Id)\
 .join(Menu, RoleMenu.MenuId == Menu.MenuId)\
 .filter(RoleMenu.RoleId == role_id)

results = query.all()
```

### 3. 查询菜单的角色
```python
# 查询拥有特定菜单的所有角色
menu_id = 1001
role_menus = db.query(RoleMenu).filter(
    and_(
        RoleMenu.MenuId == menu_id,
        RoleMenu.IsEnabled == True
    )
).all()

role_ids = [rm.RoleId for rm in role_menus]
roles = db.query(Role).filter(Role.Id.in_(role_ids)).all()
```

### 4. 更新菜单分配
```python
# 禁用特定角色的某个菜单
role_menu = db.query(RoleMenu).filter(
    and_(
        RoleMenu.RoleId == role_id,
        RoleMenu.MenuId == menu_id
    )
).first()

if role_menu:
    role_menu.IsEnabled = False
    db.commit()

# 重新分配角色菜单（先删除再添加）
# 1. 删除现有分配
db.query(RoleMenu).filter(RoleMenu.RoleId == role_id).delete()

# 2. 添加新分配
new_menu_ids = [1001, 1002, 1003]
for menu_id in new_menu_ids:
    role_menu = RoleMenu(
        RoleId=role_id,
        MenuId=menu_id,
        IsEnabled=True
    )
    db.add(role_menu)
db.commit()
```

## 🚀 API 设计建议

### 基础 CRUD 接口
```python
# POST /api/v1/role-menus - 创建角色菜单关联
# GET /api/v1/role-menus - 查询角色菜单关联列表
# PUT /api/v1/role-menus/{id} - 更新角色菜单关联
# DELETE /api/v1/role-menus/{id} - 删除角色菜单关联
```

### 业务接口
```python
# POST /api/v1/roles/{role_id}/menus - 批量分配菜单给角色
# GET /api/v1/roles/{role_id}/menus - 获取角色的菜单列表
# DELETE /api/v1/roles/{role_id}/menus - 清空角色的菜单分配

# GET /api/v1/menus/{menu_id}/roles - 获取拥有菜单的角色列表
# POST /api/v1/menus/{menu_id}/roles - 批量分配角色给菜单
```

### 权限验证接口
```python
# GET /api/v1/users/{user_id}/accessible-menus - 获取用户可访问的菜单
# POST /api/v1/check-menu-permission - 检查用户对菜单的访问权限
```

## 🔐 权限控制流程

### 用户菜单权限获取流程
1. 根据用户ID获取用户角色
2. 根据角色ID查询 RoleMenu 表
3. 获取角色拥有的所有启用菜单
4. 构建用户可访问的菜单树

```python
def get_user_accessible_menus(user_id: str, db: Session):
    """获取用户可访问的菜单"""
    # 1. 获取用户角色
    user = db.query(User).filter(User.Id == user_id).first()
    if not user:
        return []
    
    # 2. 查询角色菜单
    role_menus = db.query(RoleMenu).filter(
        and_(
            RoleMenu.RoleId == user.RoleId,
            RoleMenu.IsEnabled == True
        )
    ).all()
    
    # 3. 获取菜单详情
    menu_ids = [rm.MenuId for rm in role_menus]
    menus = db.query(Menu).filter(
        and_(
            Menu.MenuId.in_(menu_ids),
            Menu.Hidden == False
        )
    ).order_by(Menu.MenuOrder, Menu.MenuId).all()
    
    return menus
```

## ⚠️ 注意事项

1. **唯一性约束**: 同一角色不能重复分配同一菜单
2. **软删除**: 使用 `IsEnabled` 字段实现软删除，不直接删除记录
3. **性能优化**: 合理使用索引，避免全表扫描
4. **数据一致性**: 删除角色或菜单时，需要处理关联表中的数据
5. **权限缓存**: 考虑缓存用户权限信息，提高系统性能

## 🎨 扩展功能

### 可选的扩展字段
如果需要更复杂的权限控制，可以考虑添加以下字段：

```python
class RoleMenu(BaseModel):
    # ... 现有字段 ...
    
    # 扩展字段
    PermissionLevel = Column(Integer, default=1, comment="权限级别：1-只读，2-读写，3-管理")
    ExpiryDate = Column(DateTime, nullable=True, comment="权限过期时间")
    GrantedBy = Column(UNIQUEIDENTIFIER, nullable=True, comment="授权人ID")
    Remarks = Column(Text, nullable=True, comment="备注信息")
``` 