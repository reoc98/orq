import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime

class ModulosModel(base_class):
    __tablename__ = 'modulos'

    id = Column(Integer, primary_key = True)
    nombre = Column(String, nullable = False)
    descripcion = Column(String, nullable = False)
    orden = Column(Integer)
    activo = Column(Integer, nullable = False)
    ruta = Column(String)
    icono = Column(String, nullable = False)
    visible = Column(Integer, nullable = False)
    cabecera = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False)

    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "NOMBRE": self.nombre,
            "DESCRIPCION": self.descripcion,
            "ORDEN": self.orden,
            "RUTA": self.ruta,
            "ICONO": self.icono,
            "FECHA_REG": str(self.fecha_reg)
        }

        return json.dumps(columnas)
