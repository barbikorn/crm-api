from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import math

from app.models.log import SystemLog, AuditLog, APILog, LogLevel, LogCategory
from app.schemas.log import (
    SystemLogCreate, SystemLogUpdate, AuditLogCreate, APILogCreate,
    LogFilter, LogStatsFilter, LogStats, LogAnalytics
)

# System Log CRUD
def create_system_log(db: Session, log: SystemLogCreate) -> SystemLog:
    """Create a new system log entry"""
    db_log = SystemLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_system_log(db: Session, log_id: int) -> Optional[SystemLog]:
    """Get a system log by ID"""
    return db.query(SystemLog).filter(SystemLog.id == log_id).first()

def get_system_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    filters: Optional[LogFilter] = None
) -> tuple[List[SystemLog], int]:
    """Get system logs with filtering and pagination"""
    query = db.query(SystemLog)
    
    if filters:
        if filters.level:
            query = query.filter(SystemLog.level == filters.level)
        if filters.category:
            query = query.filter(SystemLog.category == filters.category)
        if filters.user_id:
            query = query.filter(SystemLog.user_id == filters.user_id)
        if filters.start_date:
            query = query.filter(SystemLog.timestamp >= filters.start_date)
        if filters.end_date:
            query = query.filter(SystemLog.timestamp <= filters.end_date)
        if filters.module:
            query = query.filter(SystemLog.module.ilike(f"%{filters.module}%"))
        if filters.endpoint:
            query = query.filter(SystemLog.endpoint.ilike(f"%{filters.endpoint}%"))
        if filters.search_text:
            query = query.filter(
                or_(
                    SystemLog.message.ilike(f"%{filters.search_text}%"),
                    SystemLog.module.ilike(f"%{filters.search_text}%"),
                    SystemLog.function_name.ilike(f"%{filters.search_text}%")
                )
            )
    
    total = query.count()
    logs = query.order_by(desc(SystemLog.timestamp)).offset(skip).limit(limit).all()
    return logs, total

def update_system_log(db: Session, log_id: int, log_update: SystemLogUpdate) -> Optional[SystemLog]:
    """Update a system log"""
    db_log = db.query(SystemLog).filter(SystemLog.id == log_id).first()
    if db_log:
        update_data = log_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_log, field, value)
        db.commit()
        db.refresh(db_log)
    return db_log

