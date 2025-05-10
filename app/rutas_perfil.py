from fastapi import APIRouter, Depends
from .dependencias import obtener_usuario_actual
from .esquemas import UsuarioRespuesta
from .modelos import Usuario

router = APIRouter()

@router.get("/perfil/", response_model=UsuarioRespuesta)
def perfil(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    return UsuarioRespuesta(id=usuario_actual.id, nombre=usuario_actual.nombre)
