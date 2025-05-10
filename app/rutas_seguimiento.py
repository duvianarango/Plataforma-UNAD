from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .dependencias import obtener_db, obtener_usuario_actual
from .crud_seguimiento import obtener_resumen_estudiante
from .modelos import Usuario

router = APIRouter()

@router.get("/mi_progreso/")
def ver_progreso(
    db: Session = Depends(obtener_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    return obtener_resumen_estudiante(db, usuario.id)
