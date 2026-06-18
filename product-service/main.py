from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from auth import verify_token
import openpyxl

app = FastAPI(title="Product Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///product.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    category = Column(String)
    brand = Column(String)
    barcode = Column(String)
    base_price = Column(Float)
    status = Column(String, default="ACTIVE")

Base.metadata.create_all(bind=engine)

class ProductRequest(BaseModel):
    code: str
    name: str
    category: str = "General"
    brand: str = "Sin marca"
    barcode: str = ""
    base_price: float
    status: str = "ACTIVE"

@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}

@app.post("/products")
def create_product(request: ProductRequest, token=Depends(verify_token)):
    db = SessionLocal()
    obj = Product(**request.model_dump())
    db.add(obj); db.commit(); db.refresh(obj); db.close()
    return {"event": "ProductCreated", "product": obj}

@app.post("/products/loadExcel")
async def load_products_excel(file: UploadFile = File(...), token=Depends(verify_token)):
    db = SessionLocal()
    created = 0
    updated = 0
    errors = []
    try:
        wb = openpyxl.load_workbook(file.file)
        sheet = wb.active
        for index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row or all(value is None for value in row):
                continue
            try:
                code, name, category, brand, barcode, base_price, status = (list(row) + [None] * 7)[:7]
                code = str(code or "").strip().upper()
                name = str(name or "").strip().upper()
                category = str(category or "General").strip()
                brand = str(brand or "Sin marca").strip()
                barcode = str(barcode or "").strip()
                status = str(status or "ACTIVE").strip().upper()
                if not code or not name:
                    raise ValueError("code y name son obligatorios")
                base_price = float(base_price)

                product = db.query(Product).filter(Product.code == code).first()
                if product:
                    product.name = name
                    product.category = category
                    product.brand = brand
                    product.barcode = barcode
                    product.base_price = base_price
                    product.status = status
                    updated += 1
                else:
                    db.add(Product(code=code, name=name, category=category, brand=brand, barcode=barcode, base_price=base_price, status=status))
                    created += 1
            except Exception as exc:
                errors.append({"row": index, "error": str(exc)})
        db.commit()
        return {"event": "ProductsExcelLoaded", "created": created, "updated": updated, "errors": errors}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        db.close()

@app.get("/products")
def list_products(token=Depends(verify_token)):
    db = SessionLocal(); data = db.query(Product).all(); db.close(); return data

@app.get("/products/{product_id}")
def get_product(product_id: int, token=Depends(verify_token)):
    db = SessionLocal(); obj = db.query(Product).filter(Product.id == product_id).first(); db.close()
    if not obj: raise HTTPException(status_code=404, detail="Producto no encontrado")
    return obj

@app.put("/products/{product_id}")
def update_product(product_id: int, request: ProductRequest, token=Depends(verify_token)):
    db = SessionLocal(); obj = db.query(Product).filter(Product.id == product_id).first()
    if not obj:
        db.close(); raise HTTPException(status_code=404, detail="Producto no encontrado")
    for k,v in request.model_dump().items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); db.close()
    return {"event": "ProductUpdated", "product": obj}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, token=Depends(verify_token)):
    db = SessionLocal(); obj = db.query(Product).filter(Product.id == product_id).first()
    if not obj:
        db.close(); raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(obj); db.commit(); db.close()
    return {"event": "ProductDeleted", "product_id": product_id}

@app.get("/categories")
def categories(token=Depends(verify_token)):
    return ["Lácteos", "Abarrotes", "Bebidas", "Limpieza", "Carnes", "Panadería"]
