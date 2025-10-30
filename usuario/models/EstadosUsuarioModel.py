import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class EstadosUsuarioModel(base_class):
    __tablename__ = 'estados_usuario'

    id = Column(Integer, primary_key = True)
    descripcion = Column(String, nullable = False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())


    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "DESCRIPCION": self.descripcion,
        }

        return json.dumps(columnas)

   