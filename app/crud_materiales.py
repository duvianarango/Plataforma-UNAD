from sqlalchemy.orm import Session
from . import modelos

def guardar_material(db: Session, nombre, tipo, ruta, curso_id: int):
    material = modelos.Material(
        nombre=nombre,
        tipo=tipo,
        archivo=ruta,
        curso_id=curso_id
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material

def listar_materiales_curso(db: Session, curso_id: int):
    return db.query(modelos.Material).filter_by(curso_id=curso_id).all()
