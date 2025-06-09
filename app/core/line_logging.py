from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request

from app.core.logging import LoggingService
from app.models.log import LogLevel, LogCategory
from app.models.line import LineMessage, LineUser

class LineLoggingService:
    """Specialized logging service for LINE chat functionality"""
    
    @staticmethod
    def log_line_message_received(
        db: Session,
        line_message: LineMessage,
        line_user: Optional[LineUser] = None,
        request: Optional[Request] = None
    ):
        """Log when a LINE message is received from a user"""
        extra_data = {
            "line_user_id": line_message.user_id,
            "message_id": line_message.id,
            "message_type": line_message.message_type,
            "content_length": len(line_message.message_text) if line_message.message_text else 0,
            "reply_token": line_message.reply_token,
            "has_sticker": bool(line_message.sticker_id),
            "sticker_id": line_message.sticker_id,
            "platform": "LINE"
        }
        
        # Add user info if available
        if line_user:
            extra_data.update({
                "display_name": line_user.display_name,
                "user_status": line_user.status_message
            })
        
        # Add message preview if it's text and not sensitive
        if line_message.message_text and not _is_sensitive_content(line_message.message_text):
            preview = line_message.message_text[:100]
            if len(line_message.message_text) > 100:
                preview += "..."
            extra_data["message_preview"] = preview
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.CHAT_MESSAGE,
            message=f"LINE message received from {line_message.user_id}",
            module="line_service",
            function_name="receive_message",
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_line_message_sent(
        db: Session,
        line_user_id: str,
        message_content: str,
        message_type: str = "text",
        reply_token: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log when a message is sent to LINE user"""
        extra_data = {
            "line_user_id": line_user_id,
            "message_type": message_type,
            "content_length": len(message_content),
            "reply_token": reply_token,
            "success": success,
            "platform": "LINE",
            "direction": "outbound"
        }
        
        if error_message:
            extra_data["error_message"] = error_message
        
        # Add message preview if successful and not sensitive
        if success and not _is_sensitive_content(message_content):
            preview = message_content[:100]
            if len(message_content) > 100:
                preview += "..."
            extra_data["message_preview"] = preview
        
        level = LogLevel.INFO if success else LogLevel.ERROR
        message = f"LINE message {'sent to' if success else 'failed to send to'} {line_user_id}"
        
        return LoggingService.log_system_event(
            db=db,
            level=level,
            category=LogCategory.CHAT_MESSAGE,
            message=message,
            module="line_service",
            function_name="send_message",
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_line_webhook_event(
        db: Session,
        event_type: str,
        line_user_id: str,
        event_data: Dict[str, Any],
        processing_success: bool = True,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log LINE webhook events (follow, unfollow, join, leave, etc.)"""
        extra_data = {
            "line_user_id": line_user_id,
            "event_type": event_type,
            "processing_success": processing_success,
            "platform": "LINE",
            "webhook_data": event_data
        }
        
        if error_message:
            extra_data["error_message"] = error_message
        
        level = LogLevel.INFO if processing_success else LogLevel.ERROR
        message = f"LINE webhook event: {event_type} from {line_user_id}"
        
        return LoggingService.log_system_event(
            db=db,
            level=level,
            category=LogCategory.CHAT_EVENT,
            message=message,
            module="line_webhook",
            function_name="process_webhook",
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_line_user_interaction(
        db: Session,
        line_user_id: str,
        interaction_type: str,  # follow, unfollow, block, typing, etc.
        line_user: Optional[LineUser] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log LINE user interactions and status changes"""
        extra_data = {
            "line_user_id": line_user_id,
            "interaction_type": interaction_type,
            "platform": "LINE",
            **(additional_data or {})
        }
        
        if line_user:
            extra_data.update({
                "display_name": line_user.display_name,
                "status_message": line_user.status_message,
                "has_picture": bool(line_user.picture_url)
            })
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            message=f"LINE user interaction: {interaction_type} by {line_user_id}",
            module="line_service",
            function_name=f"handle_{interaction_type}",
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_line_sticker_sent(
        db: Session,
        line_user_id: str,
        sticker_id: str,
        sticker_package_id: Optional[str] = None,
        direction: str = "inbound",  # inbound or outbound
        request: Optional[Request] = None
    ):
        """Log LINE sticker messages"""
        extra_data = {
            "line_user_id": line_user_id,
            "sticker_id": sticker_id,
            "sticker_package_id": sticker_package_id,
            "message_type": "sticker",
            "direction": direction,
            "platform": "LINE"
        }
        
        action = "received from" if direction == "inbound" else "sent to"
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.CHAT_MESSAGE,
            message=f"LINE sticker {action} {line_user_id}",
            module="line_service",
            function_name="handle_sticker",
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_line_rich_menu_action(
        db: Session,
        line_user_id: str,
        action_type: str,
        menu_item: str,
        additional_data: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log LINE rich menu interactions"""
        extra_data = {
            "line_user_id": line_user_id,
            "action_type": action_type,
            "menu_item": menu_item,
            "platform": "LINE",
            "interaction_source": "rich_menu",
            **(additional_data or {})
        }
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            message=f"LINE rich menu action: {action_type} - {menu_item} by {line_user_id}",
            module="line_service",
            function_name="handle_rich_menu",
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_line_api_call(
        db: Session,
        api_endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        line_user_id: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log LINE API calls (sending messages, getting user profile, etc.)"""
        extra_data = {
            "api_endpoint": api_endpoint,
            "method": method,
            "line_user_id": line_user_id,
            "platform": "LINE",
            "api_call": True
        }
        
        if request_data:
            extra_data["request_data"] = request_data
        if error_message:
            extra_data["error_message"] = error_message
        
        # Use API log for LINE API calls
        return LoggingService.log_api_call(
            db=db,
            request_id=f"line_api_{api_endpoint}_{line_user_id}",
            method=method,
            endpoint=f"/line/api{api_endpoint}",
            status_code=status_code,
            response_time_ms=response_time_ms,
            query_params=extra_data,
            error_message=error_message,
            request=request
        )
    
    @staticmethod
    def log_line_bot_health(
        db: Session,
        status: str,  # healthy, unhealthy, degraded
        check_type: str,  # webhook, api, database
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log LINE bot health check results"""
        extra_data = {
            "health_status": status,
            "check_type": check_type,
            "platform": "LINE",
            "health_check": True,
            **(details or {})
        }
        
        level = LogLevel.INFO if status == "healthy" else LogLevel.WARNING if status == "degraded" else LogLevel.ERROR
        
        return LoggingService.log_system_event(
            db=db,
            level=level,
            category=LogCategory.SYSTEM,
            message=f"LINE bot health check: {status} - {check_type}",
            module="line_health",
            function_name="health_check",
            extra_data=extra_data,
            request=request
        )

def _is_sensitive_content(content: str) -> bool:
    """Check if message content contains sensitive information"""
    if not content:
        return False
        
    sensitive_keywords = [
        "password", "token", "secret", "key", "credential",
        "ssn", "social security", "credit card", "bank account",
        "api_key", "access_token", "refresh_token"
    ]
    
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in sensitive_keywords) 