
from utils.Response import Response
from clases.RequestsOrquestador import RequestsOrquestador
from utils.Response import Response
from utils.Aws import Aws, os
import json


class ConexionAllianz (Response):
    # Funcion encargada de realizar el insert del reques y el response 
    # de la peticion entrante

    def insert_orquestador(self,payload):
        response = Response()
        # se arma el payload
        cod_dane = payload.get("cod_dane_circulacion","")
        cod_dane = str(cod_dane).zfill(5)
        cod_departamento = str(cod_dane)[:2]
        
        # Determinamos la fecha y hora combinando los campos que vienen por separado
        fecha_ocurrencia = payload.get("fecha_ocurrencia", None)
        hora_ocurrencia = payload.get("hora_ocurrencia", None)
        fecha_hora_ocurrencia = RequestsOrquestador.validar_fecha_hora(fecha_ocurrencia, hora_ocurrencia)
        person_figures = payload.get('figuras_personas', [])
        payload = {
            "numero_siniestro": payload.get('num_siniestro',""),
            "request":str(payload),
            "cod_ciudad" : payload.get("cod_ciudad_circulacion",""),
            "cod_departamento": cod_departamento,
            "fecha_hora_ocurrencia": fecha_hora_ocurrencia
        }
        requestOrquestador = RequestsOrquestador(payload)
        
        # Se invoca a la funcion encargada realizar el insert
        data = requestOrquestador.insert_requests_orquestador()
        dataUpdate = self.update_orquestador(data)
        #se valida si se actualizo correctamente.
        if (dataUpdate["statusCode"] == 200):

            # obtenemos el id del formulario request
            info_body = json.loads(data["body"])
            id_registro = { 
                "body": { "id": info_body["data"]["ID"] }
            }

            # llamamos la lambda asyncrona
            Aws.lambdaInvoke(
                    'allianz-orq-risk'
                    + '-'+str(os.getenv('STAGE'))
                    + '-risk',
                    id_registro)

            for figure in person_figures:
                print("Invocando servicio INIF para figura:", figure)
                Aws.lambdaInvoke(
                    'conexionAllianz'
                    + '-'+str(os.getenv('STAGE'))
                    + '-service_inif',
                    {
                        'body': {
                            'id_request_orq': info_body['data']['ID'],
                            'figure': figure
                        }
                    }
                )

            return response.armadoBody("Proceso exitoso.", 201)
        else:
            return dataUpdate
        # return data


    # Funcion encargada de actualizar el reponse en casos exitosos
    def update_orquestador(self,data):
        # se define los datos que se van a actualizar
        body = json.loads(data["body"])
        response = {
            "message":body["message"],
            "statusCode":body["statusCode"]
        }
        payload = {
            "response":str(response)
        }
        requestOrquestador = RequestsOrquestador(payload)
        # se obtiene el id de registro a actualizar
        id_registro = body["data"]["ID"]
        data = requestOrquestador.update_requests_orquestador(id_registro)
        # se retorna respuesta
        return data

    # validar si "estado_recibido", se encuentra parametrizado en lista
    def consult_state_received(self, data):
        response = Response()
        not_present = True
        try:
            list = RequestsOrquestador.consult_state_received()
            for i in data["recibos"]:
                if 'estado_recibo' in i:
                    if not(i['estado_recibo'] in list):
                        not_present = i['estado_recibo']
                        break

            if not_present != True:
                return response.armadoBody(f"El campo 'estado_recibo' tiene un valor inválido ({not_present}).", 400)
                
            return response.armadoBody("OK", 200)
        except Exception as error:
            return response.armadoBody("Error interno del servidor.", 500)
 