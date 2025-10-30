from classes.Reportes import Reportes
from classes.ReporteReglas import ReporteReglas
from classes.ReporteSiniestros import ReporteSiniestros
from classes.MensualReglas import MensualReglas
import json

schema = ReporteSiniestros.read_json_file('request_schemas.json')
reportes = Reportes()

# funcion que envia las lambda asyncriona a los motores
def insertarReportes(event, context):
 
    try:
        # validamos el json de entrada
        try:
            if event['body'] is None:
                raise Exception("Cuerpo de la peticion invalido.")
            request = json.loads(event['body'])
        except ValueError:
            raise Exception("Cuerpo de la peticion invalido.")

        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(
            schema=schema['receive_insert'], document=request)

        resp_usuario = reportes.validarUsuario(request["id_usuario"])

        if resp_usuario["statusCode"] != 200:
            return ReporteSiniestros.error(resp_usuario["message"])

        # validamos si el request esta ejecutado
        report = reportes.obtenerRequestOrqID(request['id_request'])
        if report != None:
            # validamos si hay una ejecucion en proceso para dejarlo en la cola
            validar = reportes.obtenerReporteOrqEstado()
            # si ya hay un proceso lo va a guardar solamente
            if validar != None:
                guardado = reportes.guardarReporte(request['id_request'],2)
                if guardado:
                    response = ReporteSiniestros.success("Generando Reporte")
                else:
                    response = ReporteSiniestros.error("Ocurrió un error al registrar.")
            else:
                # si no hay un proceso lo va a guardar y lo mandara a ejecutar
                guardado = reportes.guardarReporte(request['id_request'], 2)
                if guardado:
                    reportes.generarReporteSiniestro(request['id_usuario'])
                    response = ReporteSiniestros.success("Generando Reporte")
                else:
                    response = ReporteSiniestros.error("Ocurrió un error al registrar.")
        else:
                response = ReporteSiniestros.not_found("Request enviado no válido.")

        return response
    except ValueError as error:
        return ReporteSiniestros.error(f"{error}")
    except Exception as error:
        respt = ReporteSiniestros.internal_server_error()
        return respt

# metodo que va a generar un reporte
def generarReporteSiniestro(event, context):
    try:
        email = event["email"]
        id_usuario = event["id_usuario"]
        report = reportes.obtenerReporteOrqPendientes(2)
        # obtenemos y validamos los reportes pendientes
        if report:
            # recorremos todos los pendientes
            for row in report:
                # validamos si alguna falla no interrumpir el flujo
                try:
                    # validamos si aun sigue activo
                    validacion = reportes.obtenerReporteOrqId(row.id)
                    if validacion != None:
                        # cambiamos estado a procesando
                        actualizacion = reportes.actualizarReporte(row.id, row.id_request, 3)
                        if actualizacion:
                            # Consultamos el número del Request
                            num_siniestro = reportes.get_num_siniestro(row.id_request)

                            # generamos excel y guardamos en el s3
                            excel = reportes.excelReporteSiniestro(row, email, num_siniestro)
                            if excel:
                                resp = ReporteSiniestros.success()
                                reportes.actualizarReporte(row.id, row.id_request, 5,resp)
                            else:
                                resp = ReporteSiniestros.error("No generado ocurrio un error.")
                                reportes.actualizarReporte(row.id, row.id_request, 4, resp)
                    else:
                        resp = ReporteSiniestros.error("Registro se encuentra inactivo o cancelado.")
                        reportes.actualizarReporte(row.id, row.id_request, 4, resp)
                except Exception as error:
                    resp = ReporteSiniestros.internal_server_error()
                    reportes.actualizarReporte(row.id, row.id_request, 4, resp)
                    continue

            pendientes = reportes.obtenerReporteOrqPendientes(2)
            if pendientes:
                reportes.generarReporteSiniestro(id_usuario)
            #else:
            response = ReporteSiniestros.success()
        else:
            response = ReporteSiniestros.not_found("No hay reportes pendientes.")

        return response
    except ValueError as error:
        return ReporteSiniestros.error(f"{error}")
    except Exception as error:
        respt = ReporteSiniestros.internal_server_error()
        return respt

