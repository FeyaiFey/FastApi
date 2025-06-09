from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import time

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """统一响应基础模型"""
    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    success: bool = Field(..., description="是否成功")
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000), description="时间戳(毫秒)")

class SuccessResponse(BaseResponse[T]):
    """成功响应模型"""
    code: int = Field(default=200, description="业务状态码")
    success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="响应消息")

class ErrorResponse(BaseResponse[None]):
    """错误响应模型"""
    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="错误消息")
    cause: Optional[Any] = Field(default=None, description="错误原因，用于详细错误信息")

class PaginationMeta(BaseModel):
    """分页元数据"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

class PaginationData(BaseModel, Generic[T]):
    """分页数据模型"""
    items: List[T] = Field(..., description="数据列表")
    pagination: PaginationMeta = Field(..., description="分页信息")

class PaginationResponse(SuccessResponse[PaginationData[T]]):
    """分页响应模型"""
    pass

# 业务状态码定义
class BusinessCode:
    """业务状态码枚举"""
    # 成功
    SUCCESS = 0
    CREATED = 0
    
    # 客户端错误
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    VALIDATION_ERROR = 422
    
    # 服务端错误
    INTERNAL_ERROR = 500
    DATABASE_ERROR = 501
    EXTERNAL_SERVICE_ERROR = 502 