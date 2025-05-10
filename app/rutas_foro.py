from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from . import esquemas, crud_foro
from .dependencias import obtener_db, obtener_usuario_actual
from .modelos import Usuario

router = APIRouter()

@router.post("/foro/", response_model=esquemas.MensajeRespuesta)
def publicar_mensaje(
    datos: esquemas.MensajeCrear,
    db: Session = Depends(obtener_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    return crud_foro.crear_mensaje(db, datos.contenido, datos.curso_id, usuario.id)