def delete_system_log(db: Session, log_id: int) -> Optional[SystemLog]:
    """Delete a system log"""
    db_log = db.query(SystemLog).filter(SystemLog.id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
    return db_log

# Audit Log CRUD
def create_audit_log(db: Session, log: AuditLogCreate) -> AuditLog:
    """Create a new audit log entry"""
    db_log = AuditLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_audit_log(db: Session, log_id: int) -> Optional[AuditLog]:
    """Get an audit log by ID"""
    return db.query(AuditLog).filter(AuditLog.id == log_id).first()

def get_audit_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> tuple[List[AuditLog], int]:
    """Get audit logs with filtering and pagination"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    total = query.count()
    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    return logs, total

# API Log CRUD
def create_api_log(db: Session, log: APILogCreate) -> APILog:
    """Create a new API log entry"""
    db_log = APILog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_api_log(db: Session, log_id: int) -> Optional[APILog]:
    """Get an API log by ID"""
    return db.query(APILog).filter(APILog.id == log_id).first()

def get_api_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> tuple[List[APILog], int]:
    """Get API logs with filtering and pagination"""
    query = db.query(APILog)
    
    if endpoint:
        query = query.filter(APILog.endpoint.ilike(f"%{endpoint}%"))
    if method:
        query = query.filter(APILog.method == method)
    if status_code:
        query = query.filter(APILog.status_code == status_code)
    if user_id:
        query = query.filter(APILog.user_id == user_id)
    if start_date:
        query = query.filter(APILog.timestamp >= start_date)
    if end_date:
        query = query.filter(APILog.timestamp <= end_date)
    
    total = query.count()
    logs = query.order_by(desc(APILog.timestamp)).offset(skip).limit(limit).all()
    return logs, total

# Analytics and Statistics
def get_log_statistics(db: Session, filters: Optional[LogStatsFilter] = None) -> LogStats:
    """Get comprehensive log statistics"""
    query = db.query(SystemLog)
    api_query = db.query(APILog)
    
    if filters:
        if filters.start_date:
            query = query.filter(SystemLog.timestamp >= filters.start_date)
            api_query = api_query.filter(APILog.timestamp >= filters.start_date)
        if filters.end_date:
            query = query.filter(SystemLog.timestamp <= filters.end_date)
            api_query = api_query.filter(APILog.timestamp <= filters.end_date)
    
    # System log stats
    total_logs = query.count()
    error_count = query.filter(SystemLog.level == LogLevel.ERROR).count()
    warning_count = query.filter(SystemLog.level == LogLevel.WARNING).count()
    info_count = query.filter(SystemLog.level == LogLevel.INFO).count()
    debug_count = query.filter(SystemLog.level == LogLevel.DEBUG).count()
    critical_count = query.filter(SystemLog.level == LogLevel.CRITICAL).count()
    
    # API log stats
    total_api_calls = api_query.count()
    avg_response_time = db.query(func.avg(APILog.response_time_ms)).filter(
        APILog.timestamp >= (filters.start_date if filters and filters.start_date else datetime.utcnow() - timedelta(days=30))
    ).scalar()
    
    # Error rate calculation
    error_rate = (error_count + critical_count) / total_logs * 100 if total_logs > 0 else 0
    
    return LogStats(
        total_logs=total_logs,
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        debug_count=debug_count,
        critical_count=critical_count,
        avg_response_time_ms=float(avg_response_time) if avg_response_time else None,
        total_api_calls=total_api_calls,
        error_rate_percentage=round(error_rate, 2)
    )

def get_log_analytics(
    db: Session, 
    filters: Optional[LogStatsFilter] = None
) -> List[LogAnalytics]:
    """Get log analytics grouped by time periods"""
    if not filters:
        filters = LogStatsFilter()
    
    # Default to last 24 hours if no dates provided
    end_date = filters.end_date or datetime.utcnow()
    start_date = filters.start_date or (end_date - timedelta(days=1))
    
    # Group by time period
    if filters.group_by == "hour":
        time_format = "%Y-%m-%d %H:00:00"
        interval = timedelta(hours=1)
    elif filters.group_by == "day":
        time_format = "%Y-%m-%d"
        interval = timedelta(days=1)
    elif filters.group_by == "week":
        time_format = "%Y-%U"
        interval = timedelta(weeks=1)
    else:  # month
        time_format = "%Y-%m"
        interval = timedelta(days=30)
    
    # Query grouped data
    results = db.query(
        func.date_trunc(filters.group_by, SystemLog.timestamp).label('time_period'),
        func.count(SystemLog.id).label('log_count'),
        func.count(func.nullif(SystemLog.level.in_([LogLevel.ERROR, LogLevel.CRITICAL]), False)).label('error_count')
    ).filter(
        SystemLog.timestamp >= start_date,
        SystemLog.timestamp <= end_date
    ).group_by(
        func.date_trunc(filters.group_by, SystemLog.timestamp)
    ).order_by(
        func.date_trunc(filters.group_by, SystemLog.timestamp)
    ).all()
    
    analytics = []
    for result in results:
        analytics.append(LogAnalytics(
            time_period=result.time_period.strftime(time_format),
            log_count=result.log_count,
            error_count=result.error_count or 0,
            timestamp=result.time_period
        ))
    
    return analytics

# Utility functions
def delete_old_logs(db: Session, days_to_keep: int = 30) -> Dict[str, int]:
    """Delete logs older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    # Delete old system logs
    system_deleted = db.query(SystemLog).filter(SystemLog.timestamp < cutoff_date).count()
    db.query(SystemLog).filter(SystemLog.timestamp < cutoff_date).delete()
    
    # Delete old audit logs
    audit_deleted = db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).count()
    db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).delete()
    
    # Delete old API logs
    api_deleted = db.query(APILog).filter(APILog.timestamp < cutoff_date).count()
    db.query(APILog).filter(APILog.timestamp < cutoff_date).delete()
    
    db.commit()
    
    return {
        "system_logs_deleted": system_deleted,
        "audit_logs_deleted": audit_deleted,
        "api_logs_deleted": api_deleted,
        "total_deleted": system_deleted + audit_deleted + api_deleted
    } 