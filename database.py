from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de datos (asincrónica)
# Reemplaza 'root', '', 'localhost', '3306', y 'apidatos' con los valores correctos para tu base de datos.
SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:@localhost:3306/apidatos"

# Crear el motor de conexión a la base de datos (asincrónico)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Crear una sesión local para manejar la comunicación con la base de datos (asincrónica)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession  # Usar la clase AsyncSession para asincronía
)

# Declarative base, para crear los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos (asincrónica)
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
