from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text

class PolizasActivas(base_class):
    __tablename__ = 'polizas_activas'

    id = Column(Integer, primary_key = True)
    numero_poliza = Column(Integer, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())
