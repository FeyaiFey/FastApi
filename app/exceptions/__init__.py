from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions.base import BaseAPIException
from app.exceptions.handlers import (
    base_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

def register_exception_handlers(app: FastAPI) -> None:
    """注册异常处理器"""
    
    # 注册基础API异常处理器
    app.add_exception_handler(BaseAPIException, base_exception_handler)
    
    # 注册数据验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)
    
    # 注册数据库异常处理器
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # 注册通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler) 