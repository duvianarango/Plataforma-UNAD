import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from .dependencias import obtener_db
from . import crud_materiales, esquemas

router = APIRouter()
CARPETA = "archivos"

@router.post("/materiales/", response_model=esquemas.MaterialRespuesta)
def subir_material(
    archivo: UploadFile = File(...),
    nombre: str = Form(...),
    tipo: str = Form(...),
    curso_id: int = Form(...),
    db: Session = Depends(obtener_db)
):
    os.makedirs(CARPETA, exist_ok=True)

    ruta_archivo = os.path.join(CARPETA, archivo.filename)
    with open(ruta_archivo, "wb") as f:
        contenido = archivo.file.read()
        f.write(contenido)

    return crud_materiales.guardar_material(
        db, nombre, tipo, ruta_archivo, curso_id
    )

@router.get("/materiales/{curso_id}", response_model=list[esquemas.MaterialRespuesta])
def ver_materiales(curso_id: int, db: Session = Depends(obtener_db)):
    return crud_materiales.listar_materiales_curso(db, curso_id)
