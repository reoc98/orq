from classes.Database import base_class
from sqlalchemy import Column, Integer, Text, DateTime, sql
from datetime import datetime
import json

class ReporteMensualSiniestros(base_class):
    __tablename__ = 'reporte_mensual_siniestro'

    id = Column(Integer, primary_key = True)
    respuesta = Column(Text, nullable = False)
    ruta = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    # constructor
    def __init__(self, payload):
            self.ruta = payload.get("ruta", None)
            self.respuesta = payload.get("respuesta", None)
            self.estado = payload.get("estado", 0)
            self.fecha_reg = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "ruta": self.ruta,
            "respuesta": self.respuesta,
            "estado":str (self.estado),
            "fecha_reg":str (self.fecha_reg)
        }

        return json.dumps(columnas)
