from clases.Database import base_class
from sqlalchemy import Column, Integer, Text, DateTime, sql
from datetime import datetime

class ResponseOrquestador(base_class):
    __tablename__ = 'response_orquestador'

    id = Column(Integer, primary_key = True)
    id_request = Column(Integer, nullable = False)
    estructura_envio = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, id_request, estructura_envio):
        self.id_request = id_request
        self.estructura_envio = estructura_envio
        self.estado = 0
        self.fecha_reg = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
