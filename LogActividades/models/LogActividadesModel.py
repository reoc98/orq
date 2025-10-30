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
        self.id_tipo_actividad = payload['id_tipo_actividad']
        self.entidad = payload['entidad']
        self.inf_anterior = payload['inf_anterior']
        self.inf_actual = payload['inf_actual']
        self.comentario = payload['comentario']
        self.usuario = payload['usuario']

    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "id_tipo_actividad": self.id_tipo_actividad,
            "entidad": self.entidad,
            "inf_anterior": json.loads(self.inf_anterior if self.inf_anterior != '' else '{}'),
            "inf_actual": json.loads(self.inf_actual if self.inf_actual != '' else '{}'),
            "comentario": self.comentario,
            "usuario": self.usuario,
            "fecha_reg": str(self.fecha_reg)
        }

        return json.dumps(columnas)
