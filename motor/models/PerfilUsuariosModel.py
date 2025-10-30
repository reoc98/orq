import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, DateTime, sql

class PerfilUsuariosModel(base_class):
    __tablename__ = 'perfil_usuarios'

    id = Column(Integer, primary_key = True, nullable=False)
    id_perfil = Column(Integer, nullable=False)
    id_usuario = Column(Integer, nullable=False)
    estado = Column(Integer, nullable=False)
    usuario = Column(Integer, nullable=False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())

    def __init__(self, payload):
        self.id_perfil = payload['ID_PERFIL']
        self.id_usuario = payload['ID_USUARIO']
        self.estado = 1
        self.usuario = payload['USUARIO']

    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "ID_PERFIL": self.id_perfil,
            "ID_USUARIO": self.id_usuario,
            "ESTADO": self.estado,
            "USUARIO": self.usuario,
            "FECHA_REG": str(self.fecha_reg)
        }
        return json.dumps(columnas)
