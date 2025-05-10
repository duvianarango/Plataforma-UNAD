from datetime import datetime
from sqlalchemy.orm import Session
from . import modelos, esquemas
from sqlalchemy.orm import joinedload


def crear_foro(db: Session, foro_data: esquemas.ForoCreate):
    nuevo_foro = modelos.Foro(**foro_data.dict())
    db.add(nuevo_foro)
    db.commit()
    db.refresh(nuevo_foro)
    return nuevo_foro

def obtener_foros(db: Session):
    return db.query(modelos.Foro).all()

def obtener_foro(db: Session, foro_id: int):
    return db.query(modelos.Foro).filter(modelos.Foro.id == foro_id).first()

def obtener_foros_por_curso(db: Session, curso_id: int):
    return db.query(modelos.Foro).filter(modelos.Foro.curso_id == curso_id).all()

def crear_mensaje(db: Session, contenido: str, curso_id: int, usuario_id: int):
    mensaje = modelos.MensajeForo(
        contenido=contenido,
        curso_id=curso_id,
        usuario_id=usuario_id
    )
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)
    return mensaje

def obtener_mensajes_curso(db: Session, curso_id: int):
    return db.query(modelos.MensajeForo).filter_by(curso_id=curso_id).order_by(modelos.MensajeForo.fecha.desc()).all()

def obtener_foros_por_usuario(db: Session, usuario_id: int):
    return db.query(modelos.Foro).filter(modelos.Foro.usuario_id == usuario_id).all()


def crear_mensaje(db: Session, contenido: str, foro_id: int, usuario_id: int):
    nuevo_mensaje = modelos.MensajeForo(
        contenido=contenido,
        fecha=datetime.utcnow(),
        foro_id=foro_id,
        usuario_id=usuario_id
    )
    db.add(nuevo_mensaje)
    db.commit()
    db.refresh(nuevo_mensaje)
    return nuevo_mensaje

# Obtener todos los mensajes de un foro
def obtener_mensajes(db: Session, foro_id: int, skip: int = 0, limit: int = 100):
    return db.query(modelos.MensajeForo).filter(modelos.MensajeForo.foro_id == foro_id).offset(skip).limit(limit).all()

# Obtener un mensaje por ID
def obtener_mensaje(db: Session, mensaje_id: int):
    return db.query(modelos.MensajeForo).filter(modelos.MensajeForo.id == mensaje_id).first()

# crud_foro.py

def obtener_mensajes_por_foro(db: Session, foro_id: int):
    return (
        db.query(modelos.MensajeForo)
        .filter(modelos.MensajeForo.foro_id == foro_id)
        .options(joinedload(modelos.MensajeForo.usuario))
        .order_by(modelos.MensajeForo.fecha.asc())
        .all()
    )

def obtener_cursos_con_usuario(db: Session, usuario_id: int):
    usuario = db.query(modelos.Usuario).filter(modelos.Usuario.id == usuario_id).first()
    if usuario:
        return usuario.cursos_asignados
    return []
