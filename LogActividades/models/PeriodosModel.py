import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class PeriodosModel(base_class):
    __tablename__ = 'periodos'

    id = Column(Integer, primary_key = True)
    descripcion = Column(String, nullable = False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "descripcion": self.descripcion,
            "fecha_reg": str(self.fecha_reg)
        }

        return json.dumps(columnas)