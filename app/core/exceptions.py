from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

from app.core.logger import get_logger
from app.core.response import response_manager
from app.schemas.response import BusinessCode
from app.exceptions.base import (
    BaseException, 
    ValidationError, 
    NotFoundError, 
    DatabaseError,
    AuthenticationError,
    AuthorizationError
)

logger = get_logger("exception_handler")

def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理HTTP异常"""
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        
        # 根据HTTP状态码映射业务状态码
        code_mapping = {
            400: BusinessCode.BAD_REQUEST,
            401: BusinessCode.UNAUTHORIZED,
            403: BusinessCode.FORBIDDEN,
            404: BusinessCode.NOT_FOUND,
            409: BusinessCode.CONFLICT,
            422: BusinessCode.VALIDATION_ERROR,
            500: BusinessCode.INTERNAL_ERROR
        }
        
        business_code = code_mapping.get(exc.status_code, BusinessCode.INTERNAL_ERROR)
        
        return response_manager.error(
            message=str(exc.detail),
            code=business_code,
            http_status=exc.status_code
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """处理Starlette HTTP异常"""
        logger.warning(f"Starlette HTTP异常: {exc.status_code} - {exc.detail}")
        
        code_mapping = {
            400: BusinessCode.BAD_REQUEST,
            401: BusinessCode.UNAUTHORIZED,
            403: BusinessCode.FORBIDDEN,
            404: BusinessCode.NOT_FOUND,
            500: BusinessCode.INTERNAL_ERROR
        }
        
        business_code = code_mapping.get(exc.status_code, BusinessCode.INTERNAL_ERROR)
        
        return response_manager.error(
            message=str(exc.detail),
            code=business_code,
            http_status=exc.status_code
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """处理请求参数验证异常"""
        logger.warning(f"请求参数验证失败: {exc.errors()}")
        
        # 提取验证错误信息
        error_messages = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        
        error_message = "; ".join(error_messages)
        
        return response_manager.error(
            message=f"请求参数验证失败: {error_message}",
            code=BusinessCode.VALIDATION_ERROR,
            http_status=422
        )
    
    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
        """处理响应验证异常"""
        logger.error(f"响应验证失败: {exc.errors()}")
        
        return response_manager.error(
            message="服务器内部错误",
            code=BusinessCode.INTERNAL_ERROR,
            http_status=500
        )
    
    @app.exception_handler(ValidationError)
    async def custom_validation_exception_handler(request: Request, exc: ValidationError):
        """处理自定义验证异常"""
        logger.warning(f"业务验证失败: {exc.message}")
        
        return response_manager.error(
            message=exc.message,
            code=BusinessCode.VALIDATION_ERROR,
            http_status=422
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError):
        """处理资源不存在异常"""
        logger.warning(f"资源不存在: {exc.message}")
        
        return response_manager.error(
            message=exc.message,
            code=BusinessCode.NOT_FOUND,
            http_status=404
        )
    
    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        """处理认证异常"""
        logger.warning(f"认证失败: {exc.message}")
        
        return response_manager.error(
            message=exc.message,
            code=BusinessCode.UNAUTHORIZED,
            http_status=401
        )
    
    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, exc: AuthorizationError):
        """处理授权异常"""
        logger.warning(f"授权失败: {exc.message}")
        
        return response_manager.error(
            message=exc.message,
            code=BusinessCode.FORBIDDEN,
            http_status=403
        )
    
    @app.exception_handler(DatabaseError)
    async def database_exception_handler(request: Request, exc: DatabaseError):
        """处理数据库异常"""
        logger.error(f"数据库错误: {exc.message}")
        
        return response_manager.error(
            message="数据库操作失败",
            code=BusinessCode.DATABASE_ERROR,
            http_status=500
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """处理SQLAlchemy异常"""
        logger.error(f"SQLAlchemy错误: {str(exc)}")
        
        return response_manager.error(
            message="数据库操作失败",
            code=BusinessCode.DATABASE_ERROR,
            http_status=500
        )
    
    @app.exception_handler(BaseException)
    async def custom_base_exception_handler(request: Request, exc: BaseException):
        """处理自定义基础异常"""
        logger.error(f"自定义异常: {exc.message}")
        
        return response_manager.error(
            message=exc.message,
            code=BusinessCode.INTERNAL_ERROR,
            http_status=500
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理所有未捕获的异常"""
        logger.error(f"未知异常: {str(exc)}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        
        return response_manager.error(
            message="服务器内部错误",
            code=BusinessCode.INTERNAL_ERROR,
            http_status=500
        ) 