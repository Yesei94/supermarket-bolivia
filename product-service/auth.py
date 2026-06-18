
from fastapi import Header, HTTPException
from jose import jwt, JWTError

SECRET_KEY = "supermarket-secret-demo"
ALGORITHM = "HS256"

def verify_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token JWT requerido")
    token = authorization.replace("Bearer ", "")
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
