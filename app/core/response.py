from typing import Any, List, Optional, TypeVar, Union
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import math

from app.schemas.response import (
    SuccessResponse, 
    ErrorResponse, 
    PaginationResponse, 
    PaginationData, 
    PaginationMeta,
    BusinessCode
)

T = TypeVar('T')

class ResponseManager:
    """响应管理器"""
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "操作成功", 
        code: int = BusinessCode.SUCCESS
    ) -> SuccessResponse:
        """创建成功响应"""
        return SuccessResponse(
            code=code,
            message=message,
            data=data,
            success=True
        )
    
    @staticmethod
    def error(
        message: str, 
        code: int = BusinessCode.INTERNAL_ERROR,
        http_status: int = 500,
        cause: Any = None
    ) -> JSONResponse:
        """创建错误响应"""
        error_response = ErrorResponse(
            code=code,
            message=message,
            success=False,
            cause=cause
        )
        return JSONResponse(
            status_code=http_status,
            content=error_response.model_dump()
        )
    
    @staticmethod
    def created(
        data: Any = None, 
        message: str = "创建成功"
    ) -> SuccessResponse:
        """创建资源成功响应"""
        return ResponseManager.success(
            data=data, 
            message=message, 
            code=BusinessCode.CREATED
        )
    
    @staticmethod
    def not_found(
        message: str = "资源不存在"
    ) -> JSONResponse:
        """资源不存在响应"""
        return ResponseManager.error(
            message=message,
            code=BusinessCode.NOT_FOUND,
            http_status=404
        )
    
    @staticmethod
    def bad_request(
        message: str = "请求参数错误"
    ) -> JSONResponse:
        """请求参数错误响应"""
        return ResponseManager.error(
            message=message,
            code=BusinessCode.BAD_REQUEST,
            http_status=400
        )
    
    @staticmethod
    def unauthorized(
        message: str = "未授权访问"
    ) -> JSONResponse:
        """未授权响应"""
        return ResponseManager.error(
            message=message,
            code=BusinessCode.UNAUTHORIZED,
            http_status=401
        )
    
    @staticmethod
    def forbidden(
        message: str = "访问被禁止"
    ) -> JSONResponse:
        """禁止访问响应"""
        return ResponseManager.error(
            message=message,
            code=BusinessCode.FORBIDDEN,
            http_status=403
        )
    
    @staticmethod
    def validation_error(
        message: str = "数据验证失败"
    ) -> JSONResponse:
        """数据验证错误响应"""
        return ResponseManager.error(
            message=message,
            code=BusinessCode.VALIDATION_ERROR,
            http_status=422
        )
    
    @staticmethod
    def paginated(
        items: List[T],
        total: int,
        page: int = 1,
        page_size: int = 10,
        message: str = "查询成功"
    ) -> PaginationResponse:
        """创建分页响应"""
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        
        pagination_meta = PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
        pagination_data = PaginationData(
            items=items,
            pagination=pagination_meta
        )
        
        return PaginationResponse(
            code=BusinessCode.SUCCESS,
            message=message,
            data=pagination_data,
            success=True
        )

# 创建全局响应管理器实例
response_manager = ResponseManager() 