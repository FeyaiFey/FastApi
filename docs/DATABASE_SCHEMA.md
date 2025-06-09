# 数据库表结构说明

## 📋 概述

本文档详细说明了 FastAPI 项目的 SQL Server 数据库表结构设计。

## 🎯 表关系图

```
hDepartments (部门表)
    ↓ (1:N)
hUsers (用户表)
    ↓ (N:1)
hRoles (角色表)
    ↓ (N:M 通过 hRoleMenu)
hMenu (菜单表)

hUsers (用户表)
    ↓ (1:1)
hEmailConfigs (邮件配置表)
```

## 📊 数据表详细结构

### 1. hDepartments (部门表)

**表描述**: 组织架构管理，支持树形结构

| 字段名 | 数据类型 | 允许NULL | 默认值 | 约束 | 描述 |
|--------|----------|----------|--------|------|------|
| Id | UNIQUEIDENTIFIER | NO | NEWID() | PK | 主键 |
| ParentId | UNIQUEIDENTIFIER | YES | NULL | FK | 父部门ID |
| DepartmentName | NVARCHAR(50) | NO | - | - | 部门名称 |
| Status | NVARCHAR(50) | NO | '1' | - | 状态: 0-禁用, 1-启用 |
| CreatedAt | DATETIME2 | NO | GETDATE() | - | 创建时间 |
| UpdatedAt | DATETIME2 | NO | GETDATE() | - | 更新时间 |

**约束**:
- `FK_hDepartments_ParentId`: 外键关联自身，实现树形结构

**索引**:
- `IX_hDepartments_ParentId`: ParentId 索引
- `IX_hDepartments_Status`: Status 索引

---

### 2. hRoles (角色表)

**表描述**: 用户角色和权限管理

| 字段名 | 数据类型 | 允许NULL | 默认值 | 约束 | 描述 |
|--------|----------|----------|--------|------|------|
| Id | UNIQUEIDENTIFIER | NO | NEWID() | PK | 主键 |
| RoleName | NVARCHAR(50) | NO | - | UNIQUE | 角色名称 |
| RoleCode | NVARCHAR(50) | NO | - | UNIQUE | 角色代码 |
| Description | NTEXT | YES | NULL | - | 角色描述 |
| Status | NVARCHAR(50) | NO | '1' | - | 状态: 0-禁用, 1-启用 |
| CreatedAt | DATETIME2 | NO | GETDATE() | - | 创建时间 |
| UpdatedAt | DATETIME2 | NO | GETDATE() | - | 更新时间 |

**约束**:
- `UQ_hRoles_RoleName`: RoleName 唯一约束
- `UQ_hRoles_RoleCode`: RoleCode 唯一约束

**索引**:
- `IX_hRoles_RoleName`: RoleName 索引
- `IX_hRoles_RoleCode`: RoleCode 索引

---

### 3. hMenu (菜单表)

**表描述**: 系统菜单和路由管理，支持树形结构

| 字段名 | 数据类型 | 允许NULL | 默认值 | 约束 | 描述 |
|--------|----------|----------|--------|------|------|
| Id | UNIQUEIDENTIFIER | NO | NEWID() | PK | 主键 |
| MenuId | INT | NO | - | UNIQUE | 菜单ID (业务主键) |
| ParentId | INT | YES | NULL | FK | 父菜单ID |
| Path | NVARCHAR(255) | NO | - | - | 路由路径 |
| Component | NVARCHAR(255) | YES | NULL | - | 组件路径 |
| Redirect | NVARCHAR(255) | YES | NULL | - | 重定向路径 |
| Name | NVARCHAR(100) | NO | - | - | 路由名称 |
| Title | NVARCHAR(255) | YES | NULL | - | 菜单标题 |
| Icon | NVARCHAR(255) | YES | NULL | - | 菜单图标 |
| Hidden | BIT | YES | 0 | - | 是否隐藏 |
| AlwaysShow | BIT | YES | 0 | - | 是否总是显示 |
| NoCache | BIT | YES | 0 | - | 是否不缓存 |
| Breadcrumb | BIT | YES | 1 | - | 是否显示面包屑 |
| Affix | BIT | YES | 0 | - | 是否固定标签 |
| ActiveMenu | NVARCHAR(255) | YES | NULL | - | 激活菜单路径 |
| NoTagsView | BIT | YES | 0 | - | 是否不显示标签视图 |
| CanTo | BIT | YES | 1 | - | 是否可以跳转 |
| Permission | NVARCHAR(MAX) | YES | NULL | - | 权限标识 (JSON格式) |
| ExternalLink | NVARCHAR(255) | YES | NULL | - | 外部链接 |
| MenuOrder | INT | YES | 0 | - | 菜单排序 |
| CreatedAt | DATETIME2 | NO | GETDATE() | - | 创建时间 |
| UpdatedAt | DATETIME2 | NO | GETDATE() | - | 更新时间 |

