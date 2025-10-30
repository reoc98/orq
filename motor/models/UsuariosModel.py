import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class UsuariosModel(base_class):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key = True, nullable=False)
    codigo_ce = Column(String(15), nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100))
    estado = Column(Integer, nullable=False)
    verificado = Column(Integer, default=0)
    usuario = Column(Integer, nullable=False)
    fecha_reg = Column(
        DateTime, nullable = False,  
        server_default = sql.func.now()
    )

    def __init__(self, payload):
        self.codigo_ce = payload['CODIGO_CE']
        self.nombres = payload['NOMBRES']
        self.apellidos = payload['APELLIDOS']
        self.email = payload['EMAIL']
        self.estado = payload['ESTADO']
        self.usuario = payload['USUARIO']

    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "CODIGO_CE": self.codigo_ce,
            "NOMBRES": self.nombres,
            "APELLIDOS": self.apellidos,
            "EMAIL": self.email,
            "FECHA_REG": str(self.fecha_reg)
        }
        return json.dumps(columnas)