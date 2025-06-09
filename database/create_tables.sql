-- =====================================================
-- SQL Server 数据库表创建脚本
-- 基于 FastAPI 项目的 SQLAlchemy 模型生成
-- =====================================================

-- 1. 创建部门表 (hDepartments)
-- 需要先创建，因为用户表依赖它
CREATE TABLE hDepartments (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ParentId UNIQUEIDENTIFIER NULL,
    DepartmentName NVARCHAR(50) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT '1',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- 约束
    CONSTRAINT FK_hDepartments_ParentId FOREIGN KEY (ParentId) REFERENCES hDepartments(Id)
);

-- 为部门表创建索引
CREATE INDEX IX_hDepartments_Id ON hDepartments(Id);
CREATE INDEX IX_hDepartments_ParentId ON hDepartments(ParentId);
CREATE INDEX IX_hDepartments_Status ON hDepartments(Status);

-- 2. 创建角色表 (hRoles)
-- 需要先创建，因为用户表依赖它
CREATE TABLE hRoles (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RoleName NVARCHAR(50) NOT NULL UNIQUE,
    RoleCode NVARCHAR(50) NOT NULL UNIQUE,
    Description NTEXT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT '1',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- 为角色表创建索引
CREATE INDEX IX_hRoles_Id ON hRoles(Id);
CREATE INDEX IX_hRoles_RoleName ON hRoles(RoleName);
CREATE INDEX IX_hRoles_RoleCode ON hRoles(RoleCode);
CREATE INDEX IX_hRoles_Status ON hRoles(Status);

-- 3. 创建菜单表 (hMenu)
-- 可以独立创建
CREATE TABLE hMenu (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    MenuId INT NOT NULL UNIQUE,
    ParentId INT NULL,
    Path NVARCHAR(255) NOT NULL,
    Component NVARCHAR(255) NULL,
    Redirect NVARCHAR(255) NULL,
    Name NVARCHAR(100) NOT NULL,
    Title NVARCHAR(255) NULL,
    Icon NVARCHAR(255) NULL,
    Hidden BIT NULL DEFAULT 0,
    AlwaysShow BIT NULL DEFAULT 0,
    NoCache BIT NULL DEFAULT 0,
    Breadcrumb BIT NULL DEFAULT 1,
    Affix BIT NULL DEFAULT 0,
    ActiveMenu NVARCHAR(255) NULL,
    NoTagsView BIT NULL DEFAULT 0,
    CanTo BIT NULL DEFAULT 1,
    Permission NVARCHAR(MAX) NULL, -- JSON 数据
    ExternalLink NVARCHAR(255) NULL,
    MenuOrder INT NULL DEFAULT 0,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- 约束
    CONSTRAINT FK_hMenu_ParentId FOREIGN KEY (ParentId) REFERENCES hMenu(MenuId)
);

-- 为菜单表创建索引
CREATE INDEX IX_hMenu_Id ON hMenu(Id);
CREATE INDEX IX_hMenu_MenuId ON hMenu(MenuId);
CREATE INDEX IX_hMenu_ParentId ON hMenu(ParentId);
CREATE INDEX IX_hMenu_MenuOrder ON hMenu(MenuOrder);
CREATE INDEX IX_hMenu_Hidden ON hMenu(Hidden);
CREATE INDEX IX_hMenu_Name ON hMenu(Name);

-- 4. 创建用户表 (hUsers)
-- 依赖部门表和角色表
CREATE TABLE hUsers (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserName NVARCHAR(50) NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    Email NVARCHAR(255) NOT NULL,
    DepartmentId UNIQUEIDENTIFIER NOT NULL,
    RoleId UNIQUEIDENTIFIER NOT NULL,
    AvatarUrl NVARCHAR(255) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT '1',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- 约束
    CONSTRAINT FK_hUsers_DepartmentId FOREIGN KEY (DepartmentId) REFERENCES hDepartments(Id),
    CONSTRAINT FK_hUsers_RoleId FOREIGN KEY (RoleId) REFERENCES hRoles(Id),
    CONSTRAINT UQ_hUsers_Email UNIQUE (Email),
    CONSTRAINT UQ_hUsers_UserName UNIQUE (UserName)
);

-- 为用户表创建索引
CREATE INDEX IX_hUsers_Id ON hUsers(Id);
CREATE INDEX IX_hUsers_Email ON hUsers(Email);
CREATE INDEX IX_hUsers_UserName ON hUsers(UserName);
CREATE INDEX IX_hUsers_DepartmentId ON hUsers(DepartmentId);
CREATE INDEX IX_hUsers_RoleId ON hUsers(RoleId);
CREATE INDEX IX_hUsers_Status ON hUsers(Status);

-- 5. 创建角色菜单关联表 (hRoleMenu)
-- 依赖角色表和菜单表
CREATE TABLE hRoleMenu (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RoleId UNIQUEIDENTIFIER NOT NULL,
    MenuId INT NOT NULL,
    IsEnabled BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- 约束
    CONSTRAINT FK_hRoleMenu_RoleId FOREIGN KEY (RoleId) REFERENCES hRoles(Id),
    CONSTRAINT FK_hRoleMenu_MenuId FOREIGN KEY (MenuId) REFERENCES hMenu(MenuId),
    CONSTRAINT UQ_hRoleMenu_RoleId_MenuId UNIQUE (RoleId, MenuId)
);

-- 为角色菜单关联表创建索引
CREATE INDEX IX_hRoleMenu_Id ON hRoleMenu(Id);
CREATE INDEX IX_hRoleMenu_RoleId ON hRoleMenu(RoleId);
CREATE INDEX IX_hRoleMenu_MenuId ON hRoleMenu(MenuId);
CREATE INDEX IX_hRoleMenu_IsEnabled ON hRoleMenu(IsEnabled);

-- 6. 创建邮件配置表 (hEmailConfigs)
-- 依赖用户表
CREATE TABLE hEmailConfigs (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserId UNIQUEIDENTIFIER NULL,
    ImapServer NVARCHAR(100) NULL,
    ImapPort INT NULL,
    ImapUseSsl INT NULL,
    SmtpServer NVARCHAR(100) NULL,
    SmtpPort INT NULL,
    SmtpUseSsl INT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- 约束
    CONSTRAINT FK_hEmailConfigs_UserId FOREIGN KEY (UserId) REFERENCES hUsers(Id)
);

-- 为邮件配置表创建索引
CREATE INDEX IX_hEmailConfigs_Id ON hEmailConfigs(Id);
CREATE INDEX IX_hEmailConfigs_UserId ON hEmailConfigs(UserId);

-- =====================================================
-- 创建 UpdatedAt 自动更新触发器
-- =====================================================

-- 部门表触发器
GO
CREATE TRIGGER trg_hDepartments_UpdatedAt
ON hDepartments
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE hDepartments 
    SET UpdatedAt = GETDATE()
    FROM hDepartments d
    INNER JOIN inserted i ON d.Id = i.Id;
END;

-- 角色表触发器
GO
CREATE TRIGGER trg_hRoles_UpdatedAt
ON hRoles
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE hRoles 
    SET UpdatedAt = GETDATE()
    FROM hRoles r
    INNER JOIN inserted i ON r.Id = i.Id;
END;

-- 菜单表触发器
GO
CREATE TRIGGER trg_hMenu_UpdatedAt
ON hMenu
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE hMenu 
    SET UpdatedAt = GETDATE()
    FROM hMenu m
    INNER JOIN inserted i ON m.Id = i.Id;
END;

-- 用户表触发器
GO
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

-- 角色菜单关联表触发器
GO
CREATE TRIGGER trg_hRoleMenu_UpdatedAt
ON hRoleMenu
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE hRoleMenu 
    SET UpdatedAt = GETDATE()
    FROM hRoleMenu rm
    INNER JOIN inserted i ON rm.Id = i.Id;
END;

-- 邮件配置表触发器
GO
CREATE TRIGGER trg_hEmailConfigs_UpdatedAt
ON hEmailConfigs
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE hEmailConfigs 
    SET UpdatedAt = GETDATE()
    FROM hEmailConfigs ec
    INNER JOIN inserted i ON ec.Id = i.Id;
END;

GO

-- =====================================================
-- 初始化数据插入
-- =====================================================

-- 插入默认部门
INSERT INTO hDepartments (Id, DepartmentName, Status, CreatedAt, UpdatedAt) VALUES 
(NEWID(), '生产部', '1', GETDATE(), GETDATE()),
(NEWID(), '财务部', '1', GETDATE(), GETDATE()),
(NEWID(), '销售部', '1', GETDATE(), GETDATE());

-- 插入默认角色
INSERT INTO hRoles (Id, RoleName, RoleCode, Description, Status, CreatedAt, UpdatedAt) VALUES 
(NEWID(), '超级管理员', 'SUPER_ADMIN', '系统超级管理员，拥有所有权限', '1', GETDATE(), GETDATE()),
(NEWID(), '管理员', 'ADMIN', '系统管理员，拥有大部分权限', '1', GETDATE(), GETDATE()),
(NEWID(), '普通用户', 'USER', '普通用户，拥有基础权限', '1', GETDATE(), GETDATE());

-- 插入示例菜单数据
INSERT INTO hMenu (MenuId, ParentId, Path, Component, Redirect, Name, Title, Icon, Hidden, AlwaysShow, NoCache, Breadcrumb, Affix, ActiveMenu, NoTagsView, CanTo, Permission, ExternalLink, MenuOrder, CreatedAt, UpdatedAt) VALUES 
-- 根菜单 - 仪表盘
(1000, NULL, '/dashboard', '#', '/dashboard/analysis', 'Dashboard', 'router.dashboard', 'vi-ant-design:dashboard-filled', 0, 1, 0, 1, 0, NULL, 0, 1, NULL, NULL, 1, GETDATE(), GETDATE()),
-- 仪表盘子菜单
(1001, 1000, 'analysis', 'views/Dashboard/Analysis', NULL, 'Analysis', 'router.analysis', NULL, 0, 0, 1, 1, 1, NULL, 0, 1, NULL, NULL, 1, GETDATE(), GETDATE()),
(1002, 1000, 'workplace', 'views/Dashboard/Workplace', NULL, 'Workplace', 'router.workplace', NULL, 0, 0, 1, 1, 1, NULL, 0, 1, NULL, NULL, 2, GETDATE(), GETDATE()),

-- 根菜单 - 外部链接
(2000, NULL, '/external-link', '#', NULL, 'ExternalLink', NULL, NULL, 0, 0, 0, 1, 0, NULL, 0, 1, NULL, NULL, 2, GETDATE(), GETDATE()),
(2001, 2000, 'https://element-plus-admin-doc.cn/', NULL, NULL, 'DocumentLink', 'router.document', 'vi-clarity:document-solid', 0, 0, 0, 1, 0, NULL, 0, 1, NULL, NULL, 1, GETDATE(), GETDATE()),

-- 根菜单 - 组件示例
(3000, NULL, '/components', '#', '/components/form/default-form', 'ComponentsDemo', 'router.component', 'vi-bx:bxs-component', 0, 1, 0, 1, 0, NULL, 0, 1, NULL, NULL, 3, GETDATE(), GETDATE()),
-- 表单组件
(3100, 3000, 'form', '##', NULL, 'Form', 'router.form', NULL, 0, 1, 0, 1, 0, NULL, 0, 1, NULL, NULL, 1, GETDATE(), GETDATE()),
(3101, 3100, 'default-form', 'views/Components/Form/DefaultForm', NULL, 'DefaultForm', 'router.defaultForm', NULL, 0, 0, 0, 1, 0, NULL, 0, 1, NULL, NULL, 1, GETDATE(), GETDATE()),
(3102, 3100, 'use-form', 'views/Components/Form/UseFormDemo', NULL, 'UseForm', 'UseForm', NULL, 0, 0, 0, 1, 0, NULL, 0, 1, NULL, NULL, 2, GETDATE(), GETDATE()),

-- 根菜单 - 权限管理
(4000, NULL, '/authorization', '#', '/authorization/user', 'Authorization', 'router.authorization', 'vi-eos-icons:role-binding', 0, 1, 0, 1, 0, NULL, 0, 1, NULL, NULL, 4, GETDATE(), GETDATE()),
(4001, 4000, 'department', 'views/Authorization/Department/Department', NULL, 'Department', 'router.department', NULL, 0, 0, 0, 1, 0, NULL, 0, 1, '["department:view"]', NULL, 1, GETDATE(), GETDATE()),
(4002, 4000, 'user', 'views/Authorization/User/User', NULL, 'User', 'router.user', NULL, 0, 0, 0, 1, 0, NULL, 0, 1, '["user:view"]', NULL, 2, GETDATE(), GETDATE()),
(4003, 4000, 'role', 'views/Authorization/Role/Role', NULL, 'Role', 'router.role', NULL, 0, 0, 0, 1, 0, NULL, 0, 1, '["role:view"]', NULL, 3, GETDATE(), GETDATE()),
(4004, 4000, 'menu', 'views/Authorization/Menu/Menu', NULL, 'Menu', 'router.menuManagement', NULL, 0, 0, 0, 1, 0, NULL, 0, 1, '["menu:view"]', NULL, 4, GETDATE(), GETDATE());

-- 插入角色菜单关联数据（为演示目的）
-- 获取超级管理员角色ID
DECLARE @SuperAdminRoleId UNIQUEIDENTIFIER = (SELECT Id FROM hRoles WHERE RoleCode = 'SUPER_ADMIN');
DECLARE @AdminRoleId UNIQUEIDENTIFIER = (SELECT Id FROM hRoles WHERE RoleCode = 'ADMIN');
DECLARE @UserRoleId UNIQUEIDENTIFIER = (SELECT Id FROM hRoles WHERE RoleCode = 'USER');

-- 超级管理员拥有所有菜单
INSERT INTO hRoleMenu (RoleId, MenuId, IsEnabled, CreatedAt, UpdatedAt) VALUES 
(@SuperAdminRoleId, 1000, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 1001, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 1002, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 2000, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 2001, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 3000, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 3100, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 3101, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 3102, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 4000, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 4001, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 4002, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 4003, 1, GETDATE(), GETDATE()),
(@SuperAdminRoleId, 4004, 1, GETDATE(), GETDATE());

-- 管理员拥有除权限管理外的菜单
INSERT INTO hRoleMenu (RoleId, MenuId, IsEnabled, CreatedAt, UpdatedAt) VALUES 
(@AdminRoleId, 1000, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 1001, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 1002, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 2000, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 2001, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 3000, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 3100, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 3101, 1, GETDATE(), GETDATE()),
(@AdminRoleId, 3102, 1, GETDATE(), GETDATE());

-- 普通用户只拥有仪表盘和外部链接菜单
INSERT INTO hRoleMenu (RoleId, MenuId, IsEnabled, CreatedAt, UpdatedAt) VALUES 
(@UserRoleId, 1000, 1, GETDATE(), GETDATE()),
(@UserRoleId, 1001, 1, GETDATE(), GETDATE()),
(@UserRoleId, 1002, 1, GETDATE(), GETDATE()),
(@UserRoleId, 2000, 1, GETDATE(), GETDATE()),
(@UserRoleId, 2001, 1, GETDATE(), GETDATE());

-- =====================================================
-- 添加注释说明
-- =====================================================

-- 为表添加描述注释
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'部门表，用于管理组织架构', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hDepartments';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'角色表，用于管理用户角色和权限', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hRoles';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'菜单表，用于管理系统菜单和路由', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hMenu';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'用户表，存储系统用户信息', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hUsers';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'角色菜单关联表，实现角色和菜单的多对多关系', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hRoleMenu';

EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'邮件配置表，存储用户邮件服务器配置', 
    @level0type = N'SCHEMA', @level0name = N'dbo', 
    @level1type = N'TABLE', @level1name = N'hEmailConfigs';

-- =====================================================
-- 脚本执行完成提示
-- =====================================================

PRINT '数据库表创建完成！';
PRINT '已创建以下表:';
PRINT '- hDepartments (部门表)';
PRINT '- hRoles (角色表)';
PRINT '- hMenu (菜单表)';
PRINT '- hUsers (用户表)';
PRINT '- hRoleMenu (角色菜单关联表)';
PRINT '- hEmailConfigs (邮件配置表)';
PRINT '';
PRINT '已创建 UpdatedAt 自动更新触发器:';
PRINT '- trg_hDepartments_UpdatedAt';
PRINT '- trg_hRoles_UpdatedAt';
PRINT '- trg_hMenu_UpdatedAt';
PRINT '- trg_hUsers_UpdatedAt';
PRINT '- trg_hRoleMenu_UpdatedAt';
PRINT '- trg_hEmailConfigs_UpdatedAt';
PRINT '';
PRINT '已插入初始化数据:';
PRINT '- 默认部门';
PRINT '- 默认角色';
PRINT '- 默认菜单';
PRINT '';
PRINT '请根据实际需求创建管理员用户！'; 