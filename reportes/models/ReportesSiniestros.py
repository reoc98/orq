from classes.Database import base_class
from sqlalchemy import Column, Integer, Text, DateTime, sql
from datetime import datetime
import json

class ReportesSiniestros(base_class):
    __tablename__ = 'reportes_siniestros'

    id = Column(Integer, primary_key = True)
    id_request = Column(Integer, nullable = False)
    url = Column(Text, nullable = False)
    id_estados_reportes = Column(Integer, nullable = False)
    response = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    # constructor
    def __init__(self, id_request, estado_reportes):
            self.id_request = id_request
            self.id_estados_reportes = estado_reportes
            self.estado = 1
            self.fecha_reg = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "id_request": self.id_request,
            "url": self.url,
            "id_estados_reportes": self.id_estados_reportes,
            "response": self.response,
            "estado":str (self.estado),
            "fecha_reg":str (self.fecha_reg)
        }

        return json.dumps(columnas)
