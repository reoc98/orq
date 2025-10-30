from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime

class ModulosModel(base_class):
    __tablename__ = 'modulos'

    id = Column(Integer, primary_key = True)
    descripcion = Column(String, nullable = False)
    activo = Column(Integer, nullable = False)
    icono = Column(String, nullable = False)
    fecha_reg = Column(DateTime, nullable = False)
