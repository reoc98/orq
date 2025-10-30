import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text

class ServiceInif(base_class):
    __tablename__ = 'service_inif'

    id = Column(Integer, primary_key = True)
    id_request_orq = Column(Integer, nullable = False)
    tipo_figura = Column(String, nullable = False)
    numero_documento = Column(Integer, nullable = False)
    figuras = Column(Text, nullable = False)
    status_code = Column(Integer, nullable = False)
    request = Column(Text, nullable = False)
    response = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False, server_default = sql.func.now())
    fecha_creacion = Column(DateTime, nullable = True, server_default = sql.func.now())
    fecha_actualizacion = Column(DateTime, nullable = True)

    def __init__(self, payload: dict):
        self.id_request_orq = payload['id_request_orq']
        self.tipo_figura = payload.get('tipo_figura')
        self.numero_documento = payload.get('numero_documento')
        self.figuras = json.dumps(payload.get('figuras'))
        self.status_code = payload.get('status_code')
        self.request = payload.get('request')
        self.response = payload.get('response')


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "id_request": self.id_request_orq,
            # "figuras": self.figuras,
            "request": self.request
        }

        return json.dumps(columnas)