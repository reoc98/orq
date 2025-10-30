import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class ArbolModel(base_class):
    __tablename__ = 'arbol'

    id = Column(Integer, primary_key = True, nullable=False)
    tipo_variable_id = Column(Integer, nullable=False)
    usuario_id = Column(Integer, nullable=False)
    codigo = Column(String, nullable = False)
    nombre = Column(String, nullable = False)
    padre = Column(String, nullable = False)
    descripcion = Column(String, nullable = False)

    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre, 
            "descripcion": self.descripcion
        }

        return json.dumps(columnas)
