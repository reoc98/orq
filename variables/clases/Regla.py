
from utils.Response import Response
from clases.Database import Database
from models.ReglaVariableModel import ReglaVariableModel
from models.RequestsOrquestadorModel import RequestsOrquestadorModel
from models.ReglaLogModel import ReglaLog
from models.RiskConsulta import RiskConsulta
from models.PolizasActivas import PolizasActivas
from models.ServiceInif import ServiceInif
from utils.Response import Response
import json


# Clase cuya funcion es ejecutar y proceder con las reglas
# para devolver las variables correspondientes
class Regla (Response):

    # Funcion construsctor de la clase.
    def __init__(self):
        pass

    # Funcion encargada de obtener y ejecutar la regla
    def obtenerRegla(self, payload):
        db = Database('dbr')
        try:
            regla = db.session.query(ReglaVariableModel).filter_by(id = payload['id_regla']).first()
            request = db.session.query(RequestsOrquestadorModel).filter_by(id = payload['id_request_orquestador']).first()
            
            if request:
                if regla:
                    data_json = json.loads(request.request.replace("\'", "\""))

                    # Se obtiene la condicion de la regla
                    condicion = regla.condicion

                    # regla a un array especifico
                    if regla.id_tipo_regla == 1:
                        data = data_json.get(regla.array_obtener)
                    # Regla mixta general y un array
                    elif regla.id_tipo_regla == 2:
                        # obtenemos primero la condicion del general
                        condicion = ReglaVariableModel.getTextReemplazar(condicion, data_json)
                        data = data_json.get(regla.array_obtener)
                    else:
                        data_response = {'condicion':"",'data':[]}

                    data_response = ReglaVariableModel.reemplazar(condicion, data, regla.sufijo)
                else:
                    data_response = {'condicion':"",'data':[]}
            else:
                data_response = {'condicion':"",'data':[]}

            return data_response
        finally:
            db.session.invalidate()
            db.session.close()
    
    # guardamos el log
    def guardarLogs(self, payload, response, condicion = ""):
        db = Database('dbw')
        try:
            datos = {
                "request": json.dumps(payload),
                "response": json.dumps(response),
                "condicion": str(condicion)
            }
            ##Prepara los datos para insertarlos
            row = ReglaLog(datos)
            ##Bincula los datos
            db.session.add(row)
            ##Envia los datos a la DB
            db.session.commit()
        finally:
            db.session.invalidate()
            db.session.close()

    # Funcion encargada de obtener y ejecutar la regla de risk
    def obtenerReglaRisk(self, payload):
        db = Database('dbr')
        try:
            regla = db.session.query(ReglaVariableModel).filter_by(id = payload['id_regla']).first()
            request = db.session.query(RequestsOrquestadorModel).filter_by(id = payload['id_request_orquestador']).first()
            
            # hacemos las validaciones si existen las reglas y request
            if request:
                if regla:
                    # validamos que la regla no este vacia
                    if regla.condicion:
                        # si la regla es del tipo requerido
                        if regla.id_tipo_regla == 3:
                            # obtenemos los datos de la consulta de risk
                            consulta = db.session.query(RiskConsulta).filter_by(
                                        tipo_figura = regla.array_obtener).filter_by(
                                        estado = 1).filter_by(
                                        id_request = request.id).first()
                            if consulta:
                                data_json = json.loads(consulta.data_response.replace("\'", "\""))

                                if 'tieneResultados' in data_json:

                                    # Se obtiene la condicion de la regla
                                    condicion = regla.condicion

                                    # solo aplicamos reglas especificas
                                    data = data_json.get("resultados",[])

                                    data_response = ReglaVariableModel.reemplazar(condicion, data)
                                else:
                                    data_response = {'condicion':"",'data':[]}
                            else:
                                data_response = {'condicion':regla.array_obtener,'data':[]}
                        else:
                            raise Warning('Tipo de regla no permitido.')
                    else:
                        raise Warning('La regla esta vacia.')
                else:
                    data_response = {'condicion':"",'data':[]}
            else:
                data_response = {'condicion':"",'data':[]}

            return data_response
        finally:
            db.session.invalidate()
            db.session.close()

    # se encarga de validar si la poliza existe o no
    def consultarPoliza(self, payload):
        db = Database('dbr')
        try:
            regla = db.session.query(PolizasActivas).filter_by(
                    numero_poliza = payload['numero_poliza']).filter_by(estado = 1).first()
            
            return regla
        finally:
            db.session.invalidate()
            db.session.close()

    @staticmethod
    def get_response_inif(payload: dict):
        session = Database('dbr').session
        try:
            rule = session.query(ReglaVariableModel).filter_by(id=payload['id_regla']).first()
            request = session.query(RequestsOrquestadorModel).filter_by(id=payload['id_request_orquestador']).first()
            if not request or not rule:
                return {'condicion': "", 'data': []}
            
            if rule.id_tipo_regla != 4:
                return {'condicion': "", 'data': []}
            
            service_inif = session.query(
                ServiceInif.id,
                ServiceInif.response
            ).filter_by(
                tipo_figura=rule.array_obtener,
                id_request_orq=request.id,
                estado=1,
                # status_code=200
            ).order_by(ServiceInif.id.desc()).first()
            if not service_inif:
                print("No se encontró registro en ServiceInif")
                return {'condicion': rule.array_obtener, 'data': []}

            data_response = json.loads(service_inif.response.replace("\'", "\""))
            if not data_response or not isinstance(data_response, list) or len(data_response) == 0:
                return {'condicion': rule.array_obtener, 'data': []}
            
            data_response = data_response[0]
            response = {
                'identity': data_response.get('input', {}).get('identity',''),
                'typeId': data_response.get('input', {}).get('typeId',''),
                'docNum': data_response.get('input', {}).get('docNum',''),
                'generalScore': data_response.get('generalScore',''),
                'generalRiskLevel': data_response.get('generalRiskLevel',''),
                'generalInfo': data_response.get('generalInfo',''),
                'score': data_response.get('riskResult',{}).get('score',''),
                'riskLevel': data_response.get('riskResult',{}).get('riskLevel','')
            }
            # response = ReglaVariableModel.reemplazar(rule.condicion, data_response)
            return {'condicion': rule.condicion, 'data': response}
        finally:
            session.invalidate()
            session.close()