**约束**:
- `UQ_hMenu_MenuId`: MenuId 唯一约束
- `FK_hMenu_ParentId`: 外键关联自身，实现树形结构

**索引**:
- `IX_hMenu_MenuId`: MenuId 索引
- `IX_hMenu_ParentId`: ParentId 索引
- `IX_hMenu_MenuOrder`: MenuOrder 索引

---

### 4. hUsers (用户表)

**表描述**: 系统用户信息管理

| 字段名 | 数据类型 | 允许NULL | 默认值 | 约束 | 描述 |
|--------|----------|----------|--------|------|------|
| Id | UNIQUEIDENTIFIER | NO | NEWID() | PK | 主键 |
| UserName | NVARCHAR(50) | NO | - | UNIQUE | 用户名 |
| PasswordHash | NVARCHAR(255) | NO | - | - | 密码哈希 |
| Email | NVARCHAR(255) | NO | - | UNIQUE | 邮箱 |
| DepartmentId | UNIQUEIDENTIFIER | NO | - | FK | 部门ID |
| RoleId | UNIQUEIDENTIFIER | NO | - | FK | 角色ID |
| AvatarUrl | NVARCHAR(255) | NO | - | - | 头像URL |
| Status | NVARCHAR(50) | NO | '1' | - | 状态: 0-禁用, 1-启用 |
| CreatedAt | DATETIME2 | NO | GETDATE() | - | 创建时间 |
| UpdatedAt | DATETIME2 | NO | GETDATE() | - | 更新时间 |

**约束**:
- `UQ_hUsers_UserName`: UserName 唯一约束
- `UQ_hUsers_Email`: Email 唯一约束
- `FK_hUsers_DepartmentId`: 外键关联部门表
- `FK_hUsers_RoleId`: 外键关联角色表

**索引**:
- `IX_hUsers_Email`: Email 索引
- `IX_hUsers_UserName`: UserName 索引
- `IX_hUsers_DepartmentId`: DepartmentId 索引
- `IX_hUsers_RoleId`: RoleId 索引

---

### 5. hRoleMenu (角色菜单关联表)

**表描述**: 角色和菜单的多对多关系表

| 字段名 | 数据类型 | 允许NULL | 默认值 | 约束 | 描述 |
|--------|----------|----------|--------|------|------|
| Id | UNIQUEIDENTIFIER | NO | NEWID() | PK | 主键 |
| RoleId | UNIQUEIDENTIFIER | NO | - | FK | 角色ID |
| MenuId | INT | NO | - | FK | 菜单ID |
| IsEnabled | BIT | NO | 1 | - | 是否启用 |
| CreatedAt | DATETIME2 | NO | GETDATE() | - | 创建时间 |
| UpdatedAt | DATETIME2 | NO | GETDATE() | - | 更新时间 |

**约束**:
- `UQ_hRoleMenu_RoleId_MenuId`: RoleId + MenuId 联合唯一约束
- `FK_hRoleMenu_RoleId`: 外键关联角色表
- `FK_hRoleMenu_MenuId`: 外键关联菜单表

**索引**:
- `IX_hRoleMenu_RoleId`: RoleId 索引
- `IX_hRoleMenu_MenuId`: MenuId 索引
- `IX_hRoleMenu_IsEnabled`: IsEnabled 索引

---

### 6. hEmailConfigs (邮件配置表)

**表描述**: 用户邮件服务器配置信息

