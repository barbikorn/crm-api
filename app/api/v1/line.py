from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.line import LineMessageCreate, LineMessageOut, LineUserCreate, LineUserOut
from app.crud import line as crud_line
from app.api import deps
from app.core.line_logging import LineLoggingService

router = APIRouter()

@router.post("/line/messages", response_model=LineMessageOut)
def create_line_message(
    message: LineMessageCreate, 
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Create a LINE message and log the event"""
    # Create the message
    created_message = crud_line.create_line_message(db, message)
    
    # Log the message creation
    LineLoggingService.log_line_message_received(
        db=db,
        line_message=created_message,
        request=request
    )
    
    return created_message

@router.post("/line/users", response_model=LineUserOut)
def create_line_user(
    user: LineUserCreate, 
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Create a LINE user and log the event"""
    # Create the user
    created_user = crud_line.create_line_user(db, user)
    
    # Log user registration
    LineLoggingService.log_line_user_interaction(
        db=db,
        line_user_id=user.user_id,
        interaction_type="register",
        line_user=created_user,
        request=request
    )
    
    return created_user

@router.get("/line/messages/{message_id}", response_model=LineMessageOut)
def get_line_message(
    message_id: int, 
    db: Session = Depends(deps.get_db)
):
    message = crud_line.get_line_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.get("/line/users/{user_id}", response_model=LineUserOut)
def get_line_user(
    user_id: str, 
    db: Session = Depends(deps.get_db)
):
    user = crud_line.get_line_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/line/messages/{message_id}", response_model=LineMessageOut)
def update_line_message(
    message_id: int, 
    message: LineMessageCreate, 
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Update a LINE message and log the event"""
    updated_message = crud_line.update_line_message(db, message_id, message)
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Log message update
    LineLoggingService.log_line_user_interaction(
        db=db,
        line_user_id=message.user_id,
        interaction_type="message_update",
        additional_data={"message_id": message_id},
        request=request
    )
    
    return updated_message

@router.delete("/line/messages/{message_id}", response_model=LineMessageOut)
def delete_line_message(
    message_id: int, 
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Delete a LINE message and log the event"""
    message = crud_line.delete_line_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Log message deletion
    LineLoggingService.log_line_user_interaction(
        db=db,
        line_user_id=message.user_id,
        interaction_type="message_delete",
        additional_data={"message_id": message_id},
        request=request
    )
    
    return message

@router.put("/line/users/{user_id}", response_model=LineUserOut)
def update_line_user(
    user_id: str, 
    user: LineUserCreate, 
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Update a LINE user and log the event"""
    updated_user = crud_line.update_line_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log user update
    LineLoggingService.log_line_user_interaction(
        db=db,
        line_user_id=user_id,
        interaction_type="profile_update",
        line_user=updated_user,
        request=request
    )
    
    return updated_user

@router.delete("/line/users/{user_id}", response_model=LineUserOut)
def delete_line_user(
    user_id: str, 
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Delete a LINE user and log the event"""
    user = crud_line.delete_line_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log user deletion
    LineLoggingService.log_line_user_interaction(
        db=db,
        line_user_id=user_id,
        interaction_type="unregister",
        additional_data={"deleted_user": user.display_name},
        request=request
    )
    
    return user

@router.get("/line/messages", response_model=List[LineMessageOut])
def get_all_line_messages(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db)
):
    return crud_line.get_all_line_messages(db, skip=skip, limit=limit)

@router.get("/line/users", response_model=List[LineUserOut])
def get_all_line_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db)
):
    return crud_line.get_all_line_users(db, skip=skip, limit=limit)

# New LINE-specific logging endpoints
@router.post("/line/webhook")
def line_webhook(
    webhook_data: dict,
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Handle LINE webhook and log events"""
    try:
        # Process webhook data (implement your webhook logic here)
        events = webhook_data.get("events", [])
        
        for event in events:
            event_type = event.get("type")
            source = event.get("source", {})
            user_id = source.get("userId")
            
            if event_type == "message":
                # Handle message event
                message = event.get("message", {})
                message_data = LineMessageCreate(
                    user_id=user_id,
                    message_text=message.get("text", ""),
                    message_type=message.get("type", "text"),
                    reply_token=event.get("replyToken")
                )
                
                # Save message to database
                created_message = crud_line.create_line_message(db, message_data)
                
                # Log the received message
                LineLoggingService.log_line_message_received(
                    db=db,
                    line_message=created_message,
                    request=request
                )
                
            elif event_type in ["follow", "unfollow", "join", "leave"]:
                # Log user interaction events
                LineLoggingService.log_line_webhook_event(
                    db=db,
                    event_type=event_type,
                    line_user_id=user_id,
                    event_data=event,
                    request=request
                )
        
        return {"status": "success", "processed_events": len(events)}
        
    except Exception as e:
        # Log webhook processing error
        LineLoggingService.log_line_webhook_event(
            db=db,
            event_type="webhook_error",
            line_user_id="unknown",
            event_data=webhook_data,
            processing_success=False,
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@router.post("/line/send-message")
def send_line_message(
    user_id: str,
    message: str,
    message_type: str = "text",
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """Send a message to LINE user and log the event"""
    try:
        # Implement your LINE message sending logic here
        # This is a placeholder for the actual LINE API call
        
        # Simulate API call
        success = True  # Replace with actual API response
        
        # Log the sent message
        LineLoggingService.log_line_message_sent(
            db=db,
            line_user_id=user_id,
            message_content=message,
            message_type=message_type,
            success=success,
            request=request
        )
        
        return {"status": "sent", "user_id": user_id, "message": message}
        
    except Exception as e:
        # Log failed message sending
        LineLoggingService.log_line_message_sent(
            db=db,
            line_user_id=user_id,
            message_content=message,
            message_type=message_type,
            success=False,
            error_message=str(e),
            request=request
        )
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/line/health")
def line_bot_health_check(
    db: Session = Depends(deps.get_db),
    request: Request = None
):
    """LINE bot health check with logging"""
    try:
        # Test database connectivity
        recent_messages = crud_line.get_all_line_messages(db, skip=0, limit=1)
        db_status = "healthy"
        
        # Test LINE API connectivity (implement your actual test)
        api_status = "healthy"  # Replace with actual LINE API health check
        
        overall_status = "healthy" if db_status == "healthy" and api_status == "healthy" else "degraded"
        
        # Log health check
        LineLoggingService.log_line_bot_health(
            db=db,
            status=overall_status,
            check_type="full_check",
            details={
                "database": db_status,
                "line_api": api_status,
                "recent_messages_count": len(recent_messages)
            },
            request=request
        )
        
        return {
            "status": overall_status,
            "database": db_status,
            "line_api": api_status,
            "timestamp": "2024-01-01T00:00:00Z"  # Replace with actual timestamp
        }
        
    except Exception as e:
        # Log health check failure
        LineLoggingService.log_line_bot_health(
            db=db,
            status="unhealthy",
            check_type="full_check",
            details={"error": str(e)},
            request=request
        )
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")