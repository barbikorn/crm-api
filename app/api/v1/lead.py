from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate
from app.crud import lead as crud_lead
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/leads", response_model=LeadOut)
def create_lead(
    lead: LeadCreate, 
    db: Session = Depends(deps.get_db), 
    user: User = Depends(deps.get_current_user)
):
    # Check if user can assign to another user (admin check)
    if lead.assigned_user_id is not None and lead.assigned_user_id != user.id and user.role_id != 1:
        raise HTTPException(
            status_code=403, 
            detail="Only admins can assign leads to other users"
        )
    
    return crud_lead.create_lead(db, lead, user.id)

@router.get("/leads", response_model=List[LeadOut])
def get_leads(
    all_leads: bool = Query(False, description="Get all leads (admin only)"),
    user_id: Optional[int] = Query(None, description="Get leads for specific user (admin only)"),
    skip: int = Query(0, description="Number of leads to skip"),
    limit: int = Query(100, description="Maximum number of leads to return"),
    search: Optional[str] = Query(None, description="Search term for name, email or phone"),
    status: Optional[str] = Query(None, description="Filter by lead status"),
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    """
    Get leads with flexible filtering options:
    - By default: Current user's leads
    - With all_leads=true: All leads (admin only)
    - With user_id parameter: Specific user's leads (admin only or own leads)
    """
    # Case 1: Admin requesting all leads
    if all_leads:
        if user.role_id != 1:  # Admin check
            raise HTTPException(status_code=403, detail="Only admins can view all leads")
        return crud_lead.get_all_leads(db, skip=skip, limit=limit, search=search, status=status)
    
    # Case 2: Admin/user requesting specific user's leads
    if user_id is not None:
        # Ensure only admins can view other users' leads
        if user.role_id != 1 and user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view other users' leads")
        return crud_lead.get_user_leads(db, user_id, skip=skip, limit=limit, search=search, status=status)
    
    # Case 3: Default - user viewing their own leads
    return crud_lead.get_user_leads(db, user.id, skip=skip, limit=limit, search=search, status=status)

@router.put("/leads/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: int, 
    update: LeadUpdate, 
    db: Session = Depends(deps.get_db), 
    user: User = Depends(deps.get_current_user)
):
    # Check if the lead exists
    existing_lead = crud_lead.get_lead_by_id(db, lead_id)
    if not existing_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check authorization - admins can update any lead, users only their own
    if user.role_id != 1 and existing_lead.assigned_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this lead")
    
    # Check if trying to reassign and has permission
    if update.assigned_user_id is not None and update.assigned_user_id != existing_lead.assigned_user_id:
        if user.role_id != 1:  # Admin check
            raise HTTPException(status_code=403, detail="Only admins can reassign leads")
    
    # Update the lead
    lead = crud_lead.update_lead(db, lead_id, update)
    return lead

@router.delete("/leads/{lead_id}")
def delete_lead(
    lead_id: int, 
    db: Session = Depends(deps.get_db), 
    user: User = Depends(deps.get_current_user)
):
    # Check if the lead exists
    existing_lead = crud_lead.get_lead_by_id(db, lead_id)
    if not existing_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check authorization - admins can delete any lead, users only their own
    if user.role_id != 1 and existing_lead.assigned_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this lead")
    
    # Delete the lead
    crud_lead.delete_lead(db, lead_id)
    return {"detail": "Lead deleted successfully"}

@router.get("/leads/count")
def get_leads_count(
    all_leads: bool = Query(False, description="Count all leads (admin only)"),
    user_id: Optional[int] = Query(None, description="Count leads for specific user (admin only)"),
    search: Optional[str] = Query(None, description="Search term for name, email or phone"),
    status: Optional[str] = Query(None, description="Filter by lead status"),
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    """Get total count of leads with the same filtering options as the GET endpoint"""
    # Case 1: Admin requesting all leads count
    if all_leads:
        if user.role_id != 1:  # Admin check
            raise HTTPException(status_code=403, detail="Only admins can count all leads")
        count = crud_lead.get_leads_count(db, search=search, status=status)
        return {"total": count}
    
    # Case 2: Admin/user requesting specific user's leads count
    if user_id is not None:
        # Ensure only admins can view other users' leads
        if user.role_id != 1 and user.id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to count other users' leads")
        count = crud_lead.get_user_leads_count(db, user_id, search=search, status=status)
        return {"total": count}
    
    # Case 3: Default - user counting their own leads
    count = crud_lead.get_user_leads_count(db, user.id, search=search, status=status)
    return {"total": count}

@router.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead_by_id(
    lead_id: int, 
    db: Session = Depends(deps.get_db), 
    user: User = Depends(deps.get_current_user)
):
    """Get a specific lead by ID"""
    lead = crud_lead.get_lead_by_id(db, lead_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check authorization - admins can view any lead, users only their own
    if user.role_id != 1 and lead.assigned_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this lead")
    
    return lead
