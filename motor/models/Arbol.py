from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class Arbol(base_class):
    __tablename__ = 'arbol'

    id = Column(Integer, primary_key = True)
    tipo_variable_id = Column(Integer, nullable = False)
    usuario_id = Column(Integer, nullable = False)
    codigo = Column(String, nullable = False)
    nombre = Column(String, nullable = False)
    descripcion = Column(String, nullable = False)
    padre = Column(Integer, nullable = False)
    activo = Column(Integer, nullable = False)
    version = Column(Integer, nullable = False)
    fechareg = Column(DateTime, nullable = False,  server_default = sql.func.now())
    fecha_update = Column(DateTime, nullable = False,  server_default = sql.func.now())
