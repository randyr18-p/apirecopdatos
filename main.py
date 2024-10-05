import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import StreamingResponse, JSONResponse
import csv
from io import StringIO

import models
import schemas
from database import engine, get_db

app = FastAPI()

# Función asincrónica para crear las tablas en la base de datos si no existen
async def init_db():
    async with engine.begin() as conn:
        # Ejecutar operaciones DDL (como create_all) de manera sincrónica dentro del contexto asincrónico
        await conn.run_sync(models.Base.metadata.create_all)

# Llamada para inicializar la base de datos
@app.on_event("startup")
async def on_startup():
    await init_db()

# Función para registrar acciones en la tabla de auditoría (sincronía dentro del contexto asincrónico)
async def registrar_accion_auditoria(db: Session, cliente_id: int, accion: str):
    nueva_auditoria = models.Auditoria(
        cliente_id=cliente_id,
        accion=accion
    )
    db.add(nueva_auditoria)
    db.commit()
    db.refresh(nueva_auditoria)


# --- ENDPOINTS DE CLIENTES ---

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API FastAPI"}


# Crear un nuevo cliente
@app.post("/clientes/", response_model=schemas.ClienteResponse)
async def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    nuevo_cliente = models.Cliente(**cliente.dict())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    
    # Registrar acción en la auditoría
    await registrar_accion_auditoria(db, nuevo_cliente.id, "Cliente creado")
    
    return nuevo_cliente


# Obtener lista de clientes con paginación
@app.get("/clientes/", response_model=List[schemas.ClienteResponse])
async def obtener_clientes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).offset(skip).limit(limit).all()
    return clientes


# Obtener un cliente por ID
@app.get("/clientes/{cliente_id}", response_model=schemas.ClienteResponse)
async def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


# Actualizar un cliente existente
@app.put("/clientes/{cliente_id}", response_model=schemas.ClienteResponse)
async def actualizar_cliente(cliente_id: int, cliente_actualizado: schemas.ClienteCreate, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for key, value in cliente_actualizado.dict().items():
        setattr(cliente, key, value)
    
    db.commit()
    db.refresh(cliente)

    # Registrar acción en la auditoría
    await registrar_accion_auditoria(db, cliente.id, "Cliente actualizado")
    
    return cliente


# Eliminar (lógicamente) un cliente
@app.delete("/clientes/{cliente_id}", response_model=schemas.ClienteResponse)
async def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente.activo = False  # Eliminación lógica
    db.commit()

    # Registrar acción en la auditoría
    await registrar_accion_auditoria(db, cliente.id, "Cliente eliminado (borrado lógico)")
    
    return cliente


# --- ENDPOINTS PARA EXPORTAR DATOS ---

# Exportar datos de clientes en formato CSV o JSON
@app.get("/clientes/export")
async def exportar_datos(format: str = 'json', db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).all()

    if format == 'csv':
        # Exportar como CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'nombre', 'telefono', 'correo_electronico', 'fecha_nacimiento', 'fecha_registro', 'activo'])
        for cliente in clientes:
            writer.writerow([cliente.id, cliente.nombre, cliente.telefono, cliente.correo_electronico, cliente.fecha_nacimiento, cliente.fecha_registro, cliente.activo])
        output.seek(0)
        response = StreamingResponse(output, media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=clientes.csv"
        return response
    elif format == 'json':
        # Exportar como JSON
        return JSONResponse(content=[{
            "id": cliente.id,
            "nombre": cliente.nombre,
            "telefono": cliente.telefono,
            "correo_electronico": cliente.correo_electronico,
            "fecha_nacimiento": str(cliente.fecha_nacimiento),
            "fecha_registro": str(cliente.fecha_registro),
            "activo": cliente.activo
        } for cliente in clientes])

    raise HTTPException(status_code=400, detail="Formato no válido")


# --- ENDPOINTS PARA BÚSQUEDA Y FILTRADO ---

# Buscar clientes por nombre, correo o teléfono
@app.get("/clientes/buscar", response_model=List[schemas.ClienteResponse])
async def buscar_clientes(
    nombre: Optional[str] = None,
    correo: Optional[str] = None,
    telefono: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Cliente)
    
    # Filtrar por nombre
    if nombre:
        query = query.filter(models.Cliente.nombre.ilike(f"%{nombre}%"))

    # Filtrar por correo
    if correo:
        query = query.filter(models.Cliente.correo_electronico.ilike(f"%{correo}%"))

    # Filtrar por teléfono
    if telefono:
        query = query.filter(models.Cliente.telefono.ilike(f"%{telefono}%"))

    # Ejecutar consulta
    clientes = query.all()
    return clientes


# --- ENDPOINTS PARA CONSENTIMIENTOS ---

# Crear un nuevo consentimiento para un cliente
@app.post("/consentimientos/", response_model=schemas.ConsentimientoResponse)
async def crear_consentimiento(consentimiento: schemas.ConsentimientoCreate, db: Session = Depends(get_db)):
    nuevo_consentimiento = models.Consentimiento(**consentimiento.dict())
    db.add(nuevo_consentimiento)
    db.commit()
    db.refresh(nuevo_consentimiento)
    
    # Registrar la acción en la auditoría
    await registrar_accion_auditoria(db, nuevo_consentimiento.cliente_id, "Consentimiento registrado")
    
    return nuevo_consentimiento


# Obtener todos los consentimientos de un cliente
@app.get("/clientes/{cliente_id}/consentimientos", response_model=List[schemas.ConsentimientoResponse])
async def obtener_consentimientos(cliente_id: int, db: Session = Depends(get_db)):
    consentimientos = db.query(models.Consentimiento).filter(models.Consentimiento.cliente_id == cliente_id).all()
    return consentimientos


# --- ENDPOINTS PARA AUDITORÍA ---

# Crear un registro en la auditoría
@app.post("/auditoria/", response_model=schemas.AuditoriaResponse)
async def crear_auditoria(auditoria: schemas.AuditoriaCreate, db: Session = Depends(get_db)):
    nueva_auditoria = models.Auditoria(**auditoria.dict())
    db.add(nueva_auditoria)
    db.commit()
    db.refresh(nueva_auditoria)
    return nueva_auditoria


# Obtener todas las auditorías de un cliente
@app.get("/clientes/{cliente_id}/auditoria", response_model=List[schemas.AuditoriaResponse])
async def obtener_auditoria(cliente_id: int, db: Session = Depends(get_db)):
    auditorias = db.query(models.Auditoria).filter(models.Auditoria.cliente_id == cliente_id).all()
    return auditorias


# Obtener todas las auditorías con paginación
@app.get("/auditoria/", response_model=List[schemas.AuditoriaResponse])
async def obtener_auditoria_general(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    auditorias = db.query(models.Auditoria).offset(skip).limit(limit).all()
    return auditorias
