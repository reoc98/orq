import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text
from datetime import datetime

class ReglaLog(base_class):
    __tablename__ = 'reglas_logs'

    id = Column(Integer, primary_key = True)
    request = Column(Text, nullable = False)
    response = Column(Integer, nullable = False)
    condicion = Column(String, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, payload):
            self.request = payload.get('request',"")
            self.response = payload.get('response',"")
            self.condicion = payload.get('condicion',"")
            self.fecha_reg = datetime.today().strftime('%Y-%m-%d %H:%M:%S')


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "request": self.request,
            "response": self.response,
            "condicion": self.condicion,
            "fecha_reg":str (self.fecha_reg)
        }

        return json.dumps(columnas)
