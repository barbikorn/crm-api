from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class LogLevel(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(enum.Enum):
    API = "API"
    DATABASE = "DATABASE"
    AUTHENTICATION = "AUTHENTICATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    SYSTEM = "SYSTEM"
    SECURITY = "SECURITY"
    USER_ACTION = "USER_ACTION"
    # Chat-specific categories
    CHAT_MESSAGE = "CHAT_MESSAGE"
    CHAT_EVENT = "CHAT_EVENT"
    CHAT_MODERATION = "CHAT_MODERATION"

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(LogLevel), nullable=False, index=True)
    category = Column(Enum(LogCategory), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True, index=True)
    function_name = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    
    # Request context
    request_id = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(200), nullable=True)
    method = Column(String(10), nullable=True)
    
    # Additional data
    extra_data = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="system_logs")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(50), nullable=True, index=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class APILog(Base):
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(200), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=False)
    
    # User context
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Request/Response data
    request_size = Column(Integer, nullable=True)
    response_size = Column(Integer, nullable=True)
    query_params = Column(JSON, nullable=True)
    request_headers = Column(JSON, nullable=True)
    
    # Error info
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="api_logs") 