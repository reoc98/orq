from clases.Database import base_class
from sqlalchemy import Column, Integer, DateTime, sql

class PerfilUsuariosModel(base_class):
    __tablename__ = 'perfil_usuarios'

    id = Column(Integer, primary_key = True, nullable=False)
    id_perfil = Column(Integer, nullable=False)
    id_usuario = Column(Integer, nullable=False)
    estado = Column(Integer, nullable=False)
    usuario = Column(Integer, nullable=False)
    fecha_reg = Column(
        DateTime, nullable = False,  
        server_default = sql.func.now()
    )