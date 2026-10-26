from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from app.services.database import get_db
from app.models.note import Note
from app.schemas import NoteCreate, NoteUpdate, NoteOut
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
#from app.services.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from datetime import datetime
from pydantic import BaseModel, ConfigDict

DATABASE_URL = "postgresql+psycopg2://postgres:postgre1234@localhost:5432/notes_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def now_utc():
    return datetime.now(timezone.utc)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=now_utc)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)




class NoteBase(BaseModel):
    title: str
    content: str = ""


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NoteOut(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteOut, status_code=201)
def create_note(data: NoteCreate, db: Session = Depends(get_db)):
    note = Note(**data.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("/", response_model=list[NoteOut])
def list_notes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Note).offset(skip).limit(limit).all()

@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    return note

@router.patch("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, data: NoteUpdate, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(note, k, v)
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    db.delete(note)
    db.commit()

app1 = FastAPI(title="Notes API")
app1.include_router(router)

