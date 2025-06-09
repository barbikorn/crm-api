from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import math

from app.schemas.log import (
    SystemLogCreate, SystemLogUpdate, SystemLogOut, 
    AuditLogCreate, AuditLogOut,
    APILogCreate, APILogOut,
    LogFilter, LogStatsFilter, LogStats, LogAnalytics,
    LogListResponse, APILogListResponse, AuditLogListResponse
)
from app.crud import log as crud_log
from app.api import deps
from app.models.log import LogLevel, LogCategory

router = APIRouter()

# System Logs Endpoints
@router.post("/logs/system", response_model=SystemLogOut)
def create_system_log(
    log: SystemLogCreate,
    db: Session = Depends(deps.get_db)
):
    """Create a new system log entry"""
    return crud_log.create_system_log(db, log)

@router.get("/logs/system/{log_id}", response_model=SystemLogOut)
def get_system_log(
    log_id: int,
    db: Session = Depends(deps.get_db)
):
    """Get a specific system log by ID"""
    log = crud_log.get_system_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.get("/logs/system", response_model=LogListResponse)
def get_system_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    level: Optional[LogLevel] = Query(None, description="Filter by log level"),
    category: Optional[LogCategory] = Query(None, description="Filter by category"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    module: Optional[str] = Query(None, description="Filter by module name"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    search_text: Optional[str] = Query(None, description="Search in message, module, and function"),
    db: Session = Depends(deps.get_db)
):
    """Get system logs with advanced filtering and pagination"""
    skip = (page - 1) * size
    
    filters = LogFilter(
        level=level,
        category=category,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        module=module,
        endpoint=endpoint,
        search_text=search_text
    )
    
    logs, total = crud_log.get_system_logs(db, skip=skip, limit=size, filters=filters)
    total_pages = math.ceil(total / size)
    
    return LogListResponse(
        logs=logs,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

@router.put("/logs/system/{log_id}", response_model=SystemLogOut)
def update_system_log(
    log_id: int,
    log_update: SystemLogUpdate,
    db: Session = Depends(deps.get_db)
):
    """Update a system log"""
    updated_log = crud_log.update_system_log(db, log_id, log_update)
    if not updated_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return updated_log

@router.delete("/logs/system/{log_id}", response_model=SystemLogOut)
def delete_system_log(
    log_id: int,
    db: Session = Depends(deps.get_db)
):
    """Delete a system log"""
    deleted_log = crud_log.delete_system_log(db, log_id)
    if not deleted_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return deleted_log

# Audit Logs Endpoints
@router.post("/logs/audit", response_model=AuditLogOut)
def create_audit_log(
    log: AuditLogCreate,
    db: Session = Depends(deps.get_db)
):
    """Create a new audit log entry"""
    return crud_log.create_audit_log(db, log)

@router.get("/logs/audit/{log_id}", response_model=AuditLogOut)
def get_audit_log(
    log_id: int,
    db: Session = Depends(deps.get_db)
):
    """Get a specific audit log by ID"""
    log = crud_log.get_audit_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log

@router.get("/logs/audit", response_model=AuditLogListResponse)
def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    db: Session = Depends(deps.get_db)
):
    """Get audit logs with filtering and pagination"""
    skip = (page - 1) * size
    
    logs, total = crud_log.get_audit_logs(
        db, 
        skip=skip, 
        limit=size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date
    )
    total_pages = math.ceil(total / size)
    
    return AuditLogListResponse(
        logs=logs,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

# API Logs Endpoints
@router.post("/logs/api", response_model=APILogOut)
def create_api_log(
    log: APILogCreate,
    db: Session = Depends(deps.get_db)
):
    """Create a new API log entry"""
    return crud_log.create_api_log(db, log)

@router.get("/logs/api/{log_id}", response_model=APILogOut)
def get_api_log(
    log_id: int,
    db: Session = Depends(deps.get_db)
):
    """Get a specific API log by ID"""
    log = crud_log.get_api_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="API log not found")
    return log

@router.get("/logs/api", response_model=APILogListResponse)
def get_api_logs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    db: Session = Depends(deps.get_db)
):
    """Get API logs with filtering and pagination"""
    skip = (page - 1) * size
    
    logs, total = crud_log.get_api_logs(
        db,
        skip=skip,
        limit=size,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    total_pages = math.ceil(total / size)
    
    return APILogListResponse(
        logs=logs,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

# Analytics and Statistics Endpoints
@router.get("/logs/statistics", response_model=LogStats)
def get_log_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    db: Session = Depends(deps.get_db)
):
    """Get comprehensive log statistics"""
    filters = LogStatsFilter(start_date=start_date, end_date=end_date)
    return crud_log.get_log_statistics(db, filters)

@router.get("/logs/analytics", response_model=List[LogAnalytics])
def get_log_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    group_by: str = Query("hour", pattern="^(hour|day|week|month)$", description="Group analytics by time period"),
    db: Session = Depends(deps.get_db)
):
    """Get log analytics grouped by time periods"""
    filters = LogStatsFilter(
        start_date=start_date,
        end_date=end_date,
        group_by=group_by
    )
    return crud_log.get_log_analytics(db, filters)

# Log Management Endpoints
@router.delete("/logs/cleanup")
def cleanup_old_logs(
    days_to_keep: int = Query(30, ge=1, le=365, description="Number of days to keep logs"),
    db: Session = Depends(deps.get_db)
):
    """Delete logs older than specified days"""
    result = crud_log.delete_old_logs(db, days_to_keep)
    return {
        "message": f"Successfully deleted old logs",
        "details": result
    }

# Health Check Endpoints
@router.get("/logs/health")
def logs_health_check(db: Session = Depends(deps.get_db)):
    """Health check for logging system"""
    try:
        # Test database connectivity with a simple query
        recent_logs_count = crud_log.get_system_logs(db, skip=0, limit=1)[1]
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database_connected": True,
            "recent_logs_available": recent_logs_count > 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow(),
                "error": str(e)
            }
        )

# Bulk Operations
@router.post("/logs/system/bulk", response_model=List[SystemLogOut])
def create_bulk_system_logs(
    logs: List[SystemLogCreate],
    db: Session = Depends(deps.get_db)
):
    """Create multiple system logs in bulk"""
    if len(logs) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 logs allowed per bulk operation")
    
    created_logs = []
    for log in logs:
        created_log = crud_log.create_system_log(db, log)
        created_logs.append(created_log)
    
    return created_logs

@router.get("/logs/export")
def export_logs(
    log_type: str = Query(..., pattern="^(system|audit|api)$", description="Type of logs to export"),
    format: str = Query("json", pattern="^(json|csv)$", description="Export format"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    db: Session = Depends(deps.get_db)
):
    """Export logs in specified format"""
    # This is a placeholder for log export functionality
    # In a real implementation, you would generate and return the file
    return {
        "message": f"Export functionality for {log_type} logs in {format} format",
        "note": "This endpoint would generate and return the exported file in a real implementation",
        "filters": {
            "start_date": start_date,
            "end_date": end_date
        }
    } 