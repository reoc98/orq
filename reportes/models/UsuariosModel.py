import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class UsuariosModel(base_class):
    __tablename__ = 'usuarios'

    id = Column('id', Integer, primary_key = True, nullable=False)
    codigo_ce = Column('codigo_ce', Integer, nullable=False)
    nombres = Column('nombres', String(100), nullable=False)
    apellidos = Column('apellidos', String(100), nullable=False)
    email = Column('email', String(100), nullable=False)
    password = Column('password', String(100))
    estado = Column('estado', Integer, nullable=False)
    verificado = Column('verificado', Integer, default=0)
    usuario = Column('usuario', Integer, nullable=False)
    fecha_reg = Column('fecha_reg',
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
            "PASSWORD": self.password,
            "ESTADO": self.estado,
            "VERIFICADO": self.verificado,
            "USUARIO": self.usuario,
            "FECHA_REG": str(self.fecha_reg)
        }

        return json.dumps(columnas)
