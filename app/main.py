from multiprocessing import get_context
from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .dependencias import obtener_db, requerir_docente, requerir_estudiante
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .auth import create_access_token, decode_access_token
from .modelos import Usuario
from datetime import datetime
from flask import send_from_directory
import os

from . import modelos, db, auth, crud_usuarios, crud_cursos, esquemas, crud_foro, crud_evaluaciones, crud_asignaciones, dependencias
from . import (
    rutas_usuarios,
    rutas_login,
    rutas_perfil,
    rutas_cursos,
    rutas_asignaciones,
    rutas_materiales,
    rutas_evaluaciones,
    rutas_foro,
    rutas_seguimiento,

)

# Crear las tablas en la base de datos
modelos.Base.metadata.create_all(bind=db.engine)

# Inicializa la aplicación
app = FastAPI(title="Plataforma Educativa")

# Configuración de plantillas y archivos estáticos
templates = Jinja2Templates(directory="app/templates")
templates_docente = Jinja2Templates(directory="app/templates/docente")
templates_estudiante = Jinja2Templates(directory="app/templates/estudiante")

app.mount("/static", StaticFiles(directory="static"), name="static")

# OAuth2 Token (si es necesario para futuras mejoras)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Incluir rutas
app.include_router(rutas_usuarios.router)
app.include_router(rutas_login.router)
app.include_router(rutas_perfil.router)
app.include_router(rutas_cursos.router)
app.include_router(rutas_asignaciones.router)
app.include_router(rutas_materiales.router)
app.include_router(rutas_evaluaciones.router)
app.include_router(rutas_foro.router)
app.include_router(rutas_seguimiento.router)

@app.route('/descargar-archivo/<int:evaluacion_id>')
def descargar_archivo(evaluacion_id):
    evaluacion = modelos.Evaluacion.query.get_or_404(evaluacion_id)
    directorio_archivos = os.path.join(app.root_path, 'uploads')  # Ajusta según tu estructura
    
    return send_from_directory(
        directory=directorio_archivos,
        path=evaluacion.archivo_entrega,
        as_attachment=True
    )

@app.post("/token")
def login_api(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.obtener_db)):
    usuario = crud_usuarios.autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Crear el token JWT
    access_token = create_access_token(data={"sub": usuario.correo})
    
    # Devuelve el token en el formato de Bearer Token
    return {"access_token": access_token, "token_type": "bearer"}


# Mostrar el formulario de login (GET)
# Formularios de login
@app.get("/login", response_class=HTMLResponse)
def mostrar_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def procesar_login(
    request: Request,
    correo: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(db.obtener_db)
):
    # Autenticación del usuario
    usuario = crud_usuarios.autenticar_usuario(db, correo, contrasena)
    if not usuario:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "mensaje": "Correo o contraseña incorrectos"
        })

    # Crear token JWT
    access_token = create_access_token(data={"sub": usuario.correo})

    # Redirigir al dashboard basado en el rol del usuario, incluyendo el token como cookie
    if usuario.rol == 'Docente':
        response = RedirectResponse(url="/dashboard-docente", status_code=302)
    else:
        response = RedirectResponse(url="/dashboard-estudiante", status_code=302)

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response 

# Logout
@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "mensaje": "Has cerrado sesión correctamente."
    })

# Formulario de registro (GET)
@app.get("/registro", response_class=HTMLResponse)
def mostrar_formulario_registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

# Procesar registro (POST)
@app.post("/registro", response_class=HTMLResponse)
async def registrar_estudiante(
    request: Request,
    nombre: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(...),
    rol: str = Form(...),
    db: Session = Depends(db.obtener_db)
):
    try:
        # Verificar si el usuario ya existe
        usuario_existente = crud_usuarios.obtener_usuario_por_correo(db, correo)
        if usuario_existente:
            return templates.TemplateResponse("registro.html", {
                "request": request,
                "mensaje": "Ya existe una cuenta con este correo."
            })

        # Crear y guardar el nuevo usuario
        nuevo_usuario = esquemas.UsuarioCrear(
            nombre=nombre,
            correo=correo,
            contrasena=contrasena,  # Se puede cifrar aquí si lo implementas
            rol=rol,
        )
        crud_usuarios.crear_usuario(db, nuevo_usuario)

        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        print("ERROR AL REGISTRAR:", e)
        return templates.TemplateResponse("registro.html", {
            "request": request,
            "mensaje": f"Error al registrar: {str(e)}"
        })

