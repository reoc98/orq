from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql, ForeignKey

class ArbolEjecucion(base_class):
    __tablename__ = 'arbol_ejecucion'

    id = Column(Integer, primary_key = True)
    codigo = Column(String,  ForeignKey('arbol.codigo'))
    tipo = Column(String, nullable = False)
    risk = Column(Integer, nullable = False)
    risk_array = Column(String, nullable = False)
    vehiculo = Column(Integer, nullable = False)
    variable_comentario = Column(String, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())
