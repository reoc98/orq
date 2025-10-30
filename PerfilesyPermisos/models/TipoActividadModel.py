import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class TipoActividadModel(base_class):
    __tablename__ = "tipo_actividad"

    id = Column(Integer, primary_key = True, nullable=False)
    codigo = Column(String, nullable = False)
    nombre = Column(String, nullable = False)
    modulo = Column(String, nullable = False)
    icono = Column(String, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())

    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "CODIGO": self.codigo,
            "NOMBRE": self.nombre,
            "MODULO": self.modulo,
            "ICONO": self.icono,
            "ESTADO": self.estado,
            "FECHA_REG": str(self.fecha_reg)
        }

        return json.dumps(columnas)
