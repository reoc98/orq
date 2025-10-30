import json
from utils.Response import Response
from clases.Ejecucion import Ejecucion 
from clases.Conexion import Conexion

responseData = Response()
Ejecucion = Ejecucion()


from clases.ProcesoMotorC import ProcesoMotorC
from clases.EjecucionMotor import EjecucionMotor


def _buscar_valor_en_estructura(data, clave):
    if isinstance(data, dict):
        if clave in data and data[clave] is not None and data[clave] != "":
            return data[clave]
        for valor in data.values():
            resultado = _buscar_valor_en_estructura(valor, clave)
            if resultado is not None and resultado != "":
                return resultado
    elif isinstance(data, list):
        for item in data:
            resultado = _buscar_valor_en_estructura(item, clave)
            if resultado is not None and resultado != "":
                return resultado
    return None


def _parse_numero_documento(valor):
    if valor is None:
        return None
    try:
        return int(str(valor))
    except (ValueError, TypeError):
        return None


# funcion que envia las lambda asyncriona a los motores
def ProcesoMotor(event, context):
 
    try:
        proceso_motor = ProcesoMotorC()
        return proceso_motor.procesar_siniestros()

    except Exception as error:
        respt = responseData.armadoBody(str(error), 400)
        return respt

# funcion que llama al servicio del motor
def ejecucionMotor(event, context):

    try:
        id_request = event['id_request']

        ejecucion_motor = EjecucionMotor()
        return ejecucion_motor.ejecutar_request(id_request)

    except Exception as error:
        respt = responseData.armadoBody(str(error), 400)
        return respt

# validamos que los procesos de los motores esten terminados
def validarMotor(event, context):

    try:
        # Obtenemos los motores a validar
        motores = Ejecucion.obtenerRequestOrq(1)
        # se valida que tenga registro
        if motores != None:

            # recorremos los motores pendiente para validar
            for info in motores:

                total_request = Ejecucion.obtenerPorIdEjecucion(info.id)

                for ejecucion in total_request:
                    if not(responseData.json_validator(ejecucion.datos_response)):
                        ejecucion.estado = 0
                        Ejecucion.reintentar_ejecucion(ejecucion)

                total_consultados = Ejecucion.obtenerPorIdEjecucion(info.id, 1)

                if total_request != None:
                    if len(total_request) == len(total_consultados) and len(total_request) > 0:
                        Ejecucion.actualizarEstadoRequest(info.id, 3)                    
                    else:
                        Ejecucion.actualizarEstadoRequest(info.id, 0)
                       

            response = responseData.armadoBody("Ok", 200)
        else:
            response = responseData.armadoBody("No se encontró ningún registro", 404)

        return response

    except Exception as error:
        respt = responseData.armadoBody(str(error), 400)
        return respt

