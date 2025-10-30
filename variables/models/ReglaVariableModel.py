import json
from clases.Database import base_class
from sqlalchemy import Column, Integer, String, DateTime, sql,Text

class ReglaVariableModel(base_class):
    __tablename__ = 'reglas_variables'

    id = Column(Integer, primary_key = True)
    nombre = Column(String, nullable = False)
    id_tipo_regla = Column(Integer, nullable = False)
    condicion = Column(String, nullable = False)
    array_obtener = Column(String, nullable = False)
    sufijo = Column(String, nullable = False)
    fecha_reg = Column(DateTime, nullable = False,  server_default = sql.func.now())

    def __init__(self, payload):
            self.nombre = payload.get('nombre',"")
            self.id_tipo_regla = payload.get('id_tipo_regla',"")
            self.array_obtener = payload.get('array_obtener',1)


    def __repr__(self)->str:
        columnas = {
            "id": self.id,
            "id_tipo_regla": self.id_tipo_regla,
            "condicion": self.condicion,
            "array_obtener": self.array_obtener,
            "fecha_reg":str (self.fecha_reg)
        }

        return json.dumps(columnas)
    
    # Obtenemos y reemplazamos la condicion con los datos 
    # para asi validar si cumple la condicion
    def reemplazar(condicion, body, sufijo = None):

        # recorremos el array
        for row in body:
            cadena = condicion
            # recorremos cada item del array para reemplazarlo
            for key, valor in row.items():
                cadena = cadena.replace("{"+str(key)+"}",str(valor))
            
            # validamos la regla y controlamos el error
            try:
                if eval(cadena):
                    if sufijo != None:
                        data = {}
                        for key, valor in row.items():
                            data_r = valor
                            if isinstance(data_r, bool):
                                data_r = str(data_r).lower()
                            data[key+"_"+str(sufijo)] = data_r
                        return {'condicion':cadena,'data':data}
                    else:
                        data = {}
                        for key, valor in row.items():
                            data_r = valor
                            if isinstance(data_r, bool):
                                data_r = str(data_r).lower()
                            data[key] = data_r
                        return {'condicion':cadena,'data':data}
            except Exception as error:
                return {'condicion':cadena,'data':error}
        
        return {'condicion':condicion,'data':[]}

    # reemplazamos los datos de la condicion
    # devolvemos la condicion ya reemplazada con los datos
    def getTextReemplazar(condicion, body):
        
        cadena = condicion
        # recorremos el array
        for key, valor in body.items():
            cadena = cadena.replace("{"+str(key)+"}",str(valor))

        return cadena
