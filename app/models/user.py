from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role_id = Column(Integer, default=2)
    team_id = Column(Integer, nullable=True)
    
    # Log relationships
    system_logs = relationship("SystemLog", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    api_logs = relationship("APILog", back_populates="user")