# Construir el json para enviar a allianz
def enviarMotor(event, context):
    try:
        # Obtenemos los request a validar aquellos en EJECUCION = 3
        requests = Ejecucion.obtenerRequestOrq(3)

        # Validamos la cantidad de Requests
        if len(requests)==0:
            return responseData.armadoBody("No se encontró ningún Request", 404)

        # Se recorren los Requests
        for row in requests:
            # Obtenemos los datos del request para el numero del siniestro
            datos = {}
            datos["num_siniestro"] = row.numero_siniestro
            id_request = row.id

            # Obtenemos los motores ejecutados bajo este Request
            motores_ejecutados = Ejecucion.motores_ejecucion_request(id_request, 1)
            array = []

            # construimos la informacion recopilada del motor y la estructuramos
            for motor in motores_ejecutados:
                estructura = {}
                # motor = Ejecucion.obtenerNombreMotor(motor.id_arbol)
                if motor != None:
                    # Se inicializan parametros por defecto
                    estructura["comentarios"] = ""
                    estructura["semaforo"] = 0
                    estructura["tipo_interviniente"] = ""
                    estructura["nombre_figura"] = ""

                    figura = {}
                    numero_documento = None
                    tipo_figura_inif = motor.tipo

                    try:
                        figura = json.loads(motor.figura.replace("\'", "\""))
                        numero_documento = figura.get("num_doc_figura") or figura.get("numero_documento") or figura.get("docNum")
                        tipo_figura_inif = figura.get("tipo_figura", tipo_figura_inif)
                    except Exception:
                        figura = {}

                    if motor.activo == 1:
                        # Validamos si el arbol_arbol de ejecucion contiene "variable_comentario"
                        if motor.variable_comentario is not None and motor is not None and motor.variable_comentario != "":
                            # Asignamos variables a trabajar
                            variable_motor = motor.variable_comentario
                            datos_request = json.loads(motor.datos_request.replace("\'", "\""))

                            valor_comentario = ""

                            if motor.tipo == "Asegurado" or motor.tipo == "Conductor":
                                # Determinamos el listado donde buscaremos la variable
                                tipo_figura = "figuras_vehiculo" if motor.vehiculo == 1 else "figuras_personas"

                                # Recorremos el listado
                                for lista in datos_request['datos_front'][tipo_figura]:
                                    # Validamos el tipo de figura con el tipo del arbol
                                    if(lista['tipo_figura'] == motor.tipo):
                                        if numero_documento is None:
                                            numero_documento = lista.get('num_doc_figura') or lista.get('numero_documento') or lista.get('docNum')
                                        valor_comentario = lista.get(variable_motor, "")
                                        if valor_comentario is None:
                                            valor_comentario = ""
                                        if valor_comentario != "":
                                            estructura["comentarios"] = f"{variable_motor}: {valor_comentario}"
                                        break

                            # Para tipo "Siniestro" e "Interviniente", buscamos en el nivel superior del JSON en "datos_front"
                            else:
                                valor_comentario = datos_request['datos_front'].get(variable_motor, "")
                                if valor_comentario is None:
                                    valor_comentario = ""
                                if valor_comentario != "":
                                    estructura["comentarios"] = f"{variable_motor}: {valor_comentario}"

                            if estructura["comentarios"] == "" and variable_motor != "":
                                numero_documento = _parse_numero_documento(numero_documento)
                                if numero_documento is None and figura:
                                    numero_documento = _parse_numero_documento(
                                        figura.get('num_doc_figura')
                                        or figura.get('numero_documento')
                                        or figura.get('docNum')
                                    )

                                if numero_documento is not None and tipo_figura_inif is not None:
                                    servicio_inif = Ejecucion.obtener_service_inif(id_request, tipo_figura_inif, numero_documento)
                                    if servicio_inif is not None and servicio_inif.response is not None:
                                        try:
                                            data_inif = json.loads(servicio_inif.response.replace("\'", "\""))
                                        except Exception:
                                            data_inif = None

                                        if isinstance(data_inif, list) and len(data_inif) > 0:
                                            data_inif = data_inif[0]

                                        if isinstance(data_inif, (dict, list)):
                                            valor_inif = _buscar_valor_en_estructura(data_inif, variable_motor)
                                            if valor_inif is not None and valor_inif != "":
                                                estructura["comentarios"] = f"{variable_motor}: {valor_inif}"

                        # obtenemos la informacion de desenlace contenido
                        if motor.desenlace_contenido is not None:
                            desenlace = json.loads(motor.desenlace_contenido.replace("\'", "\""))
                            # Validando los valores para "semaforo" y asigmanos a la estrucutra
                            if desenlace != None and "semaforo" in desenlace:
                                estructura["semaforo"] = int(desenlace["semaforo"])

                    elif motor.activo == 0:
                        estructura["comentarios"] = "Este motor ha sido eliminado."
                        estructura["semaforo"] = 0

                    if motor['vehiculo'] == 0 and isinstance(figura, dict):
                        estructura["tipo_interviniente"] = figura.get("tipo_interviniente", "")
                        estructura["nombre_figura"] = figura.get("nombre_figura", "")
                    elif isinstance(figura, dict):
                        if figura.get("tipo_figura") == "Interviniente":
                            estructura["tipo_interviniente"] = "contrario"
                        else:
                            estructura["tipo_interviniente"] = ""
                        estructura["nombre_figura"] = figura.get("placa", "")

                    # estructuramos los datos de acuerdo al envio
                    estructura["tipo_figura"] = motor["tipo"]
                    estructura["nombre_regla"] = motor['nombre']
                    # agregamos la estructura al array
                    array.append(estructura)
            datos["figura"] = array
            # guardamos el json armado
            data_envio = Ejecucion.guardarEstructura(id_request, datos)

            Ejecucion.enviar_motor(data_envio['id'], row.id)
               
        response = responseData.armadoBody("Ok", 200)
        return response

    except Exception as error:
        respt = responseData.armadoBody(str(error), 400)
        return respt

# Lambda Asincrinica para Enviar la respuesta de cada Request por separada
def consumo_motor(event, context):
    try:
        id_response = event['id_response']
        id_request = event['id_request']

        response_orq = Ejecucion.buscar_datos_envio(id_response)
        if response_orq is None:
            raise ValueError("No se ha encontrado el request")

        estructura_envio = response_orq.estructura_envio
        estado_envio = Conexion.consumo_promotec(id_request, id_response, estructura_envio)
        cant_request_enviado = len(Ejecucion.buscar_request_enviados(id_request))
        
        if(estado_envio == 1): 
            Ejecucion.actualizarEstadoRequest(id_request, 4)
        elif(cant_request_enviado >= 2 ):
            Ejecucion.actualizarEstadoRequest(id_request, 4)
            estado_envio = 2
        else:
            estado_envio = 2
            
        # Actualizamos el estado de response_orq
        response_orq.estado = estado_envio
        Ejecucion.update_resp_orq(response_orq)

        response = responseData.armadoBody("Ok", 200)
        return response

    except Exception as e:
        response = responseData.armadoBody(str(e), 400)
        return response