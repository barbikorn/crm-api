from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class BudgetRange(str, enum.Enum):
    RANGE_1 = "100,000 ฿ - 300,000 ฿"
    RANGE_2 = "400,000 ฿ - 600,000 ฿" 
    RANGE_3 = "มากกว่า 700,000 ฿"

class Lead(Base):
    __tablename__ = "lead"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # Lead name (e.g., "Soap")
    
    # Probability
    probability = Column(Float, default=0.0)  # e.g., 10.39%
    
    # Company information
    company_name = Column(String, nullable=True)
    
    # Address components
    street = Column(String, nullable=True)
    street2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    website = Column(String, nullable=True)
    
    # Contact details
    contact_name = Column(String, nullable=True)
    contact_title = Column(String, nullable=True)  # Title/salutation
    email = Column(String)
    job_position = Column(String, nullable=True)
    phone = Column(String)
    mobile = Column(String, nullable=True)
    line_id = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    
    # Business information
    customer_budget = Column(Enum(BudgetRange), nullable=True)
    product_interest = Column(String, nullable=True)
    invoice_total = Column(Float, default=0.0)
    
    # CRM fields
    status = Column(String)
    priority = Column(Integer, default=0)  # 0-3 for star rating
    salesperson = Column(String, nullable=True)
    sales_team = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    
    # Notes
    internal_notes = Column(Text, nullable=True)
    
    # Relationship fields
    assigned_user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_user = relationship("User")
