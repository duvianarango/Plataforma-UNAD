from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import esquemas, crud_evaluaciones
from .dependencias import obtener_db, obtener_usuario_actual,requerir_docente, requerir_estudiante
from .modelos import Usuario


router = APIRouter()

# @router.post("/evaluaciones/", response_model=esquemas.EvaluacionRespuesta)
# def crear_eval(
#     datos: esquemas.EvaluacionCrear,
#     db: Session = Depends(obtener_db),
#     docente = Depends(requerir_docente)
# ):
#     return crud_evaluaciones.crear_evaluacion(db, datos)

# @router.get("/evaluaciones/curso/{curso_id}", response_model=list[esquemas.EvaluacionRespuesta])
# def listar_evaluaciones(curso_id: int, db: Session = Depends(obtener_db)):
#     return crud_evaluaciones.obtener_evaluaciones_por_curso(db, curso_id)

# @router.post("/responder/", response_model=esquemas.RespuestaEstudiante)
# def responder_evaluacion(
#     datos: esquemas.ResponderEvaluacion,
#     db: Session = Depends(obtener_db),
#     estudiante: Usuario = Depends(requerir_estudiante)
# ):
#     return crud_evaluaciones.guardar_respuesta(db, datos, estudiante.id)

# @router.get("/mis_respuestas/", response_model=list[esquemas.RespuestaEstudiante])
# def ver_mis_respuestas(
#     db: Session = Depends(obtener_db),
#     usuario: Usuario = Depends(obtener_usuario_actual)
# ):
#     return crud_evaluaciones.obtener_respuestas_usuario(db, usuario.id)
