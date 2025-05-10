from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import db, modelos
from .config import SECRET_KEY, ALGORITHM
from .modelos import Usuario
from .auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verificar_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = decode_access_token(token)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def obtener_db():
    db_local = db.SessionLocal()
    try:
        yield db_local
    finally:
        db_local.close()

def obtener_usuario_actual(request: Request, db: Session = Depends(obtener_db)):
    token = request.cookies.get("access_token")
    #print("TOKEN RECIBIDO:", token)  # 👈 Verifica si llega el token

    if token is None or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no encontrado en cookies")

    token = token.split(" ")[1]  # Quitamos el 'Bearer '

    try:
        payload = decode_access_token(token)
        user = db.query(Usuario).filter_by(correo=payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return user
    except Exception as e:
        print("ERROR DECODIFICANDO TOKEN:", e)
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def requerir_docente(
    request: Request,
    db: Session = Depends(obtener_db)
    ) -> Usuario:
    # 1. Leer el token JWT enviado en la cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token no encontrado")

    # 2. Decodificar el token
    try:
        payload = decode_access_token(token)
    except Exception as e:
        print(f"Error al decodificar token: {e}")
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # 3. Extraer correo del payload
    correo = payload.get("sub")
    if not correo:
        raise HTTPException(status_code=401, detail="Correo no encontrado en token")

    # 4. Buscar el usuario en la base de datos
    usuario = db.query(Usuario).filter_by(correo=correo).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # 5. Verificar rol de “Docente”
    if usuario.rol != "Docente":
        raise HTTPException(status_code=403, detail="Sólo docentes pueden crear cursos")

    return usuario

def requerir_estudiante(usuario = Depends(obtener_usuario_actual)):
    if usuario.rol != "Estudiante":
        raise HTTPException(status_code=403, detail="Acceso solo para estudiantes")
    return usuario