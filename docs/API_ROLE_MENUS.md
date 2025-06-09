# 角色菜单路由接口文档

## 📋 概述

角色菜单路由接口用于获取指定角色可访问的所有菜单，并将其构建成前端路由格式，与前端路由配置完全一致。

## 🎯 接口详情

### 获取角色菜单路由

**接口路径**: `GET /api/v1/roles/{role_id}/menus`

**接口描述**: 获取指定角色的菜单路由树，返回前端路由格式的数据结构

**请求参数**:
- `role_id` (path, required): 角色ID (UUID格式)

**响应格式**:
```json
{
  "code": 200,
  "message": "角色菜单路由查询成功",
  "data": [
    {
      "path": "/dashboard",
      "component": "#",
      "redirect": "/dashboard/analysis",
      "name": "Dashboard",
      "meta": {
        "title": "router.dashboard",
        "icon": "vi-ant-design:dashboard-filled",
        "alwaysShow": true,
        "noCache": false,
        "affix": false,
        "hidden": false,
        "noTagsView": false,
        "canTo": true,
        "permission": null,
        "activeMenu": null
      },
      "children": [
        {
          "path": "analysis",
          "component": "views/Dashboard/Analysis",
          "redirect": null,
          "name": "Analysis",
          "meta": {
            "title": "router.analysis",
            "icon": null,
            "alwaysShow": false,
            "noCache": true,
            "affix": true,
            "hidden": false,
            "noTagsView": false,
            "canTo": true,
            "permission": null,
            "activeMenu": null
          },
          "children": null
        }
      ]
    }
  ],
  "success": true,
  "timestamp": 1699123456789
}
```

## 🔧 数据结构说明

### RouteItem (路由项)
| 字段 | 类型 | 描述 | 示例 |
|------|------|------|------|
| path | string | 路由路径 | "/dashboard" |
| component | string | 组件路径 | "views/Dashboard/Analysis" |
| redirect | string | 重定向路径 | "/dashboard/analysis" |
| name | string | 路由名称 | "Dashboard" |
| meta | RouteMeta | 路由元数据 | 见下表 |
| children | RouteItem[] | 子路由数组 | 递归结构 |

### RouteMeta (路由元数据)
| 字段 | 类型 | 描述 | 示例 |
|------|------|------|------|
| title | string | 菜单标题 | "router.dashboard" |
| icon | string | 菜单图标 | "vi-ant-design:dashboard-filled" |
| alwaysShow | boolean | 是否总是显示 | true |
| noCache | boolean | 是否不缓存 | false |
| affix | boolean | 是否固定标签 | true |
| hidden | boolean | 是否隐藏 | false |
| noTagsView | boolean | 是否不显示标签视图 | false |
| canTo | boolean | 是否可以跳转 | true |
| permission | string[] | 权限标识数组 | ["user:view"] |
| activeMenu | string | 激活菜单路径 | "/example/example-page" |

## 🚀 使用示例

### cURL 示例
```bash
curl -X GET "http://localhost:8000/api/v1/roles/{role_id}/menus" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json"
```

### JavaScript 示例
```javascript
// 获取角色菜单路由
const getRoleMenus = async (roleId) => {
  try {
    const response = await axios.get(`/api/v1/roles/${roleId}/menus`);
    console.log('角色菜单路由:', response.data);
    return response.data;
  } catch (error) {
    console.error('获取角色菜单失败:', error.response.data.message);
    throw error;
  }
};

// 使用示例
const roleId = "8be8329a-2992-11f0-8c71-0c9a3cfe6f18";
getRoleMenus(roleId).then(routes => {
  // 将路由数据传递给前端路由器
  router.addRoutes(routes);
});
```

### Python 示例
```python
import requests

def get_role_menus(role_id: str, access_token: str):
    """获取角色菜单路由"""
    url = f"http://localhost:8000/api/v1/roles/{role_id}/menus"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

# 使用示例
role_id = "8be8329a-2992-11f0-8c71-0c9a3cfe6f18"
access_token = "your_access_token"

try:
    result = get_role_menus(role_id, access_token)
    print("角色菜单路由:", result['data'])
except requests.RequestException as e:
    print(f"请求失败: {e}")
```

## 📊 预设示例数据

系统默认包含以下示例数据：

### 角色分配
- **超级管理员** (SUPER_ADMIN): 拥有所有菜单权限
- **管理员** (ADMIN): 拥有除权限管理外的所有菜单
- **普通用户** (USER): 只拥有仪表盘和外部链接菜单

### 菜单结构
```
仪表盘 (/dashboard)
├── 分析页 (analysis)
└── 工作台 (workplace)

外部链接 (/external-link)
└── 文档链接 (https://element-plus-admin-doc.cn/)

组件示例 (/components)
└── 表单组件 (form)
    ├── 默认表单 (default-form)
    └── UseForm示例 (use-form)

权限管理 (/authorization)
├── 部门管理 (department) [权限: department:view]
├── 用户管理 (user) [权限: user:view]
├── 角色管理 (role) [权限: role:view]
└── 菜单管理 (menu) [权限: menu:view]
```

## ⚠️ 注意事项

1. **权限控制**: 接口需要用户登录认证，通过 JWT Token 验证
2. **角色存在性**: 如果角色不存在，接口返回 404 错误
3. **菜单过滤**: 只返回启用且非隐藏的菜单
4. **树形结构**: 自动构建菜单的父子关系
5. **排序**: 按 MenuOrder 字段排序

## 🔗 相关接口

- `GET /api/v1/roles` - 获取角色列表
- `GET /api/v1/roles/{role_id}` - 获取角色详情
- `GET /api/v1/menus` - 获取菜单列表
- `GET /api/v1/menus/tree` - 获取菜单树 