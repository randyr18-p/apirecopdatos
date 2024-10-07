from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from dotenv import load_dotenv


# Cargar el archivo .env para obtener las variables de entorno
load_dotenv()

# Leer la variable de entorno DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Verificación de que DATABASE_URL esté definida
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está definida en el archivo .env")

# Crear el motor asíncrono usando la URL de la base de datos
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear la fábrica de sesiones asíncronas
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Declarative base para definir los modelos ORM
Base = declarative_base()

# Función para inicializar la base de datos
async def init_db():
    async with engine.begin() as conn:
        # Opción para crear todas las tablas (si no existen)
        await conn.run_sync(Base.metadata.create_all)
# Función para obtener una sesión de base de datos en FastAPI
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()