from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from auth import verify_token

app = FastAPI(title="Customer Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///customer.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    document = Column(String)
    points = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

class CustomerRequest(BaseModel):
    name: str
    document: str = ""

class PointsRequest(BaseModel):
    points: int

@app.get("/health")
def health():
    return {"status": "ok", "service": "customer-service"}

@app.post("/customers")
def create_customer(request: CustomerRequest, token=Depends(verify_token)):
    db = SessionLocal()
    obj = Customer(name=request.name, document=request.document, points=0)
    db.add(obj); db.commit(); db.refresh(obj); db.close()
    return {"event": "CustomerCreated", "customer": obj}

@app.get("/customers")
def list_customers(token=Depends(verify_token)):
    db = SessionLocal(); data = db.query(Customer).all(); db.close(); return data

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, token=Depends(verify_token)):
    db = SessionLocal(); obj = db.query(Customer).filter(Customer.id == customer_id).first(); db.close()
    if not obj: raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return obj

@app.post("/customers/{customer_id}/points")
def assign_points(customer_id: int, request: PointsRequest, token=Depends(verify_token)):
    db = SessionLocal(); obj = db.query(Customer).filter(Customer.id == customer_id).first()
    if not obj:
        db.close(); raise HTTPException(status_code=404, detail="Cliente no encontrado")
    obj.points += request.points
    db.commit(); db.refresh(obj); db.close()
    return {"event": "PointsAssigned", "customer": obj}

@app.get("/customers/{customer_id}/history")
def history(customer_id: int, token=Depends(verify_token)):
    return {"customer_id": customer_id, "history": ["Cliente registrado", "Puntos asignados por venta"]}
