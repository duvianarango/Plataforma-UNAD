from sqlalchemy import Column, Float, Integer, String, ForeignKey, Table, Boolean, Date, Text
from sqlalchemy.orm import relationship
from .db import Base
from sqlalchemy import DateTime
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True, index=True)
    contrasena = Column(String(200))
    rol = Column(String(20))  # nuevo campo

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100))
    codigo = Column(String(20), unique=True)  # Nuevo campo: Código del curso
    departamento = Column(String(50))  # Nuevo campo: Departamento
    descripcion = Column(String(255))  # Descripción
    creditos = Column(Integer)  # Nuevo campo: Créditos
    horas = Column(Integer)  # Horas
    fecha_inicio = Column(Date)  # Fecha de inicio
    fecha_fin = Column(Date)  # Fecha de fin
    cupo_maximo = Column(Integer)  # Nuevo campo: Cupo máximo
    creador_id = Column(Integer, ForeignKey("usuarios.id"))

    creador = relationship("Usuario", backref="cursos")



usuarios_cursos = Table(
    "usuarios_cursos",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id")),
    Column("curso_id", Integer, ForeignKey("cursos.id")),
    Column("es_docente", Boolean, default=False)
)

# Relación en Usuario
Usuario.cursos_asignados = relationship(
    "Curso",
    secondary=usuarios_cursos,
    back_populates="usuarios"
)

# Relación en Curso
Curso.usuarios = relationship(
    "Usuario",
    secondary=usuarios_cursos,
    back_populates="cursos_asignados"
)
class Material(Base):
    __tablename__ = "materiales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    tipo = Column(String(50))
    archivo = Column(String(255))  # ruta del archivo
    curso_id = Column(Integer, ForeignKey("cursos.id"))

    curso = relationship("Curso", backref="materiales")

class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    fecha_inicio = Column(Date)
    fecha_limite = Column(Date)
    curso_id = Column(Integer, ForeignKey("cursos.id"))  # si tienes cursos relacionados
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    puntaje_maximo = Column(Integer)
    tipo = Column(String(50))  # 'examen', 'tarea' o 'proyecto'
    archivo_entrega = Column(String(255), nullable=True)  # Especificamos la longitud de 255 caracteres
    url_entrega = Column(String(255), nullable=True)  # Especificamos la longitud de 255 caracteres

    curso = relationship("Curso", backref="evaluaciones")
    usuario = relationship("Usuario", backref="evaluaciones")

class Respuesta(Base):
    __tablename__ = "respuestas"

    id = Column(Integer, primary_key=True, index=True)
    evaluacion_id = Column(Integer, ForeignKey("evaluaciones.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    nota = Column(Integer)

    evaluacion = relationship("Evaluacion", backref="respuestas")
    usuario = relationship("Usuario", backref="respuestas")


class Foro(Base):
    __tablename__ = "foros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    contenido = Column(String(500), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    curso_id = Column(Integer, ForeignKey("cursos.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    curso = relationship("Curso", backref="foros")
    usuario = relationship("Usuario", backref="foros")

class MensajeForo(Base):
    __tablename__ = "mensajes_foro"

    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text)
    fecha =  Column(DateTime, default=datetime.now)
    foro_id = Column(Integer, ForeignKey("foros.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    foro = relationship("Foro", backref="mensajes_foro")
    usuario = relationship("Usuario", backref="mensajes_foro")