-- SQL Server 数据库表创建脚本 (简化版)
-- 基于 FastAPI 项目的 SQLAlchemy 模型生成

-- 1. 部门表
CREATE TABLE hDepartments (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ParentId UNIQUEIDENTIFIER NULL,
    DepartmentName NVARCHAR(50) NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT '1',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_hDepartments_ParentId FOREIGN KEY (ParentId) REFERENCES hDepartments(Id)
);

-- 2. 角色表
CREATE TABLE hRoles (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RoleName NVARCHAR(50) NOT NULL UNIQUE,
    RoleCode NVARCHAR(50) NOT NULL UNIQUE,
    Description NTEXT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT '1',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- 3. 菜单表
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
    Permission NVARCHAR(MAX) NULL,
    ExternalLink NVARCHAR(255) NULL,
    MenuOrder INT NULL DEFAULT 0,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_hMenu_ParentId FOREIGN KEY (ParentId) REFERENCES hMenu(MenuId)
);

-- 4. 用户表
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
    CONSTRAINT FK_hUsers_DepartmentId FOREIGN KEY (DepartmentId) REFERENCES hDepartments(Id),
    CONSTRAINT FK_hUsers_RoleId FOREIGN KEY (RoleId) REFERENCES hRoles(Id),
    CONSTRAINT UQ_hUsers_Email UNIQUE (Email),
    CONSTRAINT UQ_hUsers_UserName UNIQUE (UserName)
);

-- 5. 角色菜单关联表
CREATE TABLE hRoleMenu (
    Id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RoleId UNIQUEIDENTIFIER NOT NULL,
    MenuId INT NOT NULL,
    IsEnabled BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_hRoleMenu_RoleId FOREIGN KEY (RoleId) REFERENCES hRoles(Id),
    CONSTRAINT FK_hRoleMenu_MenuId FOREIGN KEY (MenuId) REFERENCES hMenu(MenuId),
    CONSTRAINT UQ_hRoleMenu_RoleId_MenuId UNIQUE (RoleId, MenuId)
);

-- 6. 邮件配置表
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
    CONSTRAINT FK_hEmailConfigs_UserId FOREIGN KEY (UserId) REFERENCES hUsers(Id)
);

-- 创建索引
CREATE INDEX IX_hDepartments_ParentId ON hDepartments(ParentId);
CREATE INDEX IX_hRoles_RoleName ON hRoles(RoleName);
CREATE INDEX IX_hRoles_RoleCode ON hRoles(RoleCode);
CREATE INDEX IX_hMenu_MenuId ON hMenu(MenuId);
CREATE INDEX IX_hMenu_ParentId ON hMenu(ParentId);
CREATE INDEX IX_hMenu_MenuOrder ON hMenu(MenuOrder);
CREATE INDEX IX_hUsers_Email ON hUsers(Email);
CREATE INDEX IX_hUsers_UserName ON hUsers(UserName);
CREATE INDEX IX_hUsers_DepartmentId ON hUsers(DepartmentId);
CREATE INDEX IX_hUsers_RoleId ON hUsers(RoleId);
CREATE INDEX IX_hRoleMenu_RoleId ON hRoleMenu(RoleId);
CREATE INDEX IX_hRoleMenu_MenuId ON hRoleMenu(MenuId);
CREATE INDEX IX_hRoleMenu_IsEnabled ON hRoleMenu(IsEnabled);
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