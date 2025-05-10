from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import esquemas, crud_usuarios, db
from .db import SessionLocal
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi import Request


router = APIRouter()

def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/usuarios/")
def crear_usuario(usuario: esquemas.UsuarioCrear, db: Session = Depends(obtener_db)):
    try:
        crud_usuarios.crear_usuario(db, usuario)
        # Redirige al formulario de registro con un mensaje de éxito
        return RedirectResponse(url="/registro?mensaje=Usuario creado correctamente", status_code=303)
    except ValueError as e:
        # Si hay error, redirige también pero con el mensaje de error
        return RedirectResponse(url=f"/registro?mensaje={str(e)}", status_code=303)