@app.get("/dashboard-docente", response_class=HTMLResponse)
async def dashboard_docente(
    request: Request,
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db)  # <- también debes inyectar db si lo usas aquí
):
    try:
        # Obtener los cursos asignados al docente
        cursos_asignados = crud_cursos.obtener_cursos_asignados(db, usuario_actual.id)
        return templates_docente.TemplateResponse("dashboard_docente.html", {
            "request": request,
            "cursos": cursos_asignados,
            "usuario": usuario_actual
        })
    except Exception as e:
        print(f"Error en dashboard-docente: {e}")
        raise HTTPException(status_code=500, detail="Error cargando el dashboard docente")

@app.get("/crear_curso", response_class=HTMLResponse)
def crear_curso_form(request: Request, exito: str = None, db: Session = Depends(obtener_db)):
    modo_edicion = False  # Este valor indica que estamos creando un nuevo curso
    curso = {
        "titulo": "",
        "codigo": "",
        "departamento": "",
        "descripcion": "",
        "creditos": "",
        "horas": "",
        "fecha_inicio": "",
        "fecha_fin": "",
        "cupo_maximo": ""
    }

    return templates_docente.TemplateResponse("crear_curso.html", {
        "request": request, 
        "curso": curso,  # Pasamos el objeto "curso"
        "modo_edicion": modo_edicion,
        "exito": exito
    })

@app.post("/guardar-curso")
async def guardar_curso(
    titulo: str = Form(...),
    codigo: str = Form(...),
    departamento: str = Form(...),
    descripcion: str = Form(...),
    creditos: int = Form(...),
    horas: int = Form(...),
    fecha_inicio: str = Form(...),
    fecha_fin: str = Form(...),
    cupo_maximo: int = Form(...),
    db: Session = Depends(obtener_db),
    usuario_actual: Usuario = Depends(requerir_docente)  # <-- Aquí
):
    # Creamos el objeto con los datos del formulario
    datos = esquemas.CursoCrear(
        titulo=titulo,
        codigo=codigo,
        departamento=departamento,
        descripcion=descripcion,
        creditos=creditos,
        horas=horas,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        cupo_maximo=cupo_maximo
    )

    # Llamamos al CRUD real, no al formulario
    resultado = crud_cursos.crear_curso(db, datos, creador_id=usuario_actual.id)

    # Verificamos si el resultado es un objeto Curso o un error
    if isinstance(resultado, dict) and "error" in resultado:
        # Si es un diccionario con error, lanzamos una excepción HTTP con el error
        raise HTTPException(status_code=400, detail=resultado["error"])
    
    # Si todo es correcto, retornamos un mensaje de éxito
    return RedirectResponse(url="/crear_curso?exito=crear", status_code=302)
    
