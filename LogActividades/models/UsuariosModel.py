import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class UsuariosModel(base_class):
    __tablename__ = 'usuarios'

    id = Column('id', Integer, primary_key = True, nullable=False)
    codigo_ce = Column('codigo_ce', Integer, nullable=False)
    nombres = Column('nombres', String(100), nullable=False)
    apellidos = Column('apellidos', String(100), nullable=False)
    fullname = sql.func.concat(
        nombres, ' ', sql.func.coalesce(apellidos, ''))
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
        self.codigo_ce = payload['codigo_ce']
        self.nombres = payload['nombres']
        self.apellidos = payload['apellidos']
        self.email = payload['email']
        self.estado = payload['estado']
        self.usuario = payload['usuario']
    
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
