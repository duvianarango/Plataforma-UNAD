from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .dependencias import obtener_db, obtener_usuario_actual
from . import esquemas, crud_asignaciones
from .modelos import Usuario

router = APIRouter()

@router.post("/asignar_curso/")
def asignar_curso(
    datos: esquemas.AsignarCurso,
    db: Session = Depends(obtener_db),
    usuario: Usuario = Depends(obtener_usuario_actual)
):
    exito = crud_asignaciones.asignar_usuario_a_curso(
        db, usuario, datos.curso_id, datos.es_docente
    )
    if not exito:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return {"mensaje": "Curso asignado correctamente"}

@router.get("/mis_cursos/", response_model=list[esquemas.CursoAsignadoRespuesta])
def ver_cursos(db: Session = Depends(obtener_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    return crud_asignaciones.obtener_cursos_asignados(db, usuario)
