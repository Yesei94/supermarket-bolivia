from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from auth import verify_token

app = FastAPI(title="Notification Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///notification.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    type = Column(String)
    content = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class NotificationRequest(BaseModel):
    customer_id: int
    type: str = "WhatsApp"
    content: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "notification-service"}

@app.post("/notifications")
def create_notification(request: NotificationRequest, token=Depends(verify_token)):
    db = SessionLocal()
    obj = Notification(**request.model_dump())
    db.add(obj); db.commit(); db.refresh(obj); db.close()
    return {"message": "Notificación simulada registrada", "notification": obj}

@app.get("/notifications")
def list_notifications(token=Depends(verify_token)):
    db = SessionLocal(); data = db.query(Notification).all(); db.close(); return data
