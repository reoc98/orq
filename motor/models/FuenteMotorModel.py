from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, sql, Integer, String, DateTime
import json

base_class = declarative_base()

class FuenteMotorModel(base_class):

	__tablename__ = "fuente_motor"

	id = Column(Integer, primary_key=True, nullable = False)
	nombre = Column(String, nullable = False)
	valor = Column(Integer, nullable = False)
	estado = Column(Integer, nullable = False)
	fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())

	def __repr__(self)->str:
		columns = {
			"id": self.id,
			"nombre": self.nombre,
		}

		return json.dumps(columns)