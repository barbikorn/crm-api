from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class LineMessage(Base):
    __tablename__ = "line_message"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message_text = Column(String)
    message_type = Column(String, default='text')
    sticker_id = Column(String, nullable=True)
    sticker_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reply_token = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)

    def __str__(self):
        return f"{self.user_id}: {self.message_text[:30]}"

class LineUser(Base):
    __tablename__ = "line_user"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    display_name = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)
    status_message = Column(String, nullable=True)
    last_typing = Column(DateTime, nullable=True)

    def __str__(self):
        return self.display_name or self.user_id 