from sqlalchemy.orm import Session
from app.models.lead import Lead, LeadStatusChange, LeadNote
from app.schemas.lead import LeadCreate, LeadUpdate, LeadStatusChangeCreate, LeadStatusChangeUpdate, LeadNoteCreate, LeadNoteUpdate

def create_lead(db: Session, lead_in: LeadCreate, user_id: int = None):
    # Use the assigned_user_id from the request if provided, otherwise use the current user's ID (if any)
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
        if 'status' in lead_update.model_dump(exclude_unset=True):
            previous_status = lead.status
            new_status = lead_update.status
            if previous_status != new_status:
                create_lead_status_change(db, lead_id, LeadStatusChangeCreate(
                    previous_status=previous_status,
                    new_status=new_status,
                    changed_by_id=lead.assigned_user_id
                ))
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


# Lead Status Change

def create_lead_status_change(db: Session, lead_id: int, status_change_in: LeadStatusChangeCreate):
    status_change = LeadStatusChange(**status_change_in.dict(), lead_id=lead_id)
    db.add(status_change)
    db.commit()
    db.refresh(status_change)
    return status_change

def get_lead_status_change(db: Session, status_change_id: int):
    return db.query(LeadStatusChange).filter(LeadStatusChange.id == status_change_id).first()

def update_lead_status_change(db: Session, status_change_id: int, status_change_update: LeadStatusChangeUpdate):
    status_change = get_lead_status_change(db, status_change_id)
    if status_change:
        for field, value in status_change_update.dict(exclude_unset=True).items():
            setattr(status_change, field, value)
        db.commit()
        db.refresh(status_change)
    return status_change

def delete_lead_status_change(db: Session, status_change_id: int):
    status_change = get_lead_status_change(db, status_change_id)
    if status_change:
        db.delete(status_change)
        db.commit()
    return status_change

def create_lead_note(db: Session, lead_id: int, note_in: LeadNoteCreate):
    note = LeadNote(**note_in.dict(), lead_id=lead_id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_lead_note(db: Session, note_id: int):
    return db.query(LeadNote).filter(LeadNote.id == note_id).first()

def update_lead_note(db: Session, note_id: int, note_update: LeadNoteUpdate):
    note = get_lead_note(db, note_id)
    if note:
        for field, value in note_update.dict(exclude_unset=True).items():
            setattr(note, field, value)
        db.commit()
        db.refresh(note)
    return note

def delete_lead_note(db: Session, note_id: int):
    note = get_lead_note(db, note_id)
    if note:
        db.delete(note)
        db.commit()
    return note

def get_lead_by_platform_id(db: Session, platform_id: str):
    """Retrieve a lead by its platform-specific ID"""
    return db.query(Lead).filter(Lead.platform_id == platform_id).first()

def update_lead_by_platform_id(db: Session, platform_id: str, lead_update: LeadUpdate):
    """Update a lead by its platform-specific ID"""
    lead = get_lead_by_platform_id(db, platform_id)
    if lead:
        for field, value in lead_update.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        db.commit()
        db.refresh(lead)
    return lead
