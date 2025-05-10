from sqlalchemy.orm import Session
from app.modelos import Curso
from . import modelos, esquemas
from app.db import SessionLocal


def crear_curso(db: Session, datos: esquemas.CursoCrear, creador_id: int):
    nuevo = modelos.Curso(
        titulo=datos.titulo,
        codigo=datos.codigo,
        departamento=datos.departamento,
        descripcion=datos.descripcion,
        creditos=datos.creditos,
        horas=datos.horas,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        cupo_maximo=datos.cupo_maximo,
        creador_id=creador_id
    )
    try:
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)

        # 🔽 Aquí registramos al creador como docente del curso
        insertar = modelos.usuarios_cursos.insert().values(
            usuario_id=creador_id,
            curso_id=nuevo.id,
            es_docente=True
        )
        db.execute(insertar)
        db.commit()

        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": f"Error al crear el curso: {str(e)}"}


def obtener_curso(db: Session, curso_id: int, docente_id: int):
    return db.query(modelos.Curso).join(modelos.usuarios_cursos).filter(
        modelos.usuarios_cursos.c.curso_id == curso_id,
        modelos.usuarios_cursos.c.usuario_id == docente_id,
        modelos.usuarios_cursos.c.es_docente == True
    ).first()

def obtener_curso_por_id(db: Session, curso_id: int):
    return db.query(modelos.Curso).join(modelos.usuarios_cursos).filter(
        modelos.usuarios_cursos.c.curso_id == curso_id
    ).first()

def actualizar_curso(db: Session, curso_id: int, docente_id: int, datos: esquemas.CursoCrear):
    # Obtener el curso desde la base de datos
    curso = obtener_curso(db, curso_id, docente_id)
    
    if curso:
        # Actualizar los campos del curso con los nuevos datos
        curso.titulo = datos.titulo
        curso.codigo = datos.codigo
        curso.departamento = datos.departamento
        curso.descripcion = datos.descripcion
        curso.creditos = datos.creditos
        curso.horas = datos.horas
        curso.fecha_inicio = datos.fecha_inicio
        curso.fecha_fin = datos.fecha_fin
        curso.cupo_maximo = datos.cupo_maximo
        
        # Guardar los cambios en la base de datos
        db.commit()
        db.refresh(curso)
        return curso
    
    return None  # Retornar None si no se encuentra o no se autoriza

def eliminar_curso(db: Session, curso_id: int, docente_id: int):
    curso = obtener_curso(db, curso_id, docente_id)
    if curso:
        db.delete(curso)
        db.commit()
        return {"mensaje": "Curso eliminado exitosamente"}
    return {"error": "Curso no encontrado o no autorizado"}

def obtener_todos_los_cursos(db: Session):
    return db.query(modelos.Curso).all()

def obtener_cursos_asignados(db: Session, docente_id: int):
    return db.query(modelos.Curso).join(modelos.usuarios_cursos).filter(
        modelos.usuarios_cursos.c.usuario_id == docente_id,
        modelos.usuarios_cursos.c.es_docente == True
    ).all()

def obtener_cursos_asignados_estudiante(db: Session, usuario_id: int):
    usuario = db.query(modelos.Usuario).filter(modelos.Usuario.id == usuario_id).first()
    if not usuario:
        return []
    return usuario.cursos_asignados
