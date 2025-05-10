from sqlalchemy.orm import Session
from . import modelos

def obtener_resumen_estudiante(db: Session, usuario_id: int):
    cursos = db.query(modelos.Curso).join(modelos.usuarios_cursos).filter(
        modelos.usuarios_cursos.c.usuario_id == usuario_id
    ).all()

    respuestas = db.query(modelos.Respuesta).filter_by(usuario_id=usuario_id).all()

    resumen = {
        "cantidad_cursos": len(cursos),
        "cursos": [{"id": c.id, "titulo": c.titulo} for c in cursos],
        "cantidad_evaluaciones": len(respuestas),
        "promedio": (
            sum([r.nota for r in respuestas]) / len(respuestas) if respuestas else 0
        ),
        "respuestas": [
            {"evaluacion_id": r.evaluacion_id, "nota": r.nota}
            for r in respuestas
        ],
    }

    return resumen
