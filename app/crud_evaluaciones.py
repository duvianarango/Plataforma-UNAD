from sqlalchemy.orm import Session
from . import modelos, esquemas

def crear_evaluacion(db: Session, evaluacion: esquemas.EvaluacionCreate):
    db_evaluacion = modelos.Evaluacion(**evaluacion.dict())
    db.add(db_evaluacion)
    db.commit()
    db.refresh(db_evaluacion)
    return db_evaluacion

def obtener_evaluaciones_por_curso(db: Session, curso_id: int):
    return db.query(modelos.Evaluacion).filter_by(curso_id=curso_id).all()

def guardar_respuesta(db: Session, datos: esquemas.ResponderEvaluacion, usuario_id: int):
    respuesta = modelos.Respuesta(
        evaluacion_id=datos.evaluacion_id,
        usuario_id=usuario_id,
        nota=datos.nota
    )
    db.add(respuesta)
    db.commit()
    db.refresh(respuesta)
    return respuesta

def obtener_respuestas_usuario(db: Session, usuario_id: int):
    return db.query(modelos.Respuesta).filter_by(usuario_id=usuario_id).all()

def editar_evaluacion(db: Session, evaluacion_id: int, usuario_id: int, datos_actualizados: esquemas.EvaluacionUpdate):
    evaluacion = db.query(modelos.Evaluacion).filter(
        modelos.Evaluacion.id == evaluacion_id,
        modelos.Evaluacion.usuario_id == usuario_id  # Solo el creador puede editar
    ).first()

    if not evaluacion:
        print(f"Evaluación no encontrada o usuario no autorizado (ID Evaluación: {evaluacion_id}, Usuario: {usuario_id})")
        return None

    # Actualizar campos, sin modificar el usuario_id
    evaluacion.titulo = datos_actualizados.titulo
    evaluacion.descripcion = datos_actualizados.descripcion
    evaluacion.fecha_inicio = datos_actualizados.fecha_inicio
    evaluacion.fecha_limite = datos_actualizados.fecha_limite
    evaluacion.curso_id = datos_actualizados.curso_id
    evaluacion.puntaje_maximo = datos_actualizados.puntaje_maximo
    evaluacion.tipo = datos_actualizados.tipo
    evaluacion.archivo_entrega = datos_actualizados.archivo_entrega
    evaluacion.url_entrega = datos_actualizados.url_entrega

    db.commit()
    db.refresh(evaluacion)
    return evaluacion

def obtener_evaluacion(db: Session, evaluacion_id: int, usuario_id: int):
    """
    Obtiene una evaluación por su ID.
    Valida si el usuario tiene acceso a la evaluación.
    """
    evaluacion = db.query(modelos.Evaluacion).filter(
        modelos.Evaluacion.id == evaluacion_id,
        modelos.Evaluacion.usuario_id == usuario_id  # Asegúrate de que el usuario tenga acceso
    ).first()

    return evaluacion


def obtener_evaluaciones_de_cursos_asignados(db: Session, usuario_id: int):
    usuario = db.query(modelos.Usuario).filter_by(id=usuario_id).first()

    if not usuario or not usuario.cursos_asignados:
        return []

    evaluaciones = []
    for curso in usuario.cursos_asignados:
        evaluaciones_curso = db.query(modelos.Evaluacion).filter_by(curso_id=curso.id).all()
        evaluaciones.extend(evaluaciones_curso)
    return evaluaciones
