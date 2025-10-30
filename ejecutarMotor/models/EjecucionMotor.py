from clases.Database import base_class
from sqlalchemy import Column, Integer, Text, DateTime, sql
from datetime import datetime

class EjecucionMotor(base_class):
    __tablename__ = 'ejecucion_motor'

    id = Column(Integer, primary_key = True)
    id_request = Column(Integer, nullable = False)
    id_arbol = Column(Integer, nullable = False)
    codigo_arbol = Column(Text, nullable = False)
    figura = Column(Text, nullable = False)
    datos_request = Column(Text, nullable = False)
    datos_response = Column(Text, nullable = False)
    desenlace_contenido = Column(Text, nullable = False)
    estado = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())
    fecha_upd = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, id_request, id_arbol, figura, codigo_arbol):
        self.id_request = id_request
        self.id_arbol = id_arbol
        self.figura = figura
        self.codigo_arbol = codigo_arbol
        self.estado = 0
        self.fecha_reg = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
