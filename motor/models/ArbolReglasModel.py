from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql

class ArbolReglasModel(base_class):
	__tablename__ = 'arbol_reglas'

	id = Column(Integer, primary_key = True, nullable = False)
	arbol_id = Column(Integer, nullable = True)
	variable_id = Column(Integer, nullable = True)
	operacion_id = Column(Integer, nullable = True)
	tipo_comparacion_regla_id = Column(Integer, nullable = True)
	valor = Column(String, nullable = True)
	mensaje_codigo_negativo = Column(String, nullable = True)
	mensaje_codigo_positivo = Column(String, nullable = True)
	activo = Column(Integer, nullable = True)
	fechareg = Column(DateTime, nullable = False, server_default = sql.func.now())
	fecha_update = Column(DateTime, nullable = False, server_default = sql.func.now())