from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class ArbolEjecucion(base_class):
    __tablename__ = 'arbol_ejecucion'

    id = Column(Integer, primary_key = True)
    codigo = Column(String, nullable = False)
    tipo = Column(String, nullable = False)
    risk = Column(Integer, nullable = False)
    risk_array = Column(String, nullable = False)
    vehiculo = Column(Integer, nullable = False)
    variable_comentario = Column(String, nullable = False)
    estado = Column(Integer, nullable = False)
