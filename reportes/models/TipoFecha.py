import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class TipoFecha(base_class):
    __tablename__ = 'tipo_fecha'

    id = Column(Integer, primary_key = True)
    descripcion = Column(String, nullable = False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "descripcion": self.descripcion,
        }

        return json.dumps(columnas)

   