import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, DateTime, sql,Text

class Arbol(base_class):
    __tablename__ = 'arbol'

    id = Column(Integer, primary_key = True)
    tipo_variable_id = Column(Integer, nullable = False)
    usuario_id = Column(Integer, nullable = False)
    codigo = Column(Text, nullable = False)
    nombre = Column(Text, nullable = False)
    descripcion = Column(Text, nullable = False)
    padre = Column(Integer, nullable = False)
    activo = Column(Integer, nullable = False)
    version = Column(Integer, nullable = False)
    fechareg = Column(DateTime, nullable = False)
    fecha_update = Column(DateTime, nullable = False,  server_default = sql.func.now())


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "tipo_variable_id": self.tipo_variable_id,
            "usuario_id": self.usuario_id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "padre": self.padre,
            "activo": self.activo,
            "version": self.version,
            "fechareg": str(self.fechareg),
            "fecha_update":str (self.fecha_update)
        }
        return json.dumps(columnas)