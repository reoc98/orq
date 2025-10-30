import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text

class RequestsOrquestadorModel(base_class):
    __tablename__ = 'requests_orquestador'

    id = Column(Integer, primary_key = True)
    numero_siniestro = Column(Integer, nullable = False)
    cod_ciudad = Column(Integer, nullable = False)
    cod_departamento = Column(Integer, nullable = False)
    fecha_hora_ocurrencia = Column(DateTime, nullable = False)
    request = Column(Text, nullable = False)
    response = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, payload):
            self.numero_siniestro = payload.get('numero_siniestro',"")
            self.cod_ciudad = payload.get('cod_ciudad',None)
            self.cod_departamento = payload.get('cod_departamento',None)
            self.fecha_hora_ocurrencia = payload.get('fecha_hora_ocurrencia',"")
            self.request = payload.get('request',"")
            self.response = payload.get('response',"")
            self.estado = payload.get('estado',1)


    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "REQUEST": self.request,
            "RESPONSE": self.response,
            "ESTADO": self.estado,
            "FECHA_REG":str (self.fecha_reg)
        }

        return json.dumps(columnas)