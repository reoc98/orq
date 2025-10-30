from clases.Database import base_class
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