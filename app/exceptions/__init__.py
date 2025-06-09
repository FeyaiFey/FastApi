"""
异常处理模块

提供统一的异常类定义和异常处理器注册
"""

from fastapi import FastAPI
from app.core.exceptions import register_exception_handlers as _register_handlers

# 导入异常类，供其他模块使用
from app.exceptions.base import (
    BaseAPIException,
    ValidationError,
    AuthenticationError, 
    AuthorizationError,
    PermissionError,
    NotFoundError,
    DatabaseError,
    BaseException  # 向后兼容别名
)

def register_exception_handlers(app: FastAPI) -> None:
    """注册异常处理器"""
    _register_handlers(app)

__all__ = [
    "register_exception_handlers",
    "BaseAPIException", 
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError", 
    "PermissionError",
    "NotFoundError",
    "DatabaseError",
    "BaseException"
] 