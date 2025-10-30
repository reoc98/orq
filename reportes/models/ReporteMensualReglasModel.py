from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, sql, Integer, Text, String, DateTime
import json

base_class = declarative_base()

class ReporteMensualReglasModel(base_class):

	__tablename__ = 'reporte_mensual_reglas'

	id = Column(Integer, nullable = False, primary_key = True)
	ruta = Column(String, nullable = True)
	request = Column(Text, nullable = True)
	respuesta = Column(Text, nullable = True)
	finalizado = Column(Integer, nullable = False)
	estado = Column(Integer, nullable = False)
	usuario = Column(Integer, nullable = False)
	fecha_reg = Column(DateTime, nullable = False, server_default = sql.func.now())

	def __repr__(self)->str:
		columns = {
			'id': self.id,
			'ruta': self.ruta,
			'respuesta': self.respuesta,
			'estado': self.estado,
			'fecha_reg': str(self.fecha_reg)
		}

		return json.dumps(columns)