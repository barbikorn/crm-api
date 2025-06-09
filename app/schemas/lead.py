from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from app.models.lead import BudgetRange, StatusChoices

class LeadBase(BaseModel):
    # Lead information
    name: Optional[str] = None
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
    email: Optional[str] = None
    job_position: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    line_id: Optional[str] = None
    age: Optional[int] = None
    
    # Business information
    customer_budget: Optional[BudgetRange] = None
    product_interest: Optional[str] = None
    invoice_total: Optional[float] = 0.0
    
    # CRM fields
    status: Optional[StatusChoices] = StatusChoices.NEW
    priority: Optional[int] = 0
    salesperson: Optional[str] = None
    sales_team: Optional[str] = None
    tags: Optional[str] = None
    
    # Notes
    internal_notes: Optional[str] = None
    
    # New fields for source tracking
    source: Optional[str] = None
    platform_id: Optional[str] = None

class LeadCreate(LeadBase):
    assigned_user_id: Optional[int] = None

class LeadUpdate(LeadBase):
    assigned_user_id: Optional[int] = None

class LeadOut(LeadBase):
    id: int
    assigned_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Lead Status Change
class LeadStatusChangeBase(BaseModel):
    previous_status: str
    new_status: str
    changed_by_id: Optional[int] = None

class LeadStatusChangeCreate(LeadStatusChangeBase):
    pass

class LeadStatusChangeUpdate(BaseModel):
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    changed_by_id: Optional[int] = None

class LeadStatusChangeOut(LeadStatusChangeBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Lead Note
class LeadNoteBase(BaseModel):
    content: str
    user_id: Optional[int] = None

class LeadNoteCreate(LeadNoteBase):
    pass

class LeadNoteUpdate(BaseModel):
    content: Optional[str] = None
    user_id: Optional[int] = None

class LeadNoteOut(LeadNoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