@app.get("/curso/{curso_id}", response_class=HTMLResponse)
async def ver_detalle_curso(
    curso_id: int,
    request: Request,
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db)
):
    curso = crud_cursos.obtener_curso(db, curso_id, usuario_actual.id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado o acceso no autorizado")

    return templates_docente.TemplateResponse("dashboard_docente.html", {
        "request": request,
        "curso": curso,
        "usuario": usuario_actual.id
    })

@app.get("/cursos/{curso_id}/ver", response_class=HTMLResponse)
def ver_curso_detalle(
    request: Request,  # Asegúrate de que 'request' esté primero
    curso_id: int,
    db: Session = Depends(obtener_db),
    usuario_actual: Usuario = Depends(requerir_docente)
):
    curso = crud_cursos.obtener_curso(db, curso_id, usuario_actual.id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado o no autorizado")
    
    # Renderiza la página con los detalles del curso en modo visualización
    return templates_docente.TemplateResponse("crear_curso.html", {
        "request": request,  # Pasa el 'request' al contexto
        "curso": curso,
        "modo_edicion": "ver",
        "user": usuario_actual.id
    })

@app.get("/curso/{curso_id}/editar", response_class=HTMLResponse)
def mostrar_formulario_edicion(
    request: Request,
    curso_id: int,
    db: Session = Depends(obtener_db),
    usuario_actual: Usuario = Depends(requerir_docente),
    exito: str = None
):
    curso = crud_cursos.obtener_curso(db, curso_id, usuario_actual.id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado o no autorizado")
    
    return templates_docente.TemplateResponse("crear_curso.html", {
        "request": request,
        "curso": curso,
        "modo_edicion": "editar",  # Indica que el formulario es para editar
        "exito": exito,
        "user": usuario_actual.id
    })

@app.post("/curso/{curso_id}/editar")
def actualizar_curso(
    request: Request,
    curso_id: int,
    titulo: str = Form(...),
    descripcion: str = Form(...),
    codigo: str = Form(...),
    departamento: str = Form(...),
    creditos: int = Form(...),
    horas: int = Form(...),
    fecha_inicio: str = Form(...),
    fecha_fin: str = Form(...),
    cupo_maximo: int = Form(...),
    db: Session = Depends(obtener_db),
    usuario_actual: Usuario = Depends(requerir_docente)
):
    # Crear un objeto de datos (esquema) para enviar a CRUD
    datos_curso = esquemas.CursoCrear(
        titulo=titulo,
        descripcion=descripcion,
        codigo=codigo,
        departamento=departamento,
        creditos=creditos,
        horas=horas,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        cupo_maximo=cupo_maximo
    )

    # Llamar al CRUD para actualizar
    curso = crud_cursos.actualizar_curso(db, curso_id, usuario_actual.id, datos_curso)
    
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado o no autorizado")

    # Redirigir a la página del curso actualizado
    return RedirectResponse(url=f"/curso/{curso_id}/editar?exito=editar", status_code=302)

@app.get("/foro_principal", response_class=HTMLResponse)
def listar_foros(
    request: Request,
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db)
):
    # Obtener los foros del docente logueado
    foros = crud_foro.obtener_foros_por_usuario(db, usuario_actual.id)
    return templates_docente.TemplateResponse("foros_principal.html", {"request": request, "foros": foros})


@app.get("/api/foros")
def buscar_foros(
    search: str = "",
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db)
):
    # Obtener todos los foros del docente
    foros = crud_foro.obtener_foros_por_usuario(db, usuario_actual.id)

    # Filtrar por término de búsqueda (insensible a mayúsculas)
    resultados = [
        {"id": foro.id, "titulo": foro.titulo}
        for foro in foros
        if search.lower() in foro.titulo.lower()
    ]

    return JSONResponse(content={"foros": resultados})
    
@app.get("/crear_nuevo_foro", response_class=HTMLResponse)
async def foro_nuevo(
    request: Request,
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db),  # <- también debes inyectar db si lo usas aquí
    exito: str = None
):
    # Obtener cursos asignados al usuario actual
    cursos_usuario = crud_cursos.obtener_cursos_asignados(db, usuario_actual.id)

    return templates_docente.TemplateResponse("crear_foro.html", {
        "request": request,
        "usuario": usuario_actual,
        "cursos": cursos_usuario,  # <--- Esto se pasa al HTML
        "exito": exito
    })
    

