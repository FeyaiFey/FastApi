from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any, Optional
from app.schemas.response import ResponseHandler

class CustomException(Exception):
    """自定义异常基类"""
    def __init__(
        self,
        message: str,
        code: int = status.HTTP_400_BAD_REQUEST,
        data: Any = None
    ):
        self.message = message
        self.code = code
        self.data = data

class DatabaseException(CustomException):
    """数据库操作异常"""
    def __init__(self, message: str = "数据库操作失败", data: Any = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, data)

class AuthenticationException(CustomException):
    """认证相关异常"""
    def __init__(self, message: str = "认证失败", data: Any = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, data)

class ValidationException(CustomException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败", data: Any = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, data)

class BusinessException(CustomException):
    """业务逻辑异常"""
    def __init__(self, message: str = "业务处理失败", data: Any = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, data)

class UnauthorizedException(CustomException):
    """未授权异常"""
    def __init__(self, message: str = "未经授权"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class ForbiddenException(CustomException):
    """禁止访问异常"""
    def __init__(self, message: str = "禁止访问"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class NotFoundException(CustomException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class BadRequestException(CustomException):
    """请求参数错误异常"""
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

async def custom_exception_handler(request: Request, exc: CustomException):
    """自定义异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseHandler.error(
            code=exc.code,
            message=exc.message,
            data=exc.data
        ).model_dump()
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求参数验证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseHandler.error(
            code=status.HTTP_400_BAD_REQUEST,
            message=str(exc.errors())
        ).model_dump()
    )

async def internal_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ResponseHandler.error(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(exc)
        ).model_dump()
    ) 