from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from . import modelos, db, auth
from .auth import create_access_token

router = APIRouter()

def obtener_db():
    db_local = db.SessionLocal()
    try:
        yield db_local
    finally:
        db_local.close()

@router.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(obtener_db)):
    usuario = db.query(modelos.Usuario).filter_by(correo=form_data.username).first()
    if not usuario or not auth.verificar_contrasena(form_data.password, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
     # Crear token para autenticación
    token = create_access_token({"sub": usuario.correo})

    print(f"Token generado: {token}")

    # Redirigir al dashboard según el rol del usuario
    if usuario.rol == 'Docente':
        response = RedirectResponse(url="/dashboard-docente", status_code=303)
    else:
        response = RedirectResponse(url="/dashboard-estudiante", status_code=303)

    response.set_cookie(key="access_token", value=token, httponly=True)  # Guarda el token en una cookie segura
    return response