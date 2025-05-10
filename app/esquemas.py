from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum

class UsuarioCrear(BaseModel):
    nombre: str
    correo: str
    contrasena: str
    rol: str


class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str

    class Config:
        from_attributes = True

class CursoCrear(BaseModel):
    titulo: str
    codigo: str
    departamento: str
    descripcion: str
    creditos: int
    horas: int
    fecha_inicio: date
    fecha_fin: date
    cupo_maximo: int

class CursoRespuesta(CursoCrear):
    id: int
    creador_id: int

    class Config:
        from_attributes = True
    
class AsignarCurso(BaseModel):
    curso_id: int
    es_docente: bool = False

class CursoAsignadoRespuesta(BaseModel):
    id: int
    titulo: str
    descripcion: str

    class Config:
        from_attributes = True

class MaterialRespuesta(BaseModel):
    id: int
    nombre: str
    tipo: str
    archivo: str
    curso_id: int

    class Config:
        from_attributes = True

class ResponderEvaluacion(BaseModel):
    evaluacion_id: int
    nota: int

class RespuestaEstudiante(BaseModel):
    id: int
    nota: int
    evaluacion_id: int
    usuario_id: int

    class Config:
        from_attributes = True

class MensajeCrear(BaseModel):
    contenido: str
    foro_id: int

class MensajeRespuesta(BaseModel):
    id: int
    contenido: str
    fecha: datetime
    foro_id: int
    usuario_id: int

    class Config:
        from_attributes = True

class ForoCreate(BaseModel):
    titulo: str
    contenido: str
    curso_id: int
    usuario_id: int

class ForoResponse(ForoCreate):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True


class TipoEvaluacion(str, Enum):
    EXAMEN = 'Examen'
    TAREA = 'Tarea'
    PROYECTO = 'Proyecto'

class EvaluacionCreate(BaseModel):
    titulo: str
    descripcion: str
    fecha_inicio: date
    fecha_limite: date
    curso_id: int
    usuario_id: int
    puntaje_maximo: int
    tipo: TipoEvaluacion  # Usar Enum
    archivo_entrega: Optional[str]  # Solo si el tipo no es "Examen"
    url_entrega: Optional[str]  # Solo para tipo "Examen"

class EvaluacionOut(BaseModel):
    id: int
    titulo: str
    descripcion: str
    fecha_inicio: date
    fecha_limite: date
    curso_id: int
    puntaje_maximo: int
    tipo: str
    archivo_entrega: str

    class Config:
        orm_mode = True

class EvaluacionUpdate(BaseModel):
    titulo: str
    descripcion: str
    fecha_inicio: date
    fecha_limite: date
    curso_id: int
    puntaje_maximo: int
    tipo: str
    archivo_entrega: Optional[str] = None
    url_entrega: Optional[str] = None

class EvaluacionRespuesta(BaseModel):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True
