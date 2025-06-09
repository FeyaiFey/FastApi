# API 统一响应格式规范

## 📋 概述

为了与前端 Axios 保持一致，所有 API 接口都采用统一的响应格式。

## 🎯 响应格式结构

### 基础响应格式
```typescript
{
  code: number,      // 业务状态码
  message: string,   // 响应消息  
  data: T,          // 响应数据
  success: boolean,  // 是否成功
  timestamp: number  // 时间戳(毫秒)
}
```

## ✅ 成功响应示例

### 1. 单个数据响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "Id": "8be8329a-2992-11f0-8c71-0c9a3cfe6f18",
    "MenuId": 1001,
    "Name": "用户管理",
    "Path": "/users",
    "Title": "用户管理"
  },
  "success": true,
  "timestamp": 1699123456789
}
```

### 2. 列表数据响应（分页）
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [
      {
        "Id": "8be8329a-2992-11f0-8c71-0c9a3cfe6f18",
        "MenuId": 1001,
        "Name": "用户管理"
      }
    ],
    "pagination": {
      "total": 100,
      "page": 1,
      "page_size": 10,
      "total_pages": 10,
      "has_next": true,
      "has_prev": false
    }
  },
  "success": true,
  "timestamp": 1699123456789
}
```

### 3. 创建成功响应
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "Id": "8be8329a-2992-11f0-8c71-0c9a3cfe6f18",
    "MenuId": 1001,
    "Name": "用户管理"
  },
  "success": true,
  "timestamp": 1699123456789
}
```

### 4. 删除成功响应
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null,
  "success": true,
  "timestamp": 1699123456789
}
```

## ❌ 错误响应示例

### 1. 数据验证错误 (422)
```json
{
  "code": 422,
  "message": "数据验证失败: MenuId: 字段必填; Name: 字段长度至少为1",
  "data": null,
  "success": false,
  "timestamp": 1699123456789
}
```

### 2. 资源不存在 (404)
```json
{
  "code": 404,
  "message": "菜单不存在",
  "data": null,
  "success": false,
  "timestamp": 1699123456789
}
```

### 3. 权限不足 (403)
```json
{
  "code": 403,
  "message": "权限不足",
  "data": null,
  "success": false,
  "timestamp": 1699123456789
}
```

### 4. 认证失败 (401)
```json
{
  "code": 401,
  "message": "未授权访问",
  "data": null,
  "success": false,
  "timestamp": 1699123456789
}
```

### 5. 服务器错误 (500)
```json
{
  "code": 500,
  "message": "服务器内部错误",
  "data": null,
  "success": false,
  "timestamp": 1699123456789
}
```

## 📊 业务状态码对照表

| 状态码 | 含义 | HTTP状态码 | 描述 |
|--------|------|------------|------|
| 200 | SUCCESS | 200 | 操作成功 |
| 201 | CREATED | 201 | 创建成功 |
| 400 | BAD_REQUEST | 400 | 请求参数错误 |
| 401 | UNAUTHORIZED | 401 | 未授权访问 |
| 403 | FORBIDDEN | 403 | 访问被禁止 |
| 404 | NOT_FOUND | 404 | 资源不存在 |
| 409 | CONFLICT | 409 | 资源冲突 |
| 422 | VALIDATION_ERROR | 422 | 数据验证失败 |
| 500 | INTERNAL_ERROR | 500 | 服务器内部错误 |
| 501 | DATABASE_ERROR | 500 | 数据库操作失败 |
| 502 | EXTERNAL_SERVICE_ERROR | 500 | 外部服务错误 |

## 🔧 后端开发指南

### 1. 使用响应管理器
```python
from app.core.response import response_manager
from app.schemas.response import SuccessResponse, PaginationResponse

# 成功响应
@router.get("/", response_model=SuccessResponse[Menu])
async def get_menu():
    menu = await menu_service.get_menu()
    return response_manager.success(
        data=menu, 
        message="菜单查询成功"
    )

# 创建响应
@router.post("/", response_model=SuccessResponse[Menu])
async def create_menu(menu_in: MenuCreate):
    menu = await menu_service.create_menu(menu_in)
    return response_manager.created(
        data=menu, 
        message="菜单创建成功"
    )

# 分页响应
@router.get("/list", response_model=PaginationResponse[Menu])
async def get_menu_list(page: int = 1, page_size: int = 10):
    menus, total = await menu_service.get_menu_list(page, page_size)
    return response_manager.paginated(
        items=menus,
        total=total,
        page=page,
        page_size=page_size,
        message="菜单列表查询成功"
    )
```

### 2. 异常处理
```python
from app.exceptions.base import ValidationError, NotFoundError

# 抛出业务异常（会自动转换为统一格式）
if not menu:
    raise NotFoundError("菜单不存在")

if email_exists:
    raise ValidationError("邮箱已存在")
```

## 🌐 前端使用指南

### 1. Axios 响应拦截器
```typescript
// 配置响应拦截器
axios.interceptors.response.use(
  (response) => {
    // 成功响应直接返回 data 字段
    return response.data;
  },
  (error) => {
    // 错误响应统一处理
    const errorData = error.response?.data;
    if (errorData && !errorData.success) {
      // 显示错误信息
      Message.error(errorData.message);
      return Promise.reject(errorData);
    }
    return Promise.reject(error);
  }
);
```

### 2. API 调用示例
```typescript
// 获取单个数据
const getMenu = async (id: string) => {
  const response = await axios.get(`/api/v1/menus/${id}`);
  // response 结构: { code: 200, message: "成功", data: {...}, success: true, timestamp: 123 }
  return response.data; // 直接获取业务数据
};

// 获取分页数据
const getMenuList = async (page: number, pageSize: number) => {
  const response = await axios.get(`/api/v1/menus`, {
    params: { skip: (page - 1) * pageSize, limit: pageSize }
  });
  // response.data.items - 列表数据
  // response.data.pagination - 分页信息
  return response.data;
};
```

## ✨ 特性优势

1. **统一性**: 所有API响应格式一致，便于前端统一处理
2. **类型安全**: TypeScript 泛型支持，编译时类型检查
3. **自动化**: 异常自动转换为统一格式，无需手动处理
4. **分页支持**: 内置分页响应格式，包含完整分页信息
5. **时间戳**: 自动添加时间戳，便于调试和日志追踪
6. **业务状态码**: 区分HTTP状态码和业务状态码，更精确的错误处理 