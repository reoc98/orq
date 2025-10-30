from utils.Response import Response
from utils.Validations import Validations
# from os import environ as os_environ
from os import environ as os_environ
from clases.Cognito import Cognito
from clases.RequestsOrquestador import RequestsOrquestador 
from clases.ConexionAllianz import ConexionAllianz 
from entity.ConexionAllianzEntity import ConexionAllianzEntity

responseData = Response()
validate = Validations()
conexionAllianzEntity = ConexionAllianzEntity()
conexionAllianz = ConexionAllianz()



# Funcion del handler que se encarga de recibir los datos
# e insertarlos en la base de datos
def receive_request(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            token_header = validate.get_token_header(event['headers'])

            # Buscamos la informacion del usario en cognito por medio de AccessToken
            cognito = Cognito()
            data_user = cognito.get_user_by_token(token_header)

            # Teniendo la información del usuario, buscamos el Email
            email_user = None
            attributes = data_user.get("UserAttributes", [])
            for attribute in attributes:
                if attribute['Name'] == 'email':
                    email_user =  attribute['Value']
                    break

            if email_user is None:
                raise Warning("Error interno con el usuario.")
            
            # Consultamos el permiso de ENVIAR_RQ con el correo de este usuario 
            permiso = RequestsOrquestador.consult_permission(email_user)
            if permiso is None:
                return responseData.armadoBody("No cuenta con los permisos necesarios para realizar esta operación.", 403)

            payload = response['data']
            keysRule = conexionAllianzEntity.keyRules('receive_request')

            # se validan los datos.
            response = validate.validateInput(payload, keysRule)

            if response["statusCode"] == 200:
                # se extraen las listas del payload
                datos = {
                    "garantias":payload.get("garantias",[]),
                    "figuras_personas":payload.get("figuras_personas",[]),
                    "recibos":payload.get("recibos",[]),
                    "figuras_vehiculo":payload.get("figuras_vehiculo",[]),
                }

                # Obtenemos el npumero de siniestro
                num_siniestro = payload.get("num_siniestro",0)
                
                # Determinamos la fecha y hora combinando los campos que vienen por separado
                fecha_ocurrencia = payload.get("fecha_ocurrencia", None)
                hora_ocurrencia = payload.get("hora_ocurrencia", None)
                fecha_hora_ocurrencia = RequestsOrquestador.validar_fecha_hora(fecha_ocurrencia, hora_ocurrencia)

                # Obtenemos ciu_ocurrencia y dep_ocurrencia
                dep_ocurrencia = payload.get("dep_ocurrencia","")
                dep_ocurrencia = str(dep_ocurrencia).zfill(2) # agrega siempre un 0 a la izquierda
                dep_ocurrencia = str(dep_ocurrencia)[:2]
                ciu_ocurrencia = payload.get("ciu_ocurrencia","")
                ciu_ocurrencia = str(ciu_ocurrencia).zfill(5)
                ciu_dep_ocurrencia = str(ciu_ocurrencia)[:2]
                ciu_ocurrencia = str(ciu_ocurrencia)[-3:]

                ocurrencia=RequestsOrquestador.validate_city_code(ciu_ocurrencia, dep_ocurrencia)
                if not ocurrencia:
                    ocurrencia = None
                else:
                    ocurrencia=RequestsOrquestador.validate_city_code(ciu_ocurrencia, ciu_dep_ocurrencia)
                    if not ocurrencia:
                        ocurrencia = None
                
                if not (len(str(payload.get("ciu_ocurrencia",""))) >= 4 and len(str(payload.get("ciu_ocurrencia",""))) <= 5):
                    ocurrencia = None

                # Obtenemos cod_ciudad y cod_departamento
                cod_dane = payload.get("cod_dane_circulacion","")
                cod_dane = str(cod_dane).zfill(5) # agrega siempre un 0 a la izquierda
                cod_departamento = str(cod_dane)[:2]
                cod_ciudad_departamento = payload.get("cod_ciudad_circulacion","")
                cod_ciudad_departamento = str(cod_ciudad_departamento).zfill(5)
                cod_ciudad = str(cod_ciudad_departamento)[-3:]
                if cod_ciudad_departamento == cod_dane:
                    city=RequestsOrquestador.validate_city_code(cod_ciudad, cod_departamento)
                else:
                    city = None
                # cod_ciudad = payload.get("cod_ciudad_circulacion","")

                # se validan las listas
                validaLists = conexionAllianzEntity.validaList(datos)
                validad_cantidad = conexionAllianzEntity.validar_cantidad_tipo_figura(payload, 'figuras_personas')
                
                if validad_cantidad == True:
                    validad_cantidad = conexionAllianzEntity.validar_cantidad_tipo_figura(payload, 'figuras_vehiculo')

                response = validaLists["response"]
                
                # Validamos si el tipo de documento ingresado es permitido
                val_tipo_documento = True
                for figura_persona in datos['figuras_personas']:
                    if figura_persona.get('tipo_doc_figura', False) != False:
                        if figura_persona['tipo_doc_figura'] != "": 
                            tipo_documento=RequestsOrquestador.buscar_tipo_documento(figura_persona['tipo_doc_figura'])
                            if tipo_documento is None:
                                val_tipo_documento = f"El valor '{figura_persona['tipo_doc_figura']}' en el campo 'tipo_doc_figura' no es válido."
                                break
                    else:
                        val_tipo_documento = "Ha ingresado una figura persona que no tiene el campo 'tipo_doc_figura'."
                        break
                
                if validaLists["validate"] and (city is not None) and (cod_ciudad_departamento == cod_dane) and \
                    validad_cantidad == True and (val_tipo_documento == True) and ocurrencia is not None \
                    and fecha_hora_ocurrencia is not None:

                    payload["cod_ciudad_circulacion"] = cod_ciudad
                    payload["ciu_ocurrencia"] = ciu_ocurrencia
                    payload["dep_ocurrencia"] = dep_ocurrencia
                    # validamos los intervinientes repetidos
                    valida_intervinientes = conexionAllianzEntity.validaInterviniente(datos)
                    response = valida_intervinientes["response"]
                    if valida_intervinientes["validate"]:
        
                        validation_reveived = conexionAllianz.consult_state_received(datos)
                        if(validation_reveived['statusCode']==200):
                            # Se invoca a la funcion encargada realizar el insert
                            response = conexionAllianz.insert_orquestador(payload)

                        else:
                            response = validation_reveived
                            payload = {
                                "numero_siniestro": num_siniestro,
                                "cod_ciudad": cod_ciudad,
                                "cod_departamento": cod_departamento,
                                "fecha_hora_ocurrencia": fecha_hora_ocurrencia,
                                "request":str(payload),
                                "response":str(response),
                                "estado":0
                            }
                            requestOrquestador = RequestsOrquestador(payload)

                            # Se invoca a la funcion encargada realizar el insert
                            requestOrquestador.insert_requests_orquestador()
                    else:
                        payload = {
                            "numero_siniestro": num_siniestro,
                            "cod_ciudad": cod_ciudad,
                            "cod_departamento": cod_departamento,
                            "fecha_hora_ocurrencia": fecha_hora_ocurrencia,
                            "request":str(payload),
                            "response":str(response),
                            "estado":0
                        }
                        requestOrquestador = RequestsOrquestador(payload)

                        # Se invoca a la funcion encargada realizar el insert
                        requestOrquestador.insert_requests_orquestador()
                else:
                    if cod_ciudad_departamento != cod_dane:
                        response = responseData.armadoBody("Los campos 'cod_dane_circulacion' y 'cod_ciudad_circulacion' tienen diferente valor.", 400)
            
                    elif city is None:
                        response = responseData.armadoBody("Ha ingresado un código de ciudad inválido para el campo 'cod_ciudad_circulacion'.", 400)
                    elif (val_tipo_documento != True):
                        response = responseData.armadoBody(val_tipo_documento, 400)
                    elif validad_cantidad != True:
                        response = responseData.armadoBody(validad_cantidad, 400)
                    elif fecha_hora_ocurrencia is None:
                        response = responseData.armadoBody("La fecha y/u hora de ocurrencia ingresada no es válida.", 400)
                    elif ocurrencia is None:
                        response = responseData.armadoBody("Ha ingresado un código inválido para el campo 'dep_ocurrencia' y/o 'ciu_ocurrencia'.", 400)

                    payload = {
                        "numero_siniestro": num_siniestro,
                        "cod_ciudad": cod_ciudad,
                        "cod_departamento": cod_departamento,
                        "fecha_hora_ocurrencia": fecha_hora_ocurrencia,
                        "request":str(payload),
                        "response":str(response),
                        "estado":0
                }
                    requestOrquestador = RequestsOrquestador(payload)
                        
                    # Se invoca a la funcion encargada realizar el insert
                    requestOrquestador.insert_requests_orquestador()

            else: 
                # Obtenemos el npumero de siniestro
                num_siniestro = payload.get("num_siniestro",0)

                # Obtenemos cod_ciudad y cod_departamento
                cod_dane = payload.get("cod_dane_circulacion","")
                cod_dane = str(cod_dane).zfill(5)
                cod_departamento = str(cod_dane)[:2]
                cod_ciudad_departamento = payload.get("cod_ciudad_circulacion","")
                cod_ciudad_departamento = str(cod_ciudad_departamento).zfill(5)
                cod_ciudad = str(cod_ciudad_departamento)[-3:]

                # Determinamos la fecha y hora combinando los campos que vienen por separado
                fecha_ocurrencia = payload.get("fecha_ocurrencia", None)
                hora_ocurrencia = payload.get("hora_ocurrencia", None)
                fecha_hora_ocurrencia = RequestsOrquestador.validar_fecha_hora(fecha_ocurrencia, hora_ocurrencia)

                payload = {
                    "numero_siniestro": num_siniestro,
                    "cod_ciudad": cod_ciudad,
                    "cod_departamento": cod_departamento,
                    "fecha_hora_ocurrencia": fecha_hora_ocurrencia,
                    "request":str(payload),
                    "response":str(response),
                    "estado":0
                }
                requestOrquestador = RequestsOrquestador(payload)
                    
                # Se invoca a la funcion encargada realizar el insert
                requestOrquestador.insert_requests_orquestador()

        return response
    except ValueError as error:
        return responseData.armadoBody(f"{error}", 400)
    except Exception as error:
        return responseData.armadoBody(str(error), 500)

# Funcion del handler que se encarga de recibir los datos e invocar a
# la funcion que consume el servicio de crear token.
def get_tokens_orquestador(event, context):
    # Se reciben los datos que vienen en el body.
    response = validate.json_validator(event['body'])
    if response["statusCode"] == 200:
        data = response['data']
        client_id = os_environ.get("COGNITO_CLIENT_ID", "")
        keysRule = conexionAllianzEntity.keyRules('get_tokens_orquestador')
        response = validate.validateInput(data, keysRule)
        if response["statusCode"] == 200:
            # se instancia la clase cognito
            cognito = Cognito(client_id)
            response = cognito.get_tokens(data)

    return response
