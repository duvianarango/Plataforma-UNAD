from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from .dependencias import obtener_usuario_actual, obtener_db
from . import modelos, esquemas
from .main import templates

router = APIRouter()

@router.get("/dashboard-estudiante", response_class=HTMLResponse)
def dashboard_estudiante(
    request: Request,
    db: Session = Depends(obtener_db),
    usuario = Depends(obtener_usuario_actual)
):
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    
    # Obtén los cursos del usuario
    cursos = db.query(modelos.Curso).filter_by(usuario_id=usuario.id).all()
    
    return templates.TemplateResponse("dashboard_estudiante.html", {
        "request": request,
        "usuario": usuario,
        "cursos": cursos
    })

@router.get("/dashboard-docente", response_class=HTMLResponse)
def dashboard_docente(
    request: Request,
    db: Session = Depends(obtener_db),
    usuario = Depends(obtener_usuario_actual)
):
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    
    # Obtén los cursos del docente (suponiendo que la relación de cursos está relacionada por el ID del docente)
    cursos = db.query(modelos.Curso).join(modelos.usuarios_cursos).filter(
    modelos.usuarios_cursos.c.usuario_id == usuario.id,
    modelos.usuarios_cursos.c.es_docente == True
    ).all()
    
    return templates.TemplateResponse("dashboard_docente.html", {
        "request": request,
        "usuario": usuario,
        "cursos": cursos
    })
