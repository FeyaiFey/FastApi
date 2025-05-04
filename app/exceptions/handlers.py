import traceback
from typing import Any, Dict, Optional, Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.logger import get_logger
from app.exceptions.base import BaseAPIException

logger = get_logger(name="exceptions")

async def base_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """处理基础API异常"""
    logger.error(
        f"API异常: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "data": exc.data,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.message,
            "data": exc.data
        },
        headers=exc.headers
    )

async def validation_exception_handler(request: Request, exc: Union[RequestValidationError, PydanticValidationError]) -> JSONResponse:
    """处理数据验证异常"""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    logger.error(
        "数据验证错误",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "数据验证错误",
            "data": errors
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """处理数据库异常"""
    logger.error(
        "数据库操作错误",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "数据库操作失败",
            "data": None
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理通用异常"""
    logger.error(
        "未处理的异常",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "服务器内部错误",
            "data": None
        }
    ) 