import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class EstadosReportes(base_class):
    __tablename__ = 'estados_reportes'

    id = Column(Integer, primary_key = True)
    nombre = Column(String, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "nombre": self.nombre
        }

        return json.dumps(columnas)