# metodo que genera el reporte mensual de siniestro
def ReporteMensualSiniestros(event, context):
    try:
        # validamos el json de entrada
        try:
            if event['body'] is None:
                raise Exception("Cuerpo de la peticion invalido.")
            request = json.loads(event['body'])
        except ValueError:
            raise Exception("Cuerpo de la peticion invalido.")
        
        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(
            schema=schema['generar_reporte'], document=request)
        
        resp_usuario = reportes.validarUsuario(request["id_usuario"])
        
        if resp_usuario["statusCode"] != 200:
            return ReporteSiniestros.error(resp_usuario["message"])

        resp_insert = reportes.insertarReporteMensual()

        if resp_insert["statusCode"] != 200:
            return ReporteSiniestros.error(resp_insert["message"])

        request["id_reporte"] = resp_insert["data"]["id"]
        reportes.generarReporteMensual(request)

        return ReporteSiniestros.success(resp_insert["data"]["id"])
    
    except ValueError as error:
        return ReporteSiniestros.error(f"{error}")
    except Exception as error:
        respt = ReporteSiniestros.internal_server_error()
        return respt

# metodo que genera el reporte mensual de siniestro
def asyncGenerarReporteMensual(event, context):
    try:
        info_reporte = reportes.informacionReporte(event)

        if info_reporte["statusCode"] != 200:
            return ReporteSiniestros.error(info_reporte["message"])
        
        if info_reporte["data"] == []:
            return ReporteSiniestros.success([], info_reporte["message"])

        id_reporte = event["id_reporte"]
        reportes.excelReporteMensualSiniestro(info_reporte["data"], id_reporte)

    except Exception as error:
        respt = ReporteSiniestros.internal_server_error()
        return respt

# metodo que genera el reporte mensual de siniestro
def validarReporteMensual(event, context):
    try:
        # validamos el json de entrada
        try:
            if event['body'] is None:
                raise Exception("Cuerpo de la peticion invalido.")
            request = json.loads(event['body'])
        except ValueError:
            raise Exception("Cuerpo de la peticion invalido.")
        
        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(
            schema=schema['validar_reporte_mensual'], document=request)

        info_validacion = reportes.validarReporteMensual(request["id_reporte"], request["id_usuario"])

        if info_validacion["statusCode"] not in (200, 404):
            return ReporteSiniestros.error(info_validacion["message"])
        
        if info_validacion["statusCode"] == 404:
            return ReporteSiniestros.not_found(info_validacion["message"])

        data = info_validacion["data"]

        if data.estado == 2:
            msj = "No se encontraron registros"
            return ReporteSiniestros.success([], msj)

        descargar = reportes.descargarReporte(data.ruta)
        respuesta = {
            "url": "",
            "respuesta": json.loads(data.respuesta)
        }
        if descargar:
            respuesta["url"] = str(descargar)

        return ReporteSiniestros.success(respuesta)
    
    except ValueError as error:
        return ReporteSiniestros.error(f"{error}")
    except Exception as error:
        respt = ReporteSiniestros.internal_server_error()
        return respt

# metodo que cancela el reporte de siniestro en que este en pendiente
def cancelarReportes(event, context):
    try:
        # validamos el json de entrada
        try:
            if event['body'] is None:
                raise Exception("Cuerpo de la peticion invalido.")
            request = json.loads(event['body'])
        except ValueError:
            raise Exception("Cuerpo de la peticion invalido.")
        
        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(
            schema=schema['receive_insert'], document=request)
        reportes.validar_estado_reporte(request['id_request'], request['id_usuario'])
        cancelar = reportes.cancelarReporte(request['id_request'])
        if cancelar:
            response = ReporteSiniestros.success()
        else:
            response = ReporteSiniestros.error("No se pudo cancelar el reporte.")

        return response

    except ValueError as error:
        return ReporteSiniestros.error(f"{error}")
    
    except Exception as error:
        respt = ReporteSiniestros.internal_server_error()
        return respt

# funcion que descarga el archivo del s3 devuelve el link
def descargarReportes(event, context):
    try:
        # validamos el json de entrada
        try:
            if event['body'] is None:
                raise Exception("Cuerpo de la peticion invalido.")
            request = json.loads(event['body'])
        except ValueError:
            raise Exception("Cuerpo de la peticion invalido.")
        
        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(
            schema=schema['download_report'], document=request)
        
        obtenerUrl = reportes.obtenerReporteOrqIdUrl(request['id_request'], request['id_usuario'])
        if obtenerUrl != None:
            descargar = reportes.descargarReporte(obtenerUrl.url)
            if descargar:
                data = {
                    "url": str(descargar)
                }
                response = ReporteSiniestros.success(data)
            else:
                response = ReporteSiniestros.error("No se pudo generar el link.")
        else:
            response = ReporteSiniestros.error("No existe el reporte.")
        return response

    except ValueError as error:
        return ReporteSiniestros.error(f"{error}")
    
    except Exception as error:
        respt = ReporteSiniestros.internal_server_error()
        return respt

