from clases.Database import base_class
from sqlalchemy import Column, Integer, Text, DateTime, sql
from datetime import datetime
import json
class RequestsEnviados(base_class):
    __tablename__ = 'requests_enviados'

    id = Column(Integer, primary_key = True)
    id_request = Column(Integer)
    id_response  = Column(Integer, nullable = False)
    servicio = Column(Text, nullable = False)
    status_code  = Column(Integer, nullable = False)
    response = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "id_request": self.id_request,
            "id_response": self.id_response,
            "servicio": self.servicio,
            "status_code": self.status_code,
            "response": self.response,
            "estado": self.estado
        }

        return json.dumps(columnas)
