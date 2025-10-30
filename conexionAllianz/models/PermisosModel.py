from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime

class PermisosModel(base_class):
    __tablename__ = 'permisos'

    id = Column(Integer, primary_key = True)
    id_modulo = Column(Integer, nullable = False)
    id_tipo_permiso = Column(Integer, nullable = False)
    descripcion = Column(String, nullable = False)
    activo = Column(Integer, nullable = False)
    fecha_reg = Column(DateTime, nullable = False)
