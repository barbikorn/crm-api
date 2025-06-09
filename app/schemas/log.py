from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.log import LogLevel, LogCategory

# Base schemas
class SystemLogBase(BaseModel):
    level: LogLevel
    category: LogCategory
    message: str = Field(..., min_length=1, max_length=5000)
    module: Optional[str] = Field(None, max_length=100)
    function_name: Optional[str] = Field(None, max_length=100)
    line_number: Optional[int] = Field(None, ge=0)
    request_id: Optional[str] = Field(None, max_length=100)
    user_id: Optional[int] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    endpoint: Optional[str] = Field(None, max_length=200)
    method: Optional[str] = Field(None, max_length=10)
    extra_data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    duration_ms: Optional[int] = Field(None, ge=0)

class SystemLogCreate(SystemLogBase):
    pass

class SystemLogUpdate(BaseModel):
    level: Optional[LogLevel] = None
    category: Optional[LogCategory] = None
    message: Optional[str] = Field(None, min_length=1, max_length=5000)
    extra_data: Optional[Dict[str, Any]] = None

class SystemLogOut(SystemLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Audit Log schemas
class AuditLogBase(BaseModel):
    user_id: int
    action: str = Field(..., min_length=1, max_length=100)
    resource_type: str = Field(..., min_length=1, max_length=50)
    resource_id: Optional[str] = Field(None, max_length=50)
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogOut(AuditLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# API Log schemas
class APILogBase(BaseModel):
    request_id: str = Field(..., min_length=1, max_length=100)
    method: str = Field(..., min_length=1, max_length=10)
    endpoint: str = Field(..., min_length=1, max_length=200)
    status_code: int = Field(..., ge=100, le=599)
    response_time_ms: int = Field(..., ge=0)
    user_id: Optional[int] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    request_size: Optional[int] = Field(None, ge=0)
    response_size: Optional[int] = Field(None, ge=0)
    query_params: Optional[Dict[str, Any]] = None
    request_headers: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

class APILogCreate(APILogBase):
    pass

class APILogOut(APILogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Log query schemas
class LogFilter(BaseModel):
    level: Optional[LogLevel] = None
    category: Optional[LogCategory] = None
    user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    module: Optional[str] = None
    endpoint: Optional[str] = None
    search_text: Optional[str] = Field(None, max_length=500)

class LogStatsFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    group_by: Optional[str] = Field("hour", pattern="^(hour|day|week|month)$")

class LogStats(BaseModel):
    total_logs: int
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int
    critical_count: int
    avg_response_time_ms: Optional[float] = None
    total_api_calls: int
    error_rate_percentage: float

class LogAnalytics(BaseModel):
    time_period: str
    log_count: int
    error_count: int
    timestamp: datetime

# Response schemas
class LogListResponse(BaseModel):
    logs: List[SystemLogOut]
    total: int
    page: int
    size: int
    total_pages: int

class APILogListResponse(BaseModel):
    logs: List[APILogOut]
    total: int
    page: int
    size: int
    total_pages: int

class AuditLogListResponse(BaseModel):
    logs: List[AuditLogOut]
    total: int
    page: int
    size: int
    total_pages: int 