@app.post("/crear_foro")
async def crear_foro(
    request: Request,
    curso_id: int = Form(...),  # Recibe curso_id como un campo de formulario
    titulo: str = Form(...),    # Recibe el título del foro
    contenido: str = Form(...), # Recibe el contenido del foro
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db)
):
    # Verificamos si el curso existe
    curso = db.query(modelos.Curso).filter(modelos.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Creamos el nuevo foro
    nuevo_foro = modelos.Foro(
        titulo=titulo,
        contenido=contenido,
        curso_id=curso_id,
        usuario_id=usuario_actual.id
    )
    
    db.add(nuevo_foro)
    db.commit()
    db.refresh(nuevo_foro)
    
    return RedirectResponse(url="/crear_nuevo_foro?exito=crear", status_code=302)

@app.get("/foro/{foro_id}", response_class=HTMLResponse)
def ver_foro(
    foro_id: int, 
    request: Request, 
    db: Session = Depends(obtener_db)
    ):

    foro = crud_foro.obtener_foro(db, foro_id)
    if not foro:
        raise HTTPException(status_code=404, detail="Foro no encontrado")
    
    curso = crud_cursos.obtener_curso_por_id(db, foro.curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return templates_docente.TemplateResponse("foro_interno.html", {
        "request": request,
        "foro": foro,
        "curso": curso
    })

@app.post("/guardar_mensaje")
def guardar_mensaje(
    datos: esquemas.MensajeCrear,
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db)
):
    nuevo_mensaje = crud_foro.crear_mensaje(db, datos.contenido, datos.foro_id, usuario_actual.id)
    return {"mensaje": "Mensaje creado", "id": nuevo_mensaje.id}

@app.get("/mensajes/{foro_id}")
def obtener_mensajes(foro_id: int, db: Session = Depends(obtener_db)):
    # Obtener los mensajes del foro con el ID proporcionado
    mensajes = crud_foro.obtener_mensajes_por_foro(db, foro_id)
    if not mensajes:
        raise HTTPException(status_code=404, detail="No se encontraron mensajes para este foro")
    return {"foro_id": foro_id, "mensajes": mensajes}

@app.get("/principal-evaluaciones", response_class=HTMLResponse)
async def principal_evaluaciones(
    request: Request,
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db)
):
    # Obtener evaluaciones del docente actual con su curso asociado
    evaluaciones = db.query(modelos.Evaluacion).filter(
        modelos.Evaluacion.usuario_id == usuario_actual.id
    ).all()

    return templates_docente.TemplateResponse("principal_evaluaciones.html", {
        "request": request,
        "usuario": usuario_actual,
        "evaluaciones": evaluaciones
    })


@app.get("/nueva-evaluacion", response_class=HTMLResponse)
async def principal_evaluaciones(
    request: Request,
    usuario_actual: Usuario = Depends(requerir_docente),
    db: Session = Depends(obtener_db),  # <- también debes inyectar db si lo usas aquí
    exito: str = None
):
    modo_edicion = False
    # Obtener cursos asignados al usuario actual
    cursos_usuario = crud_cursos.obtener_cursos_asignados(db, usuario_actual.id)

    return templates_docente.TemplateResponse("crear_evaluacion.html", {
        "request": request,
        "usuario": usuario_actual,
        "cursos": cursos_usuario,
        "modo_edicion": modo_edicion,
        "exito": exito
    })

