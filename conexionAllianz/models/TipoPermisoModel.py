from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, sql, Integer, String, DateTime

base_class = declarative_base()

class TipoPermisoModel(base_class):

	__tablename__ = 'tipo_permiso'

	id = Column(Integer, primary_key = True, nullable = False)
	nombre = Column(String, nullable = False)
	estado = Column(Integer, nullable = False)
	fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())