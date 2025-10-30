from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class TipoDocumento(base_class):
    __tablename__ = 'tipo_documento'

    id = Column(Integer, primary_key = True)
    codigo = Column(String, nullable = False)
    prefijo_request = Column(String, nullable = False)
    descripcion = Column(String, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())