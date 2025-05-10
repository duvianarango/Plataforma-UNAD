from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from . import esquemas, crud_cursos
from .dependencias import obtener_db, requerir_docente
from .modelos import Usuario

router = APIRouter()

@router.post("/cursos/", response_model=esquemas.CursoRespuesta)
def crear_curso(
    datos: esquemas.CursoCrear,
    db: Session = Depends(obtener_db),
    docente: Usuario = Depends(requerir_docente)
):
    curso = crud_cursos.crear_curso(db, datos, docente.id)
    if isinstance(curso, dict) and "error" in curso:
        raise HTTPException(status_code=400, detail=curso["error"])
    return curso

@router.get("/cursos/", response_model=list[esquemas.CursoRespuesta])
def listar_cursos(db: Session = Depends(obtener_db)):
    return crud_cursos.obtener_todos_los_cursos()

@router.get("/cursos/{curso_id}", response_model=esquemas.CursoRespuesta)
def obtener_un_curso(
    curso_id: int,
    db: Session = Depends(obtener_db),
    docente: Usuario = Depends(requerir_docente)
):
    curso = crud_cursos.obtener_curso(db, curso_id, docente.id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado o no autorizado")
    return curso

@router.put("/cursos/{curso_id}", response_model=esquemas.CursoRespuesta)
def actualizar_curso(
    curso_id: int,
    datos: esquemas.CursoCrear,
    db: Session = Depends(obtener_db),
    docente: Usuario = Depends(requerir_docente)
):
    curso = crud_cursos.actualizar_curso(db, curso_id, docente.id, datos)
    if isinstance(curso, dict) and "error" in curso:
        raise HTTPException(status_code=404, detail=curso["error"])
    return curso

@router.delete("/cursos/{curso_id}")
def eliminar_curso(
    curso_id: int,
    db: Session = Depends(obtener_db),
    docente: Usuario = Depends(requerir_docente)
):
    resultado = crud_cursos.eliminar_curso(db, curso_id, docente.id)
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return {"mensaje": "Curso eliminado correctamente"}