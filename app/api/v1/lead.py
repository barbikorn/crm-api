from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate
from app.crud import lead as crud_lead
from app.api import deps
from app.models.user import User
from app.core.logging import LoggingService
from app.models.log import LogLevel, LogCategory

router = APIRouter()

@router.post("/leads", response_model=LeadOut)
def create_lead(
    lead: LeadCreate, 
    db: Session = Depends(deps.get_db), 
    user: User = Depends(deps.get_current_user),
    request: Request = None
):
    """Create a lead with comprehensive logging"""
    try:
        # Check if user can assign to another user (admin check)
        if lead.assigned_user_id is not None and lead.assigned_user_id != user.id and user.role_id != 1:
            # Log unauthorized assignment attempt
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.WARNING,
                category=LogCategory.SECURITY,
                message=f"Unauthorized lead assignment attempt by {user.email}",
                module="lead_service",
                function_name="create_lead",
                user_id=user.id,
                extra_data={
                    "attempted_assignment": lead.assigned_user_id,
                    "user_role": user.role_id
                },
                request=request
            )
            raise HTTPException(
                status_code=403, 
                detail="Only admins can assign leads to other users"
            )
        
        # Create the lead
        new_lead = crud_lead.create_lead(db, lead, user.id)
        
        # Log successful lead creation
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.BUSINESS_LOGIC,
            message=f"Lead created: {new_lead.name or 'Unknown'} by {user.email}",
            module="lead_service",
            function_name="create_lead",
            user_id=user.id,
            extra_data={
                "lead_id": new_lead.id,
                "lead_name": new_lead.name,
                "company": new_lead.company_name,
                "email": new_lead.email,
                "assigned_to": new_lead.assigned_user_id,
                "status": new_lead.status,
                "source": new_lead.source
            },
            request=request
        )
        
        # Log audit event
        LoggingService.log_audit_event(
            db=db,
            user_id=user.id,
            action="CREATE",
            resource_type="Lead",
            resource_id=str(new_lead.id),
            new_values={
                "name": new_lead.name,
                "company_name": new_lead.company_name,
                "email": new_lead.email,
                "status": new_lead.status,
                "assigned_user_id": new_lead.assigned_user_id
            },
            request=request
        )
        
        return new_lead
        
    except HTTPException:
        raise
    except Exception as e:
        # Log lead creation error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.BUSINESS_LOGIC,
            message=f"Lead creation failed: {str(e)}",
            module="lead_service",
            function_name="create_lead",
            user_id=user.id,
            extra_data={"error": str(e), "lead_data": lead.dict()},
            request=request
        )
        raise

@router.get("/leads", response_model=List[LeadOut])
def get_leads(
    all_leads: bool = Query(False, description="Get all leads (admin only)"),
    user_id: Optional[int] = Query(None, description="Get leads for specific user (admin only)"),
    skip: int = Query(0, description="Number of leads to skip"),
    limit: int = Query(100, description="Maximum number of leads to return"),
    search: Optional[str] = Query(None, description="Search term for name, email or phone"),
    status: Optional[str] = Query(None, description="Filter by lead status"),
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user),
    request: Request = None
):
    """Get leads with flexible filtering options and logging"""
    try:
        # Log the lead query
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            message=f"Lead query by {user.email}",
            module="lead_service",
            function_name="get_leads",
            user_id=user.id,
            extra_data={
                "all_leads": all_leads,
                "target_user_id": user_id,
                "search": search,
                "status": status,
                "skip": skip,
                "limit": limit
            },
            request=request
        )
        
        # Case 1: Admin requesting all leads
        if all_leads:
            if user.role_id != 1:  # Admin check
                # Log unauthorized access attempt
                LoggingService.log_system_event(
                    db=db,
                    level=LogLevel.WARNING,
                    category=LogCategory.SECURITY,
                    message=f"Unauthorized attempt to view all leads by {user.email}",
                    module="lead_service",
                    function_name="get_leads",
                    user_id=user.id,
                    request=request
                )
                raise HTTPException(status_code=403, detail="Only admins can view all leads")
            
            leads = crud_lead.get_all_leads(db, skip=skip, limit=limit, search=search, status=status)
            
            # Log admin access to all leads
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.INFO,
                category=LogCategory.SECURITY,
                message=f"Admin accessed all leads: {len(leads)} results",
                module="lead_service",
                function_name="get_leads",
                user_id=user.id,
                extra_data={"leads_count": len(leads)},
                request=request
            )
            
            return leads
        
        # Case 2: Admin/user requesting specific user's leads
        if user_id is not None:
            # Ensure only admins can view other users' leads
            if user.role_id != 1 and user.id != user_id:
                # Log unauthorized access attempt
                LoggingService.log_system_event(
                    db=db,
                    level=LogLevel.WARNING,
                    category=LogCategory.SECURITY,
                    message=f"Unauthorized attempt to view user {user_id} leads by {user.email}",
                    module="lead_service",
                    function_name="get_leads",
                    user_id=user.id,
                    extra_data={"target_user_id": user_id},
                    request=request
                )
                raise HTTPException(status_code=403, detail="Not authorized to view other users' leads")
            
            leads = crud_lead.get_user_leads(db, user_id, skip=skip, limit=limit, search=search, status=status)
            return leads
        
        # Case 3: Default - user viewing their own leads
        leads = crud_lead.get_user_leads(db, user.id, skip=skip, limit=limit, search=search, status=status)
        return leads
        
    except HTTPException:
        raise
    except Exception as e:
        # Log leads query error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.BUSINESS_LOGIC,
            message=f"Leads query failed: {str(e)}",
            module="lead_service",
            function_name="get_leads",
            user_id=user.id,
            extra_data={"error": str(e)},
            request=request
        )
        raise

