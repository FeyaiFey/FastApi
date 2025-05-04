from typing import Any, Dict, Optional
from fastapi import status

class BaseAPIException(Exception):
    """基础API异常类"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "服务器内部错误",
        data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.data = data
        self.headers = headers
        super().__init__(message)

class ValidationError(BaseAPIException):
    """数据验证错误"""
    def __init__(
        self,
        message: str = "数据验证错误",
        data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            data=data,
            headers=headers
        )

class AuthenticationError(BaseAPIException):
    """认证错误"""
    def __init__(
        self,
        message: str = "认证失败",
        data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            data=data,
            headers=headers
        )

class PermissionError(BaseAPIException):
    """权限错误"""
    def __init__(
        self,
        message: str = "权限不足",
        data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            data=data,
            headers=headers
        )

class NotFoundError(BaseAPIException):
    """资源不存在错误"""
    def __init__(
        self,
        message: str = "资源不存在",
        data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            data=data,
            headers=headers
        )

class DatabaseError(BaseAPIException):
    """数据库错误"""
    def __init__(
        self,
        message: str = "数据库操作失败",
        data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            data=data,
            headers=headers
        ) 