@app.post("/evaluaciones/crear")
async def crear_evaluacion(
    request: Request,
    titulo: str = Form(...),
    descripcion: str = Form(...),
    fecha_inicio: str = Form(...),
    fecha_limite: str = Form(...),
    curso_id: int = Form(...),
    usuario_actual: Usuario = Depends(requerir_docente),
    puntaje_maximo: int = Form(...),
    tipo: str = Form(...),
    archivo_entrega: Optional[UploadFile] = File(None),  # Opcional
    url_entrega: Optional[str] = Form(None),             # Opcional
    db: Session = Depends(obtener_db)
):
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    fecha_limite = datetime.strptime(fecha_limite, "%Y-%m-%d").date()

    curso = db.query(modelos.Curso).filter(modelos.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    # Determinamos el tipo de evaluación y actuamos según corresponda
    if tipo in ["Tarea", "Proyecto"]:
        if not archivo_entrega:
            raise HTTPException(status_code=400, detail="Debe subir un archivo para tareas o proyectos")
        nombre_archivo = archivo_entrega.filename
        contenido = await archivo_entrega.read()  # Aquí podrías guardarlo si quieres
        # Guarda el archivo en el sistema o en algún almacenamiento según tu lógica
    elif tipo == "Examen":
        if not url_entrega:
            raise HTTPException(status_code=400, detail="Debe ingresar una URL para exámenes")
        nombre_archivo = None  # No necesitamos archivo para el tipo Examen
    else:
        raise HTTPException(status_code=400, detail="Tipo de evaluación no válido")

    evaluacion_data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "fecha_inicio": fecha_inicio,
        "fecha_limite": fecha_limite,
        "curso_id": curso_id,
        "usuario_id": usuario_actual.id,
        "puntaje_maximo": puntaje_maximo,
        "tipo": tipo,
        "archivo_entrega": nombre_archivo if tipo != "Examen" else None,
        "url_entrega": url_entrega if tipo == "Examen" else None
    }

    # Aquí se asume que el CRUD de evaluaciones maneja la creación de la evaluación correctamente
    crud_evaluaciones.crear_evaluacion(db=db, evaluacion=esquemas.EvaluacionCreate(**evaluacion_data))

    return RedirectResponse(url="/principal-evaluaciones?exito=crear", status_code=302)