@router.put("/leads/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: int, 
    update: LeadUpdate, 
    db: Session = Depends(deps.get_db), 
    user: User = Depends(deps.get_current_user),
    request: Request = None
):
    """Update a lead with comprehensive logging"""
    try:
        # Check if the lead exists
        existing_lead = crud_lead.get_lead_by_id(db, lead_id)
        if not existing_lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Store old values for audit
        old_values = {
            "name": existing_lead.name,
            "company_name": existing_lead.company_name,
            "email": existing_lead.email,
            "status": existing_lead.status,
            "assigned_user_id": existing_lead.assigned_user_id
        }
        
        # Check authorization - admins can update any lead, users only their own
        if user.role_id != 1 and existing_lead.assigned_user_id != user.id:
            # Log unauthorized update attempt
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.WARNING,
                category=LogCategory.SECURITY,
                message=f"Unauthorized lead update attempt: Lead {lead_id} by {user.email}",
                module="lead_service",
                function_name="update_lead",
                user_id=user.id,
                extra_data={"lead_id": lead_id, "lead_owner": existing_lead.assigned_user_id},
                request=request
            )
            raise HTTPException(status_code=403, detail="Not authorized to update this lead")
        
        # Check if trying to reassign and has permission
        if update.assigned_user_id is not None and update.assigned_user_id != existing_lead.assigned_user_id:
            if user.role_id != 1:  # Admin check
                # Log unauthorized reassignment attempt
                LoggingService.log_system_event(
                    db=db,
                    level=LogLevel.WARNING,
                    category=LogCategory.SECURITY,
                    message=f"Unauthorized lead reassignment attempt by {user.email}",
                    module="lead_service",
                    function_name="update_lead",
                    user_id=user.id,
                    extra_data={
                        "lead_id": lead_id,
                        "from_user": existing_lead.assigned_user_id,
                        "to_user": update.assigned_user_id
                    },
                    request=request
                )
                raise HTTPException(status_code=403, detail="Only admins can reassign leads")
            
            # Log lead reassignment
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.INFO,
                category=LogCategory.BUSINESS_LOGIC,
                message=f"Lead {lead_id} reassigned from user {existing_lead.assigned_user_id} to {update.assigned_user_id} by {user.email}",
                module="lead_service",
                function_name="update_lead",
                user_id=user.id,
                extra_data={
                    "lead_id": lead_id,
                    "from_user": existing_lead.assigned_user_id,
                    "to_user": update.assigned_user_id
                },
                request=request
            )
        
        # Update the lead
        updated_lead = crud_lead.update_lead(db, lead_id, update)
        
        # Prepare new values for audit
        new_values = {
            "name": updated_lead.name,
            "company_name": updated_lead.company_name,
            "email": updated_lead.email,
            "status": updated_lead.status,
            "assigned_user_id": updated_lead.assigned_user_id
        }
        
        # Log successful lead update
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.BUSINESS_LOGIC,
            message=f"Lead updated: {updated_lead.name or 'Unknown'} (ID: {lead_id}) by {user.email}",
            module="lead_service",
            function_name="update_lead",
            user_id=user.id,
            extra_data={
                "lead_id": lead_id,
                "updated_fields": update.dict(exclude_unset=True)
            },
            request=request
        )
        
        # Log audit event
        LoggingService.log_audit_event(
            db=db,
            user_id=user.id,
            action="UPDATE",
            resource_type="Lead",
            resource_id=str(lead_id),
            old_values=old_values,
            new_values=new_values,
            request=request
        )
        
        return updated_lead
        
    except HTTPException:
        raise
    except Exception as e:
        # Log lead update error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.BUSINESS_LOGIC,
            message=f"Lead update failed: {str(e)}",
            module="lead_service",
            function_name="update_lead",
            user_id=user.id,
            extra_data={"error": str(e), "lead_id": lead_id},
            request=request
        )
        raise

