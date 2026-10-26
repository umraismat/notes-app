from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.services.database import Base

def now_utc():
    return datetime.now(timezone.utc)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)