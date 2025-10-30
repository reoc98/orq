import json
from classes.Database import base_class
from sqlalchemy import Column, Integer, DateTime, sql

class PerfilPermisosModel(base_class):
    __tablename__ = 'perfil_permisos'

    id = Column(Integer, primary_key = True)
    id_permiso = Column(Integer, nullable = False)
    id_perfil = Column(Integer, nullable = False)
    estado = Column(Integer, nullable = False)
    usuario = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())

    def __repr__(self)->str:
        columnas = {
            "ID": self.id,
            "ID_PERMISO": self.id_permiso,
            "ID_PERFIL": self.id_perfil,
            "ESTADO": self.estado,
            "USUARIO": self.usuario,
            "FECHA_REG": str(self.fecha_reg)
        }

        return json.dumps(columnas)
