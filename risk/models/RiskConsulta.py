import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text
from datetime import datetime

class RiskConsulta(base_class):
    __tablename__ = 'risk_consulta'

    id = Column(Integer, primary_key = True)
    id_request = Column(Integer, nullable = False)
    tipo_figura = Column(String, nullable = False)
    numero_documento = Column(Integer, nullable = False)
    request_figuras = Column(Text, nullable = False)
    data_envio = Column(Text, nullable = False)
    data_response = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())
    fecha_upd = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, id_request, payload):
            self.id_request = id_request
            self.tipo_figura = payload['tipo_figura']
            self.numero_documento = payload['num_doc_figura']
            self.request_figuras = json.dumps(payload)
            self.estado = 0
            self.fecha_reg = datetime.today().strftime('%Y-%m-%d %H:%M:%S')


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "id_request": self.id_request,
            "request_figuras": self.request_figuras,
            "data_envio": self.data_envio,
            "fecha_reg":str (self.fecha_reg)
        }

        return json.dumps(columnas)