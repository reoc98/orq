import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, DateTime, sql

class RecuperarContrasenaModel(base_class):
    __tablename__ = 'recuperar_contrasena'

    id = Column(Integer, primary_key = True)
    id_usuario = Column(Integer, nullable = False)
    email_id = Column(Integer, nullable = True)
    estado = Column(Integer, default=1)
    fecha_reg = Column(DateTime, nullable = False, 
        server_default = sql.func.now())

    def __init__(self, payload):
        self.id_usuario = payload['ID_USUARIO']

    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "ID_USUARIO": self.id_usuario,
            "ESTADO": self.estado,
            "FECHA_REG":str (self.fecha_reg)
        }

        return json.dumps(columnas)

   