@app.get("/evaluaciones/{evaluacion_id}/ver", response_class=HTMLResponse)
def ver_evaluacion_detalle(
    request: Request,
    evaluacion_id: int,
    db: Session = Depends(obtener_db),
    usuario_actual: Usuario = Depends(requerir_docente)
):
    evaluacion = crud_evaluaciones.obtener_evaluacion(db, evaluacion_id, usuario_actual.id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada o no autorizada")

    cursos = db.query(modelos.Curso).filter(modelos.Curso.creador_id == usuario_actual.id).all()

    return templates_docente.TemplateResponse("crear_evaluacion.html", {
        "request": request,
        "evaluacion": evaluacion,
        "cursos": cursos,
        "modo_edicion": "ver",
        "user": usuario_actual.id
    })

@app.get("/evaluaciones/{evaluacion_id}/editar", response_class=HTMLResponse)
def mostrar_formulario_edicion_evaluacion(
    request: Request,
    evaluacion_id: int,
    db: Session = Depends(obtener_db),
    usuario_actual: Usuario = Depends(requerir_docente),
    exito: str = None
):
    evaluacion = crud_evaluaciones.obtener_evaluacion(db, evaluacion_id, usuario_actual.id)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada o no autorizada")
    
    cursos = db.query(modelos.Curso).filter(modelos.Curso.creador_id == usuario_actual.id).all()

    return templates_docente.TemplateResponse("crear_evaluacion.html", {
        "request": request,
        "evaluacion": evaluacion,
        "cursos": cursos,
        "modo_edicion": "editar",
        "exito": exito,
        "user": usuario_actual.id
    })

@app.post("/evaluaciones/{evaluacion_id}/editar")
def actualizar_evaluacion(
    request: Request,
    evaluacion_id: int,
    titulo: str = Form(...),
    descripcion: str = Form(...),
    fecha_inicio: str = Form(...),
    fecha_limite: str = Form(...),
    curso_id: int = Form(...),
    puntaje_maximo: int = Form(...),
    tipo: str = Form(...),
    url_entrega: Optional[str] = Form(None),
    archivo_entrega: Optional[UploadFile] = File(None),
    db: Session = Depends(obtener_db),
    usuario_actual: Usuario = Depends(requerir_docente)
):
    try:
        # Convertir fechas de string a date
        fecha_inicio_date = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_limite_date = datetime.strptime(fecha_limite, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {e}")

    # Verificar si el usuario tiene permisos sobre el evaluacion (opcional)
    curso = db.query(modelos.Evaluacion).filter(
        modelos.Evaluacion.id == evaluacion_id,
        modelos.Evaluacion.usuario_id == usuario_actual.id
    ).first()
    if not curso:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar evaluaciones en este curso")

    # Preparar datos para actualizar
    datos_actualizados = esquemas.EvaluacionUpdate(
        titulo=titulo,
        descripcion=descripcion,
        fecha_inicio=fecha_inicio_date,
        fecha_limite=fecha_limite_date,
        curso_id=curso_id,
        puntaje_maximo=puntaje_maximo,
        tipo=tipo,
        archivo_entrega=archivo_entrega.filename if archivo_entrega else None,
        url_entrega=url_entrega
    )

    # Llamar al CRUD
    evaluacion = crud_evaluaciones.editar_evaluacion(db, evaluacion_id, usuario_actual.id, datos_actualizados)
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada o no tienes permisos para editarla")

    return RedirectResponse(url=f"/principal-evaluaciones?exito=editar", status_code=302)



@app.get("/dashboard-estudiante", response_class=HTMLResponse)
async def dashboard_estudiante(
    request: Request,
    usuario_actual: Usuario = Depends(requerir_estudiante),  # <- Dependencia específica para estudiantes
    db: Session = Depends(obtener_db)
):
    try:
        # Obtener los cursos asignados al estudiante
        cursos_asignados = crud_cursos.obtener_cursos_asignados_estudiante(db, usuario_actual.id)

        return templates.TemplateResponse("estudiante/dashboard_estudiante.html", {
            "request": request,
            "cursos": cursos_asignados,
            "usuario": usuario_actual
        })
    except Exception as e:
        print(f"Error en dashboard-estudiante: {e}")
        raise HTTPException(status_code=500, detail="Error cargando el dashboard del estudiante")


@app.get("/cursos", response_class=HTMLResponse)
async def listar_cursos_no_asignados(
    request: Request,
    db: Session = Depends(obtener_db),
    usuario = Depends(requerir_estudiante)
):
    try:
        subconsulta = db.query(modelos.usuarios_cursos.c.curso_id).filter(
            modelos.usuarios_cursos.c.usuario_id == usuario.id
        )
        # Cursos que NO están en la subconsulta
        cursos_no_asignados = db.query(modelos.Curso).filter(
            ~modelos.Curso.id.in_(subconsulta)
        ).all()

        return templates.TemplateResponse("estudiante/cursos.html", {
            "request": request,
            "cursos": cursos_no_asignados
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cursos no asignados: {str(e)}")


@app.get("/detallecurso/{curso_id}", response_class=HTMLResponse)
async def detalle_curso(
    curso_id: int,
    request: Request,
    db: Session = Depends(db.obtener_db),
    usuario = Depends(requerir_estudiante)
):
    try:
        curso = db.query(modelos.Curso).filter(modelos.Curso.id == curso_id).first()
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado.")

        # Verificar si ya está registrado
        registrado = db.query(modelos.usuarios_cursos).filter_by(
            usuario_id=usuario.id,
            curso_id=curso_id
        ).first() is not None

        return templates.TemplateResponse("estudiante/detalle_curso.html", {
            "request": request,
            "curso": curso,
            "registrado": registrado
        })
    except Exception as e:
        print(f"Error en detalle_curso: {str(e)}")
        raise HTTPException(status_code=500, detail="Error cargando el detalle del curso.")
    
    
@app.post("/registrar_estudiante_curso/{curso_id}")
async def registrar_estudiante_en_curso(
    curso_id: int,
    request: Request,
    db: Session = Depends(obtener_db),
    usuario = Depends(requerir_estudiante)
):
    try:
        if usuario.rol != "Estudiante":
            raise HTTPException(status_code=403, detail="Solo los estudiantes pueden registrarse en cursos.")

        curso = db.query(modelos.Curso).filter(modelos.Curso.id == curso_id).first()
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado.")

        # Accedemos al atributo .id en lugar de usar ["id"]
        estudiante_ya_registrado = db.query(modelos.usuarios_cursos).filter_by(
            usuario_id=usuario.id, curso_id=curso_id
        ).first()

        if estudiante_ya_registrado:
            return templates.TemplateResponse("estudiante/mensaje_exito.html", {
                "request": request,
                "mensaje": "Ya estas registrado en el curso",
                "redirect_url": f"/detallecurso/{curso_id}"
            })

        relacion = modelos.usuarios_cursos.insert().values(
            usuario_id=usuario.id,
            curso_id=curso_id,
            es_docente=False
        )
        db.execute(relacion)
        db.commit()

        return templates.TemplateResponse("estudiante/mensaje_exito.html", {
            "request": request,
            "mensaje": "Te has registrado exitosamente en el curso.",
            "redirect_url": f"/detallecurso/{curso_id}"
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al registrarte en el curso.")


@app.get("/foros", response_class=HTMLResponse)
def listar_foros_usuario(
    request: Request,
    db: Session = Depends(obtener_db),
    usuario: modelos.Usuario = Depends(requerir_estudiante)
):
    cursos = crud_foro.obtener_cursos_con_usuario(db, usuario.id)

    for curso in cursos:
        foro = db.query(modelos.Foro).filter_by(curso_id=curso.id).first()
        curso.tiene_foro = foro is not None
        curso.foro_id = foro.id if foro else None

    return templates.TemplateResponse("estudiante/foros.html", {
        "request": request,
        "cursos": cursos,
    })

@app.get("/foro-estudiante/{foro_id}", response_class=HTMLResponse)
def ver_foro_curso(
    foro_id: int,
    request: Request,
    exito: int = 0,
    db: Session = Depends(obtener_db),
    usuario: modelos.Usuario = Depends(requerir_estudiante)
):
    foro = db.query(modelos.Foro).filter_by(id=foro_id).first()
    
    if not foro:

        return HTMLResponse(content="Foro no encontrado", status_code=404)

    mensajes = crud_foro.obtener_mensajes_por_foro(db, foro.id)

    return templates.TemplateResponse("estudiante/detalle_foro.html", {
        "request": request,
        "foro": foro,
        "mensajes": mensajes,
        "usuario": usuario,
        "exito": exito == 1
    })


@app.post("/foros/{foro_id}/mensaje")
def crear_mensaje_foro(
    foro_id: int,
    contenido: str = Form(...),
    db: Session = Depends(obtener_db),
    usuario: modelos.Usuario = Depends(requerir_estudiante)
):
    nuevo_mensaje = modelos.MensajeForo(
        contenido=contenido,
        foro_id=foro_id,
        usuario_id=usuario.id
    )
    db.add(nuevo_mensaje)
    db.commit()
    return RedirectResponse(url=f"/foro-estudiante/{foro_id}?exito=1", status_code=303)


from datetime import date  

@app.get("/evaluaciones-estudiante", response_class=HTMLResponse)
def listar_evaluaciones_estudiante(
    request: Request,
    db: Session = Depends(obtener_db),
    usuario: modelos.Usuario = Depends(requerir_estudiante)
):
    evaluaciones = crud_evaluaciones.obtener_evaluaciones_de_cursos_asignados(db, usuario.id)

    return templates.TemplateResponse("estudiante/listar_evaluaciones.html", {
        "request": request,
        "evaluaciones": evaluaciones,
        "fecha_actual": date.today()  
    })


@app.get("/evaluaciones-estudiante/{evaluacion_id}", response_class=HTMLResponse)
def ver_evaluacion(request: Request, evaluacion_id: int, db: Session = Depends(obtener_db)):
    evaluacion = db.query(modelos.Evaluacion).filter(modelos.Evaluacion.id == evaluacion_id).first()
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    return templates.TemplateResponse("estudiante/ver_evaluacion.html", {
        "request": request,
        "evaluacion": evaluacion
    })