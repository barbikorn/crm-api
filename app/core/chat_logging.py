from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request

from app.core.logging import LoggingService
from app.models.log import LogLevel, LogCategory

class ChatLoggingService:
    """Specialized logging service for chat functionality"""
    
    @staticmethod
    def log_message_sent(
        db: Session,
        sender_id: int,
        chat_id: str,
        message_id: str,
        message_content: str,
        message_type: str = "text",
        recipient_id: Optional[int] = None,
        request: Optional[Request] = None
    ):
        """Log when a chat message is sent"""
        extra_data = {
            "message_id": message_id,
            "chat_id": chat_id,
            "message_type": message_type,
            "content_length": len(message_content),
            "recipient_id": recipient_id
        }
        
        # Only log content if it's not sensitive (you can add content filtering here)
        if not _is_sensitive_content(message_content):
            extra_data["message_preview"] = message_content[:100] + "..." if len(message_content) > 100 else message_content
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.CHAT_MESSAGE,
            message=f"Message sent in chat {chat_id}",
            module="chat_service",
            function_name="send_message",
            user_id=sender_id,
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_message_received(
        db: Session,
        recipient_id: int,
        chat_id: str,
        message_id: str,
        sender_id: int,
        request: Optional[Request] = None
    ):
        """Log when a chat message is received"""
        extra_data = {
            "message_id": message_id,
            "chat_id": chat_id,
            "sender_id": sender_id,
            "action": "message_received"
        }
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.CHAT_MESSAGE,
            message=f"Message received in chat {chat_id}",
            module="chat_service",
            function_name="receive_message",
            user_id=recipient_id,
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_chat_event(
        db: Session,
        user_id: int,
        chat_id: str,
        event_type: str,  # join, leave, create, delete, mute, etc.
        additional_data: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log chat events like joining, leaving, creating chats"""
        extra_data = {
            "chat_id": chat_id,
            "event_type": event_type,
            **(additional_data or {})
        }
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.CHAT_EVENT,
            message=f"Chat event: {event_type} in chat {chat_id}",
            module="chat_service",
            function_name=f"chat_{event_type}",
            user_id=user_id,
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_message_moderation(
        db: Session,
        moderator_id: int,
        chat_id: str,
        message_id: str,
        action: str,  # delete, flag, warn, etc.
        reason: str,
        target_user_id: Optional[int] = None,
        request: Optional[Request] = None
    ):
        """Log chat moderation actions"""
        extra_data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "moderation_action": action,
            "reason": reason,
            "target_user_id": target_user_id
        }
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.WARNING,
            category=LogCategory.CHAT_MODERATION,
            message=f"Moderation action: {action} on message {message_id}",
            module="chat_moderation",
            function_name=f"moderate_{action}",
            user_id=moderator_id,
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_file_share(
        db: Session,
        user_id: int,
        chat_id: str,
        file_name: str,
        file_size: int,
        file_type: str,
        request: Optional[Request] = None
    ):
        """Log file sharing in chat"""
        extra_data = {
            "chat_id": chat_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "action": "file_shared"
        }
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.CHAT_MESSAGE,
            message=f"File shared in chat {chat_id}: {file_name}",
            module="chat_service",
            function_name="share_file",
            user_id=user_id,
            extra_data=extra_data,
            request=request
        )
    
    @staticmethod
    def log_chat_search(
        db: Session,
        user_id: int,
        chat_id: str,
        search_query: str,
        results_count: int,
        request: Optional[Request] = None
    ):
        """Log chat search activities"""
        extra_data = {
            "chat_id": chat_id,
            "search_query": search_query,
            "results_count": results_count,
            "action": "search_messages"
        }
        
        return LoggingService.log_system_event(
            db=db,
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            message=f"Message search in chat {chat_id}",
            module="chat_service",
            function_name="search_messages",
            user_id=user_id,
            extra_data=extra_data,
            request=request
        )

def _is_sensitive_content(content: str) -> bool:
    """Check if message content contains sensitive information"""
    sensitive_keywords = [
        "password", "token", "secret", "key", "credential",
        "ssn", "social security", "credit card", "bank account"
    ]
    
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in sensitive_keywords) 