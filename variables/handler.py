
import json
from utils.Response import Response
from utils.Validations import Validations
from clases.Regla import Regla 
from entity.VariableEntity import VariableEntity

responseData = Response()
validate = Validations()
VariableEntity = VariableEntity()
Regla = Regla()


# Funcion del handler que se encarga llamar a la ejecucion de la regla
def variable(event, context):    
    try:
        response_info = validate.json_validator(event["body"])
        if response_info["statusCode"] == 200:
            # validamos el json de entrada
            try:
                if event['body'] is None:
                    raise Exception("Cuerpo de la peticion invalido.")
                payload = response_info['data']
            except Exception:
                raise Exception("Cuerpo de la peticion invalido.")

            keysRule = VariableEntity.keyRules('receive_request')

            # se validan los datos.
            response = validate.validateInput(payload, keysRule)
            if response["statusCode"] == 200:

                try:
                    # Se llama a la regla
                    resp = Regla.obtenerRegla(payload)
                    # validamos si fue exitoso
                    if resp['data']:
                        response_info = responseData.armadoBody("Proceso exitoso.", 201, resp['data'])
                    else:
                        response_info = responseData.armadoBody("No se encontraron datos.", 404, [])
                except Exception as error:
                    Regla.guardarLogs(payload,str(error))
                    return responseData.armadoBody(str(error), 400)

                # guardamos el log
                Regla.guardarLogs(payload,response_info,resp['condicion'])
            else: 
                response_info = response
                Regla.guardarLogs(payload,response)

        return response_info

    except Exception as error:
        return responseData.armadoBody(str(error), 400)

# Funcion que se encarga entregar la variable de risk
def variableRisk(event, context):    
    try:
        response_info = validate.json_validator(event["body"])
        if response_info["statusCode"] == 200:
            # validamos el json de entrada
            try:
                if event['body'] is None:
                    raise Exception("Cuerpo de la peticion invalido.")
                payload = response_info['data']
            except Exception:
                raise Exception("Cuerpo de la peticion invalido.")

            keysRule = VariableEntity.keyRules('receive_request')

            # se validan los datos.
            response = validate.validateInput(payload, keysRule)
            if response["statusCode"] == 200:

                try:
                    # Se llama a la regla
                    resp = Regla.obtenerReglaRisk(payload)
                    # validamos si fue exitoso
                    if resp['data']:
                        response_info = responseData.armadoBody("Proceso exitoso.", 201, resp['data'])
                    else:
                        response_info = responseData.armadoBody("No se encontraron datos.", 404, [])
                except Warning as error:
                    Regla.guardarLogs(payload,str(error))
                    return responseData.armadoBody(str(error), 400)
                except Exception as error:
                    Regla.guardarLogs(payload,str(error))
                    return responseData.armadoBody(str(error), 400)

                # guardamos el log
                Regla.guardarLogs(payload,response_info,resp['condicion'])
            else: 
                response_info = response
                Regla.guardarLogs(payload,response)

        return response_info

    except Exception as error:
        return responseData.armadoBody(str(error), 400)

# funcion encargada de validar si una poliza existe o no
def validarPoliza(event, context): 
    try:
        response = validate.json_validator(event["body"])
        if response["statusCode"] == 200:
            # validamos el json de entrada
            try:
                if event['body'] is None:
                    raise Exception("Cuerpo de la peticion invalido.")
                payload = response['data']
            except Exception:
                raise Exception("Cuerpo de la peticion invalido.")

            keysRule = VariableEntity.keyRules('validar_poliza')

            # se validan los datos.
            response = validate.validateInput(payload, keysRule)
            if response["statusCode"] == 200:

                try:
                    # Se valida si la poliza existe
                    resp = Regla.consultarPoliza(payload)
                    # validamos si fue exitoso
                    if resp:
                        existe = "true"
                    else:
                        existe = "false"
                    data_resp = {
                        "existe": existe
                    }
                    response = responseData.armadoBody("Proceso exitoso.", 201, data_resp)
                except Exception as error:
                    return responseData.armadoBody(str(error), 400)

        return response

    except Exception as error:
        return responseData.armadoBody(str(error), 400)

def get_response_inif(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        keysRule = VariableEntity.keyRules('receive_request')
        response = validate.validateInput(body, keysRule)
        if response["statusCode"] != 200:
            Regla.guardarLogs(body,response)
            return response
        print(f"body: {body}")
        response = Regla.get_response_inif(body)
        if not response.get('data'):
            return responseData.armadoBody("No se encontraron datos.", 404, [])
        return responseData.armadoBody("Proceso exitoso.", 201, response['data'])
    except Exception as error:
        Regla.guardarLogs(body,str(error))
        return responseData.armadoBody(str(error), 400)