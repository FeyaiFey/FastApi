# 异常处理使用指南

## 📋 概述

项目已经定义了完整的异常处理系统，包括：
- 自定义异常类
- 全局异常处理器
- 统一的错误响应格式

## 🎯 异常类层级

```
BaseAPIException
├── ValidationError (422)        # 数据验证错误
├── AuthenticationError (401)    # 认证错误  
├── PermissionError (403)        # 权限错误
├── NotFoundError (404)          # 资源不存在
└── DatabaseError (500)          # 数据库错误
```

## ✅ 在路由中使用异常

### 1. 导入异常类
```python
from app.exceptions.base import (
    BaseAPIException,
    ValidationError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    DatabaseError
)
```

### 2. 优化后的路由风格

#### ✅ 推荐写法（使用项目异常系统）
```python
@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserSchema:
    """根据ID获取用户"""
    user = await user_service.get_user(db, user_id)
    if not user:
        raise NotFoundError("用户不存在")
    return user

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_user)
) -> UserSchema:
    """创建用户"""
    # 检查邮箱是否已存在
    existing_user = await user_service.get_user_by_email(db, user_in.email)
    if existing_user:
        raise ValidationError("该邮箱已被注册")
    
    return await user_service.create_user(db, user_in)
```

#### ❌ 旧写法（使用HTTPException）
```python
@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        user = await user_service.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户失败"
        )
```

## 📝 各种场景的异常使用

### 1. 资源不存在
```python
# 用户不存在
user = await user_service.get_user(db, user_id)
if not user:
    raise NotFoundError("用户不存在")

# 菜单不存在  
menu = await menu_service.get_menu(db, menu_id)
if not menu:
    raise NotFoundError("菜单不存在")
```

### 2. 数据验证错误
```python
# 邮箱已存在
if await user_service.email_exists(db, email):
    raise ValidationError("该邮箱已被注册")

# 菜单ID重复
if await menu_service.menu_id_exists(db, menu_id):
    raise ValidationError(f"菜单ID {menu_id} 已存在")

# 父菜单不存在
if parent_id and not await menu_service.get_by_menu_id(db, parent_id):
    raise ValidationError(f"父菜单 {parent_id} 不存在")
```

### 3. 权限错误
```python
# 用户权限不足
if not await permission_service.check_admin_permission(current_user):
    raise PermissionError("需要管理员权限")

# 只能操作自己的数据
if resource.owner_id != current_user.Id:
    raise PermissionError("无权操作他人数据")
```

### 4. 认证错误
```python
# 令牌无效
if not token_valid:
    raise AuthenticationError("令牌无效")

# 密码错误
if not verify_password(password, user.hashed_password):
    raise AuthenticationError("用户名或密码错误")
```

### 5. 数据库错误
```python
try:
    db.commit()
except SQLAlchemyError as e:
    db.rollback()
    raise DatabaseError("数据保存失败")
```

## 🔧 Service层异常处理

### 推荐在Service层处理业务逻辑异常
```python
# app/services/user.py
async def create_user(self, db: Session, user_in: UserCreate) -> User:
    # 检查邮箱是否已存在
    if await self.get_user_by_email(db, user_in.email):
        raise ValidationError("该邮箱已被注册")
    
    try:
        # 创建用户逻辑
        user = await crud_user.create(db, user_in)
        return user
    except SQLAlchemyError:
        raise DatabaseError("用户创建失败")

# app/services/menu.py  
async def delete_menu(self, db: Session, menu_id: UUID) -> None:
    menu = await self.get_menu(db, menu_id)
    if not menu:
        raise NotFoundError("菜单不存在")
    
    # 检查是否有子菜单
    children = await self.get_children(db, menu.MenuId)
    if children:
        raise ValidationError("该菜单下还有子菜单，无法删除")
    
    try:
        await crud_menu.delete(db, menu_id)
    except SQLAlchemyError:
        raise DatabaseError("菜单删除失败")
```

## 📊 统一错误响应格式

所有异常都会返回统一格式：
```json
{
    "code": 404,
    "message": "用户不存在", 
    "data": null
}
```

验证错误会返回详细信息：
```json
{
    "code": 422,
    "message": "数据验证错误",
    "data": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

## ✨ 最佳实践

1. **Service层处理业务异常**：在Service层抛出具体的业务异常
2. **路由层简化处理**：路由层只需调用Service，让异常自然抛出
3. **使用具体异常类**：根据错误类型使用对应的异常类
4. **提供有意义的错误信息**：错误信息要对用户有帮助
5. **记录详细日志**：异常处理器会自动记录详细的错误日志

## 🔄 迁移现有代码

将现有的 try-catch 风格改为异常抛出风格：

### Before:
```python
try:
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
except HTTPException:
    raise
except Exception as e:
    logger.error(f"获取用户失败: {str(e)}")
    raise HTTPException(status_code=500, detail="获取用户失败")
```

### After:
```python
user = await user_service.get_user(db, user_id)
if not user:
    raise NotFoundError("用户不存在")
return user
```

更简洁、更清晰！ 