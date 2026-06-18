from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI(title="Auth Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = "supermarket-secret-demo"
ALGORITHM = "HS256"

users = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "cajero": {"password": "cajero123", "role": "CAJERO"},
    "supervisor": {"password": "supervisor123", "role": "SUPERVISOR"}
}

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}

@app.post("/auth/login")
def login(request: LoginRequest):
    user = users.get(request.username)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    payload = {
        "sub": request.username,
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}
