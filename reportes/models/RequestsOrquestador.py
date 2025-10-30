import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, DateTime, sql,Text

class RequestsOrquestador(base_class):
    __tablename__ = 'requests_orquestador'

    id = Column(Integer, primary_key = True)
    numero_siniestro = Column(Integer, nullable = False)
    cod_ciudad = Column(Integer, nullable = False)
    cod_departamento = Column(Integer, nullable = False)
    fecha_hora_ocurrencia = Column(DateTime, nullable = False)
    request = Column(Text, nullable = False)
    response = Column(Text, nullable = False)
    risk = Column(Integer, nullable = False)
    ejecucion = Column(Integer, nullable = False)
    reintentar = Column(Integer, nullable = False)
    numero_reintentos = Column(Integer, nullable = False)
    id_estados_reportes = Column(Integer, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, payload):
        self.numero_siniestro = payload.get('numero_siniestro')
        self.request = payload.get('request',"")
        self.response = payload.get('response',"")
        self.risk = payload.get('risk')
        self.ejecucion = payload.get('ejecucion')
        self.reintentar = payload.get('reintentar')
        self.numero_reintentos = payload.get('numero_reintentos')
        self.id_estados_reportes = payload.get('id_estados_reportes')
        self.estado = payload.get('estado',1)

    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "numero_siniestro": self.numero_siniestro,
            "request": self.request,
            "response": self.response,
            "risk": self.risk,
            "ejecucion": self.ejecucion,
            "reintentar": self.reintentar,
            "numero_reintentos": self.numero_reintentos,
            "id_estados_reportes": self.id_estados_reportes,
            "estado": self.estado,
            "fecha_reg":str (self.fecha_reg)
        }
        return json.dumps(columnas)