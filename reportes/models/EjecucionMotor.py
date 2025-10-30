import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, DateTime, sql,Text

class EjecucionMotor(base_class):
    __tablename__ = 'ejecucion_motor'

    id = Column(Integer, primary_key = True)
    id_request = Column(Integer, nullable = False)
    id_arbol = Column(Integer, nullable = False)
    codigo_arbol = Column(Text, nullable = False)
    figura = Column(Text, nullable = False)
    datos_request = Column(Text, nullable = False)
    datos_response = Column(Text, nullable = False)
    desenlace_contenido = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())
    fecha_upd = Column(DateTime, nullable = False)


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "id_request": self.id_request,
            "id_arbol": self.id_arbol,
            "codigo_arbol": self.codigo_arbol,
            "figura": self.figura,
            "datos_request": self.datos_request,
            "datos_response": self.datos_response,
            "desenlace_contenido": self.desenlace_contenido,
            "estado": self.estado,
            "fecha_reg":str (self.fecha_reg),
            "fecha_upd": str (self.fecha_upd)
        }
        return json.dumps(columnas)