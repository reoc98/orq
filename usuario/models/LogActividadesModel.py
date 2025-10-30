import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class LogActividadesModel(base_class):
    __tablename__ = 'log_actividades'

    id = Column(Integer, primary_key = True, nullable=False)
    id_tipo_actividad = Column(Integer, nullable=False)
    entidad = Column(Integer, nullable=False)
    inf_anterior = Column(String, nullable = False)
    inf_actual = Column(String, nullable = False)
    comentario = Column(String, nullable = False)
    usuario = Column(Integer, nullable=False)
    fecha_reg = Column(
        DateTime, nullable = False,  
        server_default = sql.func.now()
    )

    def __init__(self, payload):
        self.id_tipo_actividad = payload['ID_TIPO_ACTIVIDAD']
        self.entidad = payload['ENTIDAD']
        self.inf_anterior = payload['INF_ANTERIOR']
        self.inf_actual = payload['INF_ACTUAL']
        self.comentario = payload['COMENTARIO']
        self.usuario = payload['USUARIO']