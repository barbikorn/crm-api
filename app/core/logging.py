import logging
import traceback
import uuid
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, Any, Callable
from fastapi import Request
from sqlalchemy.orm import Session

from app.crud.log import create_system_log, create_audit_log, create_api_log
from app.schemas.log import SystemLogCreate, AuditLogCreate, APILogCreate
from app.models.log import LogLevel, LogCategory

# Configure Python logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LoggingService:
    """Professional logging service for the CRM system"""
    
    @staticmethod
    def log_system_event(
        db: Session,
        level: LogLevel,
        category: LogCategory,
        message: str,
        module: Optional[str] = None,
        function_name: Optional[str] = None,
        line_number: Optional[int] = None,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
        duration_ms: Optional[int] = None,
        request: Optional[Request] = None
    ):
        """Log a system event"""
        try:
            # Extract request information if available
            ip_address = None
            user_agent = None
            endpoint = None
            method = None
            
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                endpoint = str(request.url.path)
                method = request.method
            
            log_entry = SystemLogCreate(
                level=level,
                category=category,
                message=message,
                module=module,
                function_name=function_name,
                line_number=line_number,
                request_id=request_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                method=method,
                extra_data=extra_data,
                stack_trace=stack_trace,
                duration_ms=duration_ms
            )
            
            return create_system_log(db, log_entry)
        except Exception as e:
            logger.error(f"Failed to create system log: {str(e)}")
            return None
    
    @staticmethod
    def log_audit_event(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log an audit event"""
        try:
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
            
            audit_entry = AuditLogCreate(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return create_audit_log(db, audit_entry)
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            return None
    
    @staticmethod
    def log_api_call(
        db: Session,
        request_id: str,
        method: str,
        endpoint: str,
        status_code: int,
        response_time_ms: int,
        user_id: Optional[int] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
        query_params: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log an API call"""
        try:
            ip_address = None
            user_agent = None
            request_headers = None
            
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
                # Only log safe headers
                safe_headers = ["content-type", "accept", "authorization"]
                request_headers = {
                    k: v for k, v in request.headers.items() 
                    if k.lower() in safe_headers
                }
                # Mask authorization header
                if "authorization" in request_headers:
                    request_headers["authorization"] = "***MASKED***"
            
            api_entry = APILogCreate(
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_time_ms=response_time_ms,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_size=request_size,
                response_size=response_size,
                query_params=query_params,
                request_headers=request_headers,
                error_message=error_message,
                stack_trace=stack_trace
            )
            
            return create_api_log(db, api_entry)
        except Exception as e:
            logger.error(f"Failed to create API log: {str(e)}")
            return None

def log_function_call(
    category: LogCategory = LogCategory.BUSINESS_LOGIC,
    log_args: bool = False,
    log_result: bool = False
):
    """Decorator to automatically log function calls"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            request_id = str(uuid.uuid4())
            
            # Extract db session if available
            db = None
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break
            
            if not db:
                for value in kwargs.values():
                    if isinstance(value, Session):
                        db = value
                        break
            
            try:
                # Log function start
                extra_data = {}
                if log_args:
                    extra_data["args"] = str(args)
                    extra_data["kwargs"] = str(kwargs)
                
                if db:
                    LoggingService.log_system_event(
                        db=db,
                        level=LogLevel.INFO,
                        category=category,
                        message=f"Function {func.__name__} started",
                        module=func.__module__,
                        function_name=func.__name__,
                        request_id=request_id,
                        extra_data=extra_data if extra_data else None
                    )
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                end_time = datetime.utcnow()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Log function completion
                extra_data = {}
                if log_result:
                    extra_data["result"] = str(result)
                
                if db:
                    LoggingService.log_system_event(
                        db=db,
                        level=LogLevel.INFO,
                        category=category,
                        message=f"Function {func.__name__} completed successfully",
                        module=func.__module__,
                        function_name=func.__name__,
                        request_id=request_id,
                        duration_ms=duration_ms,
                        extra_data=extra_data if extra_data else None
                    )
                
                return result
                
            except Exception as e:
                # Calculate execution time for failed calls
                end_time = datetime.utcnow()
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Log function error
                if db:
                    LoggingService.log_system_event(
                        db=db,
                        level=LogLevel.ERROR,
                        category=category,
                        message=f"Function {func.__name__} failed: {str(e)}",
                        module=func.__module__,
                        function_name=func.__name__,
                        request_id=request_id,
                        duration_ms=duration_ms,
                        stack_trace=traceback.format_exc()
                    )
                
                raise
        
        return wrapper
    return decorator

def log_audit_action(action: str, resource_type: str):
    """Decorator to automatically log audit actions"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract parameters
            db = None
            user_id = None
            resource_id = None
            old_values = None
            
            # Try to extract from args/kwargs
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break
            
            if not db:
                for value in kwargs.values():
                    if isinstance(value, Session):
                        db = value
                        break
            
            # Look for user_id in kwargs
            user_id = kwargs.get('user_id') or kwargs.get('current_user_id')
            
            try:
                # Store old values for update operations
                if action.lower() in ['update', 'delete'] and 'id' in kwargs:
                    # This would need to be customized based on your models
                    pass
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Get new values for create/update operations
                new_values = None
                if hasattr(result, '__dict__'):
                    new_values = {k: v for k, v in result.__dict__.items() 
                                if not k.startswith('_')}
                
                # Log audit event
                if db and user_id:
                    LoggingService.log_audit_event(
                        db=db,
                        user_id=user_id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=str(getattr(result, 'id', None)) if result else None,
                        old_values=old_values,
                        new_values=new_values
                    )
                
                return result
                
            except Exception as e:
                # Log failed audit action
                if db and user_id:
                    LoggingService.log_system_event(
                        db=db,
                        level=LogLevel.ERROR,
                        category=LogCategory.SECURITY,
                        message=f"Audit action {action} on {resource_type} failed: {str(e)}",
                        user_id=user_id,
                        stack_trace=traceback.format_exc()
                    )
                raise
        
        return wrapper
    return decorator 