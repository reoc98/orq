from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, sql, Integer, String, Text, DateTime
import json

base_class = declarative_base()

class ListaRiskModel(base_class):

	__tablename__ = "lista_risk"

	id = Column(Integer, primary_key=True, nullable = False)
	lista = Column(String, nullable = False)
	descripcion = Column(Text, nullable = True)
	estado = Column(Integer, nullable = False)
	fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())

	def __repr__(self)->str:
		columns = {
			"id": self.id,
			"nombre": self.lista,
			"descripcion": self.descripcion
		}

		return json.dumps(columns)