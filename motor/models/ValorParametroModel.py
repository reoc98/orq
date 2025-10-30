from clases.Database import base_class
from sqlalchemy import Column, Integer, String, Text

class ValorParametroModel(base_class):
	__tablename__ = 'valor_parametro'

	id = Column(Integer, primary_key = True)
	codigo = Column(String, nullable = False)
	descripcion = Column(Text, nullable = False)
	valor = Column(String, nullable = False)
	modulo = Column(Integer, nullable = True)
	estado = Column(Integer, nullable = False)

	def __repr__(self)->str:
		return self.valor