| 字段名 | 数据类型 | 允许NULL | 默认值 | 约束 | 描述 |
|--------|----------|----------|--------|------|------|
| Id | UNIQUEIDENTIFIER | NO | NEWID() | PK | 主键 |
| UserId | UNIQUEIDENTIFIER | YES | NULL | FK | 用户ID |
| ImapServer | NVARCHAR(100) | YES | NULL | - | IMAP服务器 |
| ImapPort | INT | YES | NULL | - | IMAP端口 |
| ImapUseSsl | INT | YES | NULL | - | IMAP是否使用SSL |
| SmtpServer | NVARCHAR(100) | YES | NULL | - | SMTP服务器 |
| SmtpPort | INT | YES | NULL | - | SMTP端口 |
| SmtpUseSsl | INT | YES | NULL | - | SMTP是否使用SSL |
| CreatedAt | DATETIME2 | NO | GETDATE() | - | 创建时间 |
| UpdatedAt | DATETIME2 | NO | GETDATE() | - | 更新时间 |

**约束**:
- `FK_hEmailConfigs_UserId`: 外键关联用户表

**索引**:
- `IX_hEmailConfigs_UserId`: UserId 索引

---

## 🔄 UpdatedAt 自动更新触发器

为确保数据的完整性和一致性，系统为所有表创建了 `UpdatedAt` 字段自动更新触发器：

### 触发器列表
- `trg_hDepartments_UpdatedAt`: 部门表更新触发器
- `trg_hRoles_UpdatedAt`: 角色表更新触发器  
- `trg_hMenu_UpdatedAt`: 菜单表更新触发器
- `trg_hUsers_UpdatedAt`: 用户表更新触发器
- `trg_hRoleMenu_UpdatedAt`: 角色菜单关联表更新触发器
- `trg_hEmailConfigs_UpdatedAt`: 邮件配置表更新触发器

### 触发器功能
- **触发时机**: 每当表中的记录被更新时自动触发
- **执行逻辑**: 自动将 `UpdatedAt` 字段设置为当前时间 `GETDATE()`
- **性能优化**: 使用 `SET NOCOUNT ON` 避免额外的计数消息
- **精确匹配**: 通过 `INNER JOIN inserted` 确保只更新被修改的记录

### 触发器示例
```sql
CREATE TRIGGER trg_hUsers_UpdatedAt
ON hUsers
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE hUsers 
    SET UpdatedAt = GETDATE()
    FROM hUsers u
    INNER JOIN inserted i ON u.Id = i.Id;
END;
```

---

## 🔗 表关系说明

### 1. 部门 - 用户 (1:N)
- 一个部门可以有多个用户
- 每个用户必须属于一个部门
- 外键: `hUsers.DepartmentId` → `hDepartments.Id`

### 2. 角色 - 用户 (1:N)
- 一个角色可以分配给多个用户
- 每个用户必须有一个角色
- 外键: `hUsers.RoleId` → `hRoles.Id`

### 3. 角色 - 菜单 (N:M)
- 一个角色可以拥有多个菜单权限
- 一个菜单可以分配给多个角色
- 关联表: `hRoleMenu`
- 外键: `hRoleMenu.RoleId` → `hRoles.Id`
- 外键: `hRoleMenu.MenuId` → `hMenu.MenuId`

### 4. 用户 - 邮件配置 (1:1)
- 一个用户可以有一个邮件配置
- 一个邮件配置属于一个用户
- 外键: `hEmailConfigs.UserId` → `hUsers.Id`

### 5. 部门自关联 (1:N)
- 支持部门树形结构
- 外键: `hDepartments.ParentId` → `hDepartments.Id`

### 6. 菜单自关联 (1:N)
- 支持菜单树形结构
- 外键: `hMenu.ParentId` → `hMenu.MenuId`

---

## 📝 使用说明

1. **执行顺序**: 建议按照依赖关系创建表
   - 先创建独立表: `hDepartments`, `hRoles`, `hMenu`
   - 再创建依赖表: `hUsers`, `hRoleMenu`, `hEmailConfigs`
   - 最后创建触发器

2. **数据类型说明**:
   - `UNIQUEIDENTIFIER`: 使用 UUID 作为主键
   - `NVARCHAR`: 支持 Unicode 字符
   - `DATETIME2`: 精度更高的日期时间类型
   - `BIT`: 布尔类型 (0/1)

3. **字段约束**:
   - `UpdatedAt` 字段已设为必填 (NOT NULL)
   - 创建和更新时间都有默认值 `GETDATE()`
   - 触发器自动维护 `UpdatedAt` 字段

4. **索引策略**:
   - 主键自动创建聚集索引
   - 外键字段创建非聚集索引
   - 常用查询字段创建索引

5. **约束说明**:
   - 使用外键约束保证数据完整性
   - 使用唯一约束防止重复数据
   - 使用默认值简化数据插入
   - 触发器确保时间戳一致性 