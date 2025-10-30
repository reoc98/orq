
import json
from utils.Response import Response
from utils.Validations import Validations
from clases.Risk import Risk 
from entity.RiskEntity import RiskEntity
from clases.Core import Core
from urllib.error import HTTPError, URLError

responseData = Response()
validate = Validations()
RiskEntity = RiskEntity()
Risk = Risk()
Core = Core()


# Se encarga de administrar los datos que seran consultado a risk
def risk(event, context):    
    try:
        # validamos el json de entrada
        try:
            if event['body'] is None:
                raise Exception("Cuerpo de la peticion invalido.")
            if "id" in event['body']:
                request = event['body']
            else:
                request = json.loads(event['body'])
            id = request['id']
        except ValueError:
            raise Exception("Cuerpo de la peticion invalido.")

        orq = Risk.obtenerRequestOrq(id)
        # se valida que exista el request
        if orq != None:
            # obtenemos y validamos si el request tiene figuras persona
            # a consultar a risk
            datos = json.loads(orq.request.replace("\'", "\""))
            if "figuras_personas" in datos:
                if datos["figuras_personas"] is not None:
                    # insertamos a la tabla y ejecutamos risk
                    figuras_personas = datos["figuras_personas"]
                    envio = Risk.prepararRisk(id, figuras_personas)
                    response = responseData.armadoBody("ok", 200)
                else:
                    response = responseData.armadoBody("No se encontro figuras persona", 404)
            else:
                response = responseData.armadoBody("No se encontro figuras persona", 404)
        else:
            response = responseData.armadoBody("No se encontro ningun registro", 404)

        return response

    except Exception as error:
        return responseData.armadoBody(str(error), 500)


# Ejecuta las consultas hacia risk
def procesoRisk(event, context):
    id = event['id']  
    try:

        # Obtenemos el risk a consultar
        risk = Risk.ObtenerRiskConsulta(id)
        # se valida que exista el request
        if risk != None:
            figura = json.loads(risk.request_figuras.replace("\'", "\""))
            tipo_doc_figura = figura['tipo_doc_figura']
            
            # Buscamos el código del tipo de documento por medio del prefijo
            tipo_doc_figura = Risk.buscar_tipo_documento(figura['tipo_doc_figura'])
            
            if tipo_doc_figura is None:
                tipo_doc_figura = figura['tipo_doc_figura']

            datos = {
                "datoConsultar": figura['num_doc_figura'],
                "tipoDocumento": tipo_doc_figura
            }
            try:
                # consultamos el token y el servicio de risk
                resp = Core.consultarRisk(datos)

            except HTTPError as e:
                resp = json.loads(e.read())
            except URLError as e:
                resp = str(e.reason())
            except Exception as error:
                resp = str(error)
            # guardamos los logs
            Risk.guardarLog(id,resp,1,json.dumps(datos))

            response = responseData.armadoBody("Ok", 200, resp)
        else:
            response = responseData.armadoBody("No se encontró ningún registro", 404)
            Risk.guardarLog(id,response,2)

        return response

    except Exception as error:
        respt = responseData.armadoBody(str(error), 500)
        Risk.guardarLog(id,str(respt),2)
        return respt

# validamos que los procesos de risk se hayan completado
def validarRisk(event, context):

    try:

        # Obtenemos el risk a validar
        risk = Risk.obtenerPendienteRisk()
        # se valida que tenga registro
        if risk != None:
            
            # recorremos los risk pendientes por validar
            for info in risk:
                
                total_request = Risk.obtenerPorIdRequest(info.id)
                total_consultados = Risk.obtenerPorIdRequest(info.id, 1)

                if total_request != None:
                    if len(total_request) == len(total_consultados) and len(total_request) > 0:
                        Risk.actualizarEstadoRequest(info.id, 1)                    
              

            response = responseData.armadoBody("Ok", 200)
        else:
            response = responseData.armadoBody("No se encontró ningún registro", 404)

        return response

    except Exception as error:
        respt = responseData.armadoBody(str(error), 500)
        return respt
