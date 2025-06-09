from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.crud import user as crud_user
from app.core.security import verify_password
from app.core.jwt import create_access_token
from app.api import deps
from app.models.user import User
from app.core.logging import LoggingService
from app.models.log import LogLevel, LogCategory

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate, 
    db: Session = Depends(deps.get_db),
    request: Request = None
) -> UserOut:
    """Register a new user with logging"""
    try:
        # Check if email already exists
        if crud_user.get_user_by_email(db, user_in.email):
            # Log failed registration attempt
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.WARNING,
                category=LogCategory.AUTHENTICATION,
                message=f"Registration failed: Email already exists - {user_in.email}",
                module="user_service",
                function_name="register_user",
                extra_data={"email": user_in.email, "reason": "email_exists"},
                request=request
            )
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        new_user = crud_user.create_user(db, user_in)
        
        # Log successful registration
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.AUTHENTICATION,
            message=f"User registered successfully: {new_user.email}",
            module="user_service",
            function_name="register_user",
            user_id=new_user.id,
            extra_data={
                "user_id": new_user.id,
                "email": new_user.email,
                "name": new_user.name
            },
            request=request
        )
        
        # Log audit event
        LoggingService.log_audit_event(
            db=db,
            user_id=new_user.id,
            action="CREATE",
            resource_type="User",
            resource_id=str(new_user.id),
            new_values={
                "email": new_user.email,
                "name": new_user.name,
                "role_id": new_user.role_id
            },
            request=request
        )
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        # Log registration error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.AUTHENTICATION,
            message=f"Registration error: {str(e)}",
            module="user_service",
            function_name="register_user",
            extra_data={"email": user_in.email, "error": str(e)},
            request=request
        )
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Dict[str, str])
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """User login with comprehensive logging"""
    try:
        user = crud_user.get_user_by_email(db, form_data.username)
        
        # Check if user exists and password is correct
        if not user or not verify_password(form_data.password, user.password):
            # Log failed login attempt
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.WARNING,
                category=LogCategory.AUTHENTICATION,
                message=f"Login failed: Invalid credentials for {form_data.username}",
                module="user_service",
                function_name="login_user",
                user_id=user.id if user else None,
                extra_data={
                    "email": form_data.username,
                    "reason": "invalid_password" if user else "user_not_found"
                },
                request=request
            )
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Create access token
        token = create_access_token({"sub": str(user.id), "role": str(user.role_id)})
        
        # Log successful login
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.AUTHENTICATION,
            message=f"User logged in successfully: {user.email}",
            module="user_service",
            function_name="login_user",
            user_id=user.id,
            extra_data={
                "user_id": user.id,
                "email": user.email,
                "role_id": user.role_id
            },
            request=request
        )
        
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        # Log login system error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.AUTHENTICATION,
            message=f"Login system error: {str(e)}",
            module="user_service",
            function_name="login_user",
            extra_data={"email": form_data.username, "error": str(e)},
            request=request
        )
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/me", response_model=UserOut)
def get_me(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
    request: Request = None
) -> UserOut:
    """Get current user profile with logging"""
    # Log profile access
    LoggingService.log_system_event(
        db=db,
        level=LogLevel.INFO,
        category=LogCategory.USER_ACTION,
        message=f"User accessed own profile: {current_user.email}",
        module="user_service",
        function_name="get_me",
        user_id=current_user.id,
        request=request
    )
    
    return current_user

@router.put("/me", response_model=UserOut)
def update_me(
    user_update: UserUpdate, 
    db: Session = Depends(deps.get_db), 
    current_user: User = Depends(deps.get_current_user),
    request: Request = None
) -> UserOut:
    """Update current user profile with logging"""
    try:
        # Store old values for audit
        old_values = {
            "name": current_user.name,
            "email": current_user.email
        }
        
        # Update user
        updated = crud_user.update_user(db, current_user.id, user_update)
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare new values for audit
        new_values = {
            "name": updated.name,
            "email": updated.email
        }
        
        # Log profile update
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            message=f"User updated own profile: {updated.email}",
            module="user_service",
            function_name="update_me",
            user_id=current_user.id,
            extra_data={"updated_fields": user_update.dict(exclude_unset=True)},
            request=request
        )
        
        # Log audit event
        LoggingService.log_audit_event(
            db=db,
            user_id=current_user.id,
            action="UPDATE",
            resource_type="User",
            resource_id=str(current_user.id),
            old_values=old_values,
            new_values=new_values,
            request=request
        )
        
        return updated
        
    except Exception as e:
        # Log update error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.USER_ACTION,
            message=f"Profile update failed: {str(e)}",
            module="user_service",
            function_name="update_me",
            user_id=current_user.id,
            extra_data={"error": str(e)},
            request=request
        )
        raise

