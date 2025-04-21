from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate

def create_lead(db: Session, lead_in: LeadCreate, user_id: int):
    # Use the assigned_user_id from the request if provided, otherwise use the current user's ID
    assigned_id = lead_in.assigned_user_id if lead_in.assigned_user_id is not None else user_id
    
    # Convert to dict and exclude assigned_user_id since we're handling it separately
    lead_data = lead_in.model_dump(exclude={"assigned_user_id"})
    lead = Lead(**lead_data, assigned_user_id=assigned_id)
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_user_leads(db: Session, user_id: int, skip: int = 0, limit: int = 100, search: str = None, status: str = None):
    """Get leads assigned to a specific user with filtering options"""
    # Start with a query base
    query = db.query(Lead)
    
    # Apply filters
    query = query.filter(Lead.assigned_user_id == user_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_term)) | 
            (Lead.email.ilike(search_term)) |
            (Lead.phone.ilike(search_term))
        )
    
    if status:
        query = query.filter(Lead.status == status)
    
    # Order, paginate and execute
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()

def get_user_leads_count(db: Session, user_id: int, search: str = None, status: str = None):
    """Count leads assigned to a specific user with filtering options"""
    query = db.query(Lead).filter(Lead.assigned_user_id == user_id)
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_term)) | 
            (Lead.email.ilike(search_term)) |
            (Lead.phone.ilike(search_term))
        )
    
    if status:
        query = query.filter(Lead.status == status)
        
    return query.count()

def update_lead(db: Session, lead_id: int, lead_update: LeadUpdate):
    """Update a lead by ID"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        for field, value in lead_update.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        db.commit()
        db.refresh(lead)
    return lead

def delete_lead(db: Session, lead_id: int):
    """Delete a lead by ID"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        db.delete(lead)
        db.commit()
    return lead

def get_all_leads(db: Session, skip: int = 0, limit: int = 100, search: str = None, status: str = None):
    """Get all leads with filtering options"""
    # Start with a query base
    query = db.query(Lead)
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_term)) | 
            (Lead.email.ilike(search_term)) |
            (Lead.phone.ilike(search_term))
        )
    
    if status:
        query = query.filter(Lead.status == status)
        
    # Apply pagination
    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()

def get_leads_count(db: Session, search: str = None, status: str = None):
    query = db.query(Lead)
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_term)) | 
            (Lead.email.ilike(search_term)) |
            (Lead.phone.ilike(search_term))
        )
    
    if status:
        query = query.filter(Lead.status == status)
        
    return query.count()

def get_lead_by_id(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()
