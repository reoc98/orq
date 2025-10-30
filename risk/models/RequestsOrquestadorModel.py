import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text

class RequestsOrquestadorModel(base_class):
    __tablename__ = 'requests_orquestador'

    id = Column(Integer, primary_key = True)
    request = Column(Text, nullable = False)
    response = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    risk = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, payload):
            self.request = payload.get('request',"")
            self.response = payload.get('response',"")
            self.estado = payload.get('estado',1)


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "request": self.request,
            "response": self.response,
            "estado": self.estado,
            "fecha_reg":str (self.fecha_reg)
        }

        return json.dumps(columnas)