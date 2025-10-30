import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class Ciudades(base_class):
    __tablename__ = 'ciudades'

    id = Column(Integer, primary_key = True)
    codigo = Column(String, nullable = False)
    codigo_departamento = Column(String, nullable = False)
    descripcion = Column(String, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
        }

        return json.dumps(columnas)

   