@router.post("/register-admin", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_admin(
    user_in: UserCreate, 
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),
    request: Request = None
) -> UserOut:
    """Register admin user with logging"""
    try:
        if crud_user.get_user_by_email(db, user_in.email):
            # Log failed admin registration
            LoggingService.log_system_event(
                db=db,
                level=LogLevel.WARNING,
                category=LogCategory.SECURITY,
                message=f"Admin registration failed: Email exists - {user_in.email}",
                module="user_service",
                function_name="register_admin",
                user_id=current_user.id,
                extra_data={"target_email": user_in.email, "admin_id": current_user.id},
                request=request
            )
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_in.role_id = 1  # Admin role
        new_admin = crud_user.create_user(db, user_in)
        
        # Log admin creation
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.WARNING,  # Admin creation is a security event
            category=LogCategory.SECURITY,
            message=f"Admin user created: {new_admin.email} by {current_user.email}",
            module="user_service",
            function_name="register_admin",
            user_id=current_user.id,
            extra_data={
                "new_admin_id": new_admin.id,
                "new_admin_email": new_admin.email,
                "created_by": current_user.id
            },
            request=request
        )
        
        # Log audit event
        LoggingService.log_audit_event(
            db=db,
            user_id=current_user.id,
            action="CREATE",
            resource_type="AdminUser",
            resource_id=str(new_admin.id),
            new_values={
                "email": new_admin.email,
                "name": new_admin.name,
                "role_id": new_admin.role_id,
                "created_by": current_user.id
            },
            request=request
        )
        
        return new_admin
        
    except HTTPException:
        raise
    except Exception as e:
        # Log admin creation error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.SECURITY,
            message=f"Admin registration error: {str(e)}",
            module="user_service",
            function_name="register_admin",
            user_id=current_user.id,
            extra_data={"error": str(e), "target_email": user_in.email},
            request=request
        )
        raise

@router.put("/users/{user_id}/role/{role_id}", response_model=UserOut)
def update_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),
    request: Request = None
) -> UserOut:
    """Update user role with logging"""
    try:
        # Get target user for old values
        target_user = crud_user.get_user_by_id(db, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        old_role = target_user.role_id
        updated_user = crud_user.update_user_role(db, user_id, role_id)
        
        # Log role change (critical security event)
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.WARNING,
            category=LogCategory.SECURITY,
            message=f"User role changed: {target_user.email} from role {old_role} to {role_id} by {current_user.email}",
            module="user_service",
            function_name="update_user_role",
            user_id=current_user.id,
            extra_data={
                "target_user_id": user_id,
                "target_email": target_user.email,
                "old_role": old_role,
                "new_role": role_id,
                "changed_by": current_user.id
            },
            request=request
        )
        
        # Log audit event
        LoggingService.log_audit_event(
            db=db,
            user_id=current_user.id,
            action="UPDATE",
            resource_type="UserRole",
            resource_id=str(user_id),
            old_values={"role_id": old_role},
            new_values={"role_id": role_id},
            request=request
        )
        
        return updated_user
        
    except Exception as e:
        # Log role change error
        LoggingService.log_system_event(
            db=db,
            level=LogLevel.ERROR,
            category=LogCategory.SECURITY,
            message=f"Role update failed: {str(e)}",
            module="user_service",
            function_name="update_user_role",
            user_id=current_user.id,
            extra_data={"error": str(e), "target_user_id": user_id},
            request=request
        )
        raise

@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),
    request: Request = None
) -> List[UserOut]:
    """Get all users with logging"""
    # Log admin access to user list
    LoggingService.log_system_event(
        db=db,
        level=LogLevel.INFO,
        category=LogCategory.SECURITY,
        message=f"Admin accessed user list: {current_user.email}",
        module="user_service",
        function_name="get_all_users",
        user_id=current_user.id,
        request=request
    )
    
    users = db.query(User).all()
    
    # Log additional details about the access
    LoggingService.log_system_event(
        db=db,
        level=LogLevel.INFO,
        category=LogCategory.USER_ACTION,
        message=f"User list retrieved: {len(users)} users",
        module="user_service",
        function_name="get_all_users",
        user_id=current_user.id,
        extra_data={"users_count": len(users)},
        request=request
    )
    
    return users
