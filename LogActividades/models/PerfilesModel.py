import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text

class PerfilesModel(base_class):
    __tablename__ = 'perfiles'

    id = Column(Integer, primary_key = True)
    nombre = Column(String, nullable = False)
    descripcion = Column(String, nullable = False)
    estado = Column(Integer, nullable = False)
    usuario = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())

    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "estado": self.estado,
            "usuario": self.usuario,
            "fecha_reg": str(self.fecha_reg)
        }

        return json.dumps(columnas)