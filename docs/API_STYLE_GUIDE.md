# FastAPI 路由风格指南

## 📋 概述

本文档定义了项目中 FastAPI 路由的统一编码风格和最佳实践。

## 🎯 核心原则

### 1. 导入顺序
```python
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.xxx import XxxCreate, XxxUpdate, Xxx
from app.services.xxx import xxx_service
from app.core.logger import get_logger
from app.exceptions.base import NotFoundError, ValidationError, PermissionError
```

### 2. 数据库依赖
✅ **正确使用**：
```python
db: Session = Depends(get_db)
```

❌ **避免使用**：
```python
db: Session = Depends(get_db_session)
```

### 3. 请求参数处理
✅ **正确方式**：
```python
@router.post("/", response_model=UserSchema)
async def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_user)
):
```

❌ **避免方式**：
```python
@router.post("/add")
async def create_user(
    db: Session = Depends(get_db),
    user_in: UserCreate = Depends(),
    current_user: User = Depends(get_current_user)
):
```

### 4. RESTful 路径设计
✅ **推荐的路径风格**：
```python
# 资源操作
@router.get("/")                    # 获取列表
@router.post("/")                   # 创建资源
@router.get("/{resource_id}")       # 获取单个资源
@router.put("/{resource_id}")       # 完整更新资源
@router.patch("/{resource_id}")     # 部分更新资源
@router.delete("/{resource_id}")    # 删除资源

# 特殊操作
@router.get("/tree")                # 获取树形结构
@router.patch("/{id}/status")       # 状态更新
@router.patch("/{id}/toggle")       # 切换操作
```

❌ **避免的路径风格**：
```python
@router.post("/add")                # 应使用 POST /
@router.delete("/delete/{id}")      # 应使用 DELETE /{id}
@router.put("/{id}/status")         # 应使用 PATCH /{id}/status
```

### 5. 响应模型和状态码
✅ **明确指定**：
```python
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.get("/", response_model=List[UserSchema])
```

### 6. 异常处理标准（🌟 重要）
✅ **使用项目异常系统**：
```python
from app.exceptions.base import NotFoundError, ValidationError, PermissionError

async def get_user(user_id: uuid.UUID, db: Session):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise NotFoundError("用户不存在")
    return user

async def create_user(user_in: UserCreate, db: Session):
    # 检查邮箱是否已存在
    if await user_service.email_exists(db, user_in.email):
        raise ValidationError("该邮箱已被注册")
    
    return await user_service.create_user(db, user_in)
```

❌ **避免使用HTTPException和try-catch**：
```python
# 不要再使用这种方式
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

### 7. 认证中间件
✅ **所有需要认证的端点**：
```python
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
```

### 8. 查询参数处理
✅ **使用 Query 进行参数验证**：
```python
async def get_items(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    status: str = Query(..., regex="^[01]$", description="状态筛选")
):
```

## 📝 完整示例

```python
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services.item import item_service
from app.core.logger import get_logger
from app.exceptions.base import NotFoundError, ValidationError

router = APIRouter()
logger = get_logger("item.api")

@router.get("/", response_model=List[Item])
async def get_items(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    current_user: User = Depends(get_current_user)
) -> List[Item]:
    """获取项目列表"""
    return await item_service.get_items(db, skip=skip, limit=limit)

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    *,
    db: Session = Depends(get_db),
    item_in: ItemCreate,
    current_user: User = Depends(get_current_user)
) -> Item:
    """创建项目"""
    return await item_service.create_item(db, item_in)

@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Item:
    """获取单个项目"""
    item = await item_service.get_item(db, item_id)
    if not item:
        raise NotFoundError("项目不存在")
    return item

@router.patch("/{item_id}", response_model=Item)
async def update_item(
    item_id: UUID,
    item_update: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Item:
    """更新项目"""
    return await item_service.update_item(db, item_id, item_update)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """删除项目"""
    await item_service.delete_item(db, item_id)
    return None
```

## 🎯 异常处理最佳实践

### 可用的异常类
```python
from app.exceptions.base import (
    BaseAPIException,        # 基础异常类
    ValidationError,         # 422 - 数据验证错误
    AuthenticationError,     # 401 - 认证错误  
    PermissionError,         # 403 - 权限错误
    NotFoundError,          # 404 - 资源不存在
    DatabaseError           # 500 - 数据库错误
)
```

### 常见场景
```python
# 资源不存在
if not user:
    raise NotFoundError("用户不存在")

# 数据验证失败
if await user_service.email_exists(db, email):
    raise ValidationError("该邮箱已被注册")

# 权限不足
if resource.owner_id != current_user.Id:
    raise PermissionError("无权操作他人数据")

# 认证失败
if not verify_password(password, user.password_hash):
    raise AuthenticationError("用户名或密码错误")
```

## ✨ 总结

遵循以上风格指南可以确保：
- 代码风格一致性
- 更好的可读性和维护性
- 符合 RESTful API 设计原则
- 统一的错误处理和响应格式
- 自动的异常日志记录
- 良好的类型提示和文档

## 🔄 关键变化

**新风格特点**：
1. **去除try-catch块**：让异常自然抛出，由全局异常处理器处理
2. **使用语义化异常**：根据业务场景选择合适的异常类型
3. **简化路由代码**：路由层专注于参数处理和调用服务
4. **统一错误响应**：所有异常都有一致的响应格式
5. **自动日志记录**：异常处理器自动记录详细的错误信息 