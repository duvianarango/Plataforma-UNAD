from sqlalchemy.orm import Session
from . import modelos, esquemas, auth
from .modelos import Curso, Usuario, usuarios_cursos

def crear_usuario(db: Session, datos: esquemas.UsuarioCrear):
    usuario_existente = db.query(modelos.Usuario).filter(modelos.Usuario.correo == datos.correo).first()
    if usuario_existente:
        raise ValueError("El correo ya está registrado")

    nuevo_usuario = modelos.Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        contrasena=auth.encriptar_contrasena(datos.contrasena),  # <<< ENCRIPTAR AQUÍ
        rol=datos.rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario



def obtener_usuario_por_correo(db: Session, correo: str):
    return db.query(modelos.Usuario).filter(modelos.Usuario.correo == correo).first()

def autenticar_usuario(db: Session, correo: str, contrasena: str):
    usuario = obtener_usuario_por_correo(db, correo)
    if not usuario:
        return None
    if not auth.verificar_contrasena(contrasena, usuario.contrasena):
        return None
    return usuario

def obtener_cursos_asignados(db: Session, usuario_id: int):
    cursos = db.query(Curso)\
        .join(usuarios_cursos, Curso.id == usuarios_cursos.c.curso_id)\
        .filter(usuarios_cursos.c.usuario_id == usuario_id)\
        .all()
    return cursos