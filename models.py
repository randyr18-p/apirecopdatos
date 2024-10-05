from sqlalchemy import Column, Integer, String, Boolean, Date, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Modelo para la tabla de clientes
class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    telefono = Column(String(255), nullable=False)
    correo_electronico = Column(String(255), nullable=False, unique=True)
    fecha_nacimiento = Column(Date, nullable=True)
    fecha_registro = Column(TIMESTAMP, default=func.now())
    activo = Column(Boolean, default=True)

    # Relación con las tablas de Consentimiento y Auditoría
    consentimientos = relationship("Consentimiento", back_populates="cliente", cascade="all, delete-orphan")
    auditorias = relationship("Auditoria", back_populates="cliente", cascade="all, delete-orphan")


# Modelo para la tabla de consentimientos
class Consentimiento(Base):
    __tablename__ = "consentimientos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    acepta_terminos = Column(Boolean, nullable=False)
    fecha_consentimiento = Column(TIMESTAMP, default=func.now())

    # Relación con el cliente
    cliente = relationship("Cliente", back_populates="consentimientos")


# Modelo para la tabla de auditoría
class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    accion = Column(String(255), nullable=False)
    fecha = Column(TIMESTAMP, default=func.now())

    # Relación con el cliente
    cliente = relationship("Cliente", back_populates="auditorias")
