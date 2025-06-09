from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LineMessageBase(BaseModel):
    user_id: str
    message_text: str
    message_type: Optional[str] = 'text'
    sticker_id: Optional[str] = None
    sticker_url: Optional[str] = None
    reply_token: Optional[str] = None
    is_read: Optional[bool] = False

class LineMessageCreate(LineMessageBase):
    pass

class LineMessageOut(LineMessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class LineUserBase(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    status_message: Optional[str] = None
    last_typing: Optional[datetime] = None

class LineUserCreate(LineUserBase):
    pass

class LineUserOut(LineUserBase):
    id: int

    class Config:
        from_attributes = True