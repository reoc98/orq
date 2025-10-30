from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class ArbolVariablesModel(base_class):
	__tablename__ = 'arbol_variables'

	id = Column(Integer, primary_key = True, nullable = False)
	tipo_variable_id = Column(Integer, nullable = True)
	tipo_dato_id = Column(Integer, nullable = True)
	unidad_id = Column(Integer, nullable = True)
	codigo = Column(String, nullable = False)
	nombre = Column(String, nullable = True)
	descripcion = Column(String, nullable = True)
	tabla_id = Column(Integer, nullable = True)
	limite_caracteres = Column(Integer, nullable = True)
	fin = Column(Integer, nullable = True)
	activo = Column(Integer, nullable = True)
	fechareg = Column(DateTime, nullable = False, server_default = sql.func.now())
	fecha_update = Column(DateTime, nullable = False, server_default = sql.func.now())