def get_siniestros(event, context):
    try:
        request_body = json.loads(event['body'])

        ReporteSiniestros.schema_validation(
            schema=schema['get_siniestros'], document=request_body)

        response = ReporteSiniestros.get_siniestros(request_body)
        
    except KeyError as e:
        response = ReporteSiniestros.internal_server_error()
    except ValueError as e:
        response = ReporteSiniestros.error(message=f'{e}')
    except Exception as e:
        response = ReporteSiniestros.internal_server_error()
    
    return response

def get_reglas(event, context):
    try:
        request_body = json.loads(event['body'])

        ReporteReglas.schema_validation(
            schema=schema['get_reglas'], document=request_body)

        response = ReporteReglas.get_reglas(request_body)
        
    except KeyError as e:
        response = ReporteReglas.internal_server_error()
    except ValueError as e:
        response = ReporteReglas.error(message=f'{e}')
    except Exception as e:
        response = ReporteReglas.internal_server_error()
    
    return response

#función encargada de obtener los usuarios que realizan una actividad
def get_tipo_fecha(event, context):
    try:
        # Se invoca a la funcion encargada de realizar la consulta
        response = ReporteSiniestros.get_tipo_fecha()

    except ValueError as e:
        response = ReporteSiniestros.error(f"{e}")
    except Exception as error:
        response = ReporteSiniestros.internal_server_error()

    return response

#función encargada de obtener ciudades
def get_cities(event, context):
    try:
        request_body = json.loads(event['body'])

        ReporteReglas.schema_validation(
            schema=schema['get_cities'], document=request_body)
        # Se invoca a la funcion encargada de realizar la consulta
        response = ReporteSiniestros.get_cities(request_body['id_departamento'])

    except ValueError as e:
        response = ReporteSiniestros.error(f"{e}")
    except Exception as error:
        response = ReporteSiniestros.internal_server_error()

    return response

#función encargada de obtener los departanentos
def get_departments(event, context):
    try:
        # Se invoca a la funcion encargada de realizar la consulta
        response = ReporteSiniestros.get_departments()

    except ValueError as e:
        response = ReporteSiniestros.error(f"{e}")
    except Exception as error:
        response = ReporteSiniestros.internal_server_error()

    return response

#función encargada de obtener los departanentos
def get_months(event, context):
    try:
        # Se invoca a la funcion encargada de realizar la consulta
        response = ReporteSiniestros.get_months()

    except ValueError as e:
        response = ReporteSiniestros.error(f"{e}")
    except Exception as error:
        response = ReporteSiniestros.internal_server_error()

    return response

#función encargada de obtener las reglas (motores)
def get_select_reglas(event, context):
    try:
        response = MensualReglas.get_select_reglas()
        return response

    except ValueError as e:
        return ReporteSiniestros.error(str(e))

    except Exception as e:
        return ReporteSiniestros.internal_server_error()

# Generar reporte mensual de reglas
def reporte_mensual_reglas(event, context):
    try:
        # validamos el json de entrada
        request = ReporteSiniestros.json_validator(event['body'])

        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(schema=schema['generar_mensual_reglas'], document=request)

        response = MensualReglas.monthly_rules_report(payload=request)

        return response

    except ValueError as e:
        return ReporteSiniestros.error(str(e))

    except Exception as e:
        return ReporteSiniestros.internal_server_error()
    
# Metodo asyncronico para Generar reporte mensual de reglas
def async_generar_mensual_reglas(event, context):
    try:
        info_reporte = MensualReglas.informacionReporte(event)

        return info_reporte

    except ValueError as e:
        return ReporteSiniestros.error(str(e))

    except Exception as e:
        return ReporteSiniestros.internal_server_error()
    
# metodo que validar el reporte mesual de reglas
def validar_reporte_reglas(event, context):
    try:
        # validamos el json de entrada
        request = ReporteSiniestros.json_validator(event['body'])

        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(schema=schema['validar_reporte_reglas'], document=request)

        response = MensualReglas.validar_reporte_reglas(request)

        return response

    except ValueError as e:
        return ReporteSiniestros.error(str(e))

    except Exception as e:
        return ReporteSiniestros.internal_server_error()
    
def get_years(event, context):
    try:
        return MensualReglas.get_years()

    except ValueError as e:
        return ReporteSiniestros.error(str(e))

    except Exception as e:
        return ReporteSiniestros.internal_server_error()
    
def download_report_monthly(event, context):
    try:
        # validamos el json de entrada
        request = ReporteSiniestros.json_validator(event['body'])

        # validamos los campos de entrada
        ReporteSiniestros.schema_validation(schema=schema['descargar_reporte_mensual'], document=request)

        return MensualReglas.download_report(request)

    except ValueError as e:
        return ReporteSiniestros.error(str(e))
    
    except Exception as e:
        return ReporteSiniestros.internal_server_error()