@router.delete("/leads/{lead_id}")
def delete_lead(
    lead_id: int, 
    db: Session = Depends(deps.get_db), 
    user: User = Depends(deps.get_current_user),
    request: Request = None
):
    """Delete a lead with comprehensive logging"""
    try:
        # Check if the lead exists
        existing_lead = crud_lead.get_lead_by_id(db, lead_id)
        if not existing_lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Store lead data for audit
        lead_data = {
            "name": existing_lead.name,
            "company_name": existing_lead.company_name,
            "email": existing_lead.email,
            "status": existing_lead.status,
            "assigned_user_id": existing_lead.assigned_user_id
        }
        
        # Check authorization - admins can delete any lead, users only their own
        if user.role_id != 1 and existing_lead.assigned_user_id != user.id:
            # Log unauthorized deletion attempt
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.WARNING,
                category=LogCategory.SECURITY,
                message=f"Unauthorized lead deletion attempt: Lead {lead_id} by {user.email}",
                module="lead_service",
                function_name="delete_lead",
                user_id=user.id,
                extra_data={"lead_id": lead_id, "lead_owner": existing_lead.assigned_user_id},
                request=request
            )
            raise HTTPException(status_code=403, detail="Not authorized to delete this lead")
        
        # Delete the lead
        crud_lead.delete_lead(db, lead_id)
        
        # Log successful lead deletion
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.WARNING,  # Deletion is a significant action
            category=LogCategory.BUSINESS_LOGIC,
            message=f"Lead deleted: {existing_lead.name or 'Unknown'} (ID: {lead_id}) by {user.email}",
            module="lead_service",
            function_name="delete_lead",
            user_id=user.id,
            extra_data={
                "lead_id": lead_id,
                "deleted_lead_data": lead_data
            },
            request=request
        )
        
        # Log audit event
        LoggingService.log_audit_event(
            db=db,
            user_id=user.id,
            action="DELETE",
            resource_type="Lead",
            resource_id=str(lead_id),
            old_values=lead_data,
            request=request
        )
        
        return {"detail": "Lead deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        # Log lead deletion error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.BUSINESS_LOGIC,
            message=f"Lead deletion failed: {str(e)}",
            module="lead_service",
            function_name="delete_lead",
            user_id=user.id,
            extra_data={"error": str(e), "lead_id": lead_id},
            request=request
        )
        raise

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

@router.get("/leads/platform/{platform_id}", response_model=LeadOut)
def get_lead_by_platform_id(
    platform_id: str,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    """Get a lead by its platform-specific ID"""
    lead = crud_lead.get_lead_by_platform_id(db, platform_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check authorization - admins can view any lead, users only their own
    if user.role_id != 1 and lead.assigned_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this lead")
    
    return lead

@router.put("/leads/platform/{platform_id}", response_model=LeadOut)
def update_lead_by_platform_id(
    platform_id: str,
    update: LeadUpdate,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    """Update a lead by its platform-specific ID"""
    lead = crud_lead.get_lead_by_platform_id(db, platform_id)
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check authorization - admins can update any lead, users only their own
    if user.role_id != 1 and lead.assigned_user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this lead")
    
    # Update the lead
    lead = crud_lead.update_lead_by_platform_id(db, platform_id, update)
    return lead

# Lead Status Change
from app.schemas.lead import LeadStatusChangeCreate, LeadStatusChangeOut, LeadStatusChangeUpdate, LeadNoteCreate, LeadNoteOut, LeadNoteUpdate

@router.post("/leads/{lead_id}/status-change", response_model=LeadStatusChangeOut)
def create_status_change(
    lead_id: int,
    status_change: LeadStatusChangeCreate,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    return crud_lead.create_lead_status_change(db, lead_id, status_change)

@router.put("/status-change/{status_change_id}", response_model=LeadStatusChangeOut)
def update_status_change(
    status_change_id: int,
    status_change_update: LeadStatusChangeUpdate,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    return crud_lead.update_lead_status_change(db, status_change_id, status_change_update)

@router.delete("/status-change/{status_change_id}")
def delete_status_change(
    status_change_id: int,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    crud_lead.delete_lead_status_change(db, status_change_id)
    return {"detail": "Status change deleted successfully"}

@router.post("/leads/{lead_id}/notes", response_model=LeadNoteOut)
def create_note(
    lead_id: int,
    note: LeadNoteCreate,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    return crud_lead.create_lead_note(db, lead_id, note)

@router.put("/notes/{note_id}", response_model=LeadNoteOut)
def update_note(
    note_id: int,
    note_update: LeadNoteUpdate,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    return crud_lead.update_lead_note(db, note_id, note_update)

@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(deps.get_db),
    user: User = Depends(deps.get_current_user)
):
    crud_lead.delete_lead_note(db, note_id)
    return {"detail": "Note deleted successfully"}
