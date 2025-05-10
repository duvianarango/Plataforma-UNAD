from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, Dict
from fastapi import HTTPException, status

# Clave secreta para firmar el token (puedes generar una más fuerte)
SECRET_KEY = "miclavesecreta123456"
ALGORITHM = "HS256"
EXPIRA_MINUTOS = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encriptar_contrasena(contrasena: str) -> str:
    return pwd_context.hash(contrasena)

def verificar_contrasena(entrada: str, hashed: str) -> bool:
    return pwd_context.verify(entrada, hashed)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=EXPIRA_MINUTOS)) -> str:
    """
    Función para crear un token JWT con una fecha de expiración.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
