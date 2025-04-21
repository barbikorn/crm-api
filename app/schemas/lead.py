from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from app.models.lead import BudgetRange

class LeadBase(BaseModel):
    # Lead information
    name: str
    probability: Optional[float] = 0.0
    
    # Company information
    company_name: Optional[str] = None
    
    # Address components
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    
    website: Optional[str] = None
    
    # Contact details
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    email: str
    job_position: Optional[str] = None
    phone: str
    mobile: Optional[str] = None
    line_id: Optional[str] = None
    age: Optional[int] = None
    
    # Business information
    customer_budget: Optional[BudgetRange] = None  # Use the enum type
    product_interest: Optional[str] = None
    invoice_total: Optional[float] = 0.0
    
    # CRM fields
    status: str
    priority: Optional[int] = 0
    salesperson: Optional[str] = None
    sales_team: Optional[str] = None
    tags: Optional[str] = None
    
    # Notes
    internal_notes: Optional[str] = None

class LeadCreate(LeadBase):
    assigned_user_id: Optional[int] = None

class LeadUpdate(BaseModel):
    # Lead information
    name: Optional[str] = None
    probability: Optional[float] = None
    
    # Company information
    company_name: Optional[str] = None
    
    # Address components
    street: Optional[str] = None
    street2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    
    website: Optional[str] = None
    
    # Contact details
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    email: Optional[str] = None
    job_position: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    line_id: Optional[str] = None
    age: Optional[int] = None
    
    # Business information
    customer_budget: Optional[BudgetRange] = None  # Use the enum type
    product_interest: Optional[str] = None
    invoice_total: Optional[float] = None
    
    # CRM fields
    status: Optional[str] = None
    priority: Optional[int] = None
    salesperson: Optional[str] = None
    sales_team: Optional[str] = None
    tags: Optional[str] = None
    
    # Notes
    internal_notes: Optional[str] = None
    
    assigned_user_id: Optional[int] = None

class LeadOut(LeadBase):
    id: int
    assigned_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
