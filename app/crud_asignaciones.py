from sqlalchemy.orm import Session
from . import modelos

def asignar_usuario_a_curso(db: Session, usuario, curso_id: int, es_docente: bool):
    curso = db.query(modelos.Curso).filter_by(id=curso_id).first()
    if curso:
        db.execute(
            modelos.usuarios_cursos.insert().values(
                usuario_id=usuario.id,
                curso_id=curso.id,
                es_docente=es_docente
            )
        )
        db.commit()
        return True
    return False

def obtener_cursos_asignados(db: Session, usuario):
    return usuario.cursos_asignados
