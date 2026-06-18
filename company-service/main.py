from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from auth import verify_token

app = FastAPI(title="Company Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///company.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, default="Bolivia")

class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, nullable=False)
    company_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    city = Column(String, default="Bolivia")

Base.metadata.create_all(bind=engine)

class CompanyRequest(BaseModel):
    name: str
    city: str = "Bolivia"

class BranchRequest(BaseModel):
    company_id: int
    name: str
    city: str = "Bolivia"

@app.get("/health")
def health():
    return {"status": "ok", "service": "company-service"}

@app.post("/companies")
def create_company(request: CompanyRequest, token=Depends(verify_token)):
    db = SessionLocal()
    obj = Company(name=request.name, city=request.city)
    db.add(obj); db.commit(); db.refresh(obj); db.close()
    return obj

@app.get("/companies")
def list_companies(token=Depends(verify_token)):
    db = SessionLocal(); data = db.query(Company).all(); db.close(); return data

@app.get("/companies/{company_id}")
def get_company(company_id: int, token=Depends(verify_token)):
    db = SessionLocal(); obj = db.query(Company).filter(Company.id == company_id).first(); db.close()
    if not obj: raise HTTPException(status_code=404, detail="Compañía no encontrada")
    return obj

@app.post("/branches")
def create_branch(request: BranchRequest, token=Depends(verify_token)):
    db = SessionLocal()
    company = db.query(Company).filter(Company.id == request.company_id).first()
    if not company:
        db.close()
        raise HTTPException(status_code=404, detail="Compañía no encontrada")
    obj = Branch(company_id=company.id, company_name=company.name, name=request.name, city=request.city)
    db.add(obj); db.commit(); db.refresh(obj); db.close()
    return obj

@app.get("/branches")
def list_branches(token=Depends(verify_token)):
    db = SessionLocal(); data = db.query(Branch).all(); db.close(); return data

@app.get("/branches/{branch_id}")
def get_branch(branch_id: int, token=Depends(verify_token)):
    db = SessionLocal(); obj = db.query(Branch).filter(Branch.id == branch_id).first(); db.close()
    if not obj: raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return obj
