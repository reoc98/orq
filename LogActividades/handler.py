import json
from clases.LogActivity import LogActivity

schema = LogActivity.read_json_file('request_schemas.json')

#función encargada de obtener los usuarios que realizan una actividad
def get_users_log(event, context):
    try:
        # Se invoca a la funcion encargada de realizar la consulta
        response = LogActivity.get_users_log()

        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()

#función encargada de obtener todos los perfiles
def get_profiles_log(event, context):
    try:
        # Se invoca a la funcion encargada de realizar la consulta
        response = LogActivity.get_profiles_log()

        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()

#función encargada de obtener los usuarios afectados en una actividad
def get_users_affected(event, context):
    try:
        # Se invoca a la funcion encargada de realizar la consulta
        response = LogActivity.get_users_affected()

        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()

#función encargada de obtener todos los tipos de actividades
def get_activity_type(event, context):
    try:
        request_body = json.loads(event["body"])

        # validar que los datos sean correctos
        LogActivity.schema_validation(
            schema=schema['get_activity_type'], document=request_body)
        
        response = LogActivity.get_activity_type(request_body)
        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()

#función encargada crear un filtro en el log de actividades
def create_filter(event, context):
    try:

        request_body = json.loads(event["body"])

        # validar que los datos sean correctos
        LogActivity.schema_validation(
            schema=schema['filter_log'], document=request_body)
        # keysRule = logActivityEntity.keyRules('filter_log')

        response = LogActivity.create_filter(request_body)
        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        #traceback.print_exc(error)
        return LogActivity.internal_server_error()

# Funcion para obtener la inforacion de un log de actividades con todos los detalles
def get_activity(event, context):
    try:
        request_body = json.loads(event["body"])

        # validar que los datos sean correctos
        LogActivity.schema_validation(
            schema=schema['get_activity'], document=request_body)

        response = LogActivity.get_activity(request_body)

        return response
    
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()

# Funcion para obtener los periodos de tiempo para filtrar
def get_period(event, context):

    try:
        # Se instancia la clase y se ejecuta la funcion.
        response = LogActivity.get_period()
        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()
    
def get_motores(event, context):
    try:
        response = LogActivity.get_arboles_log(1)

        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()
    
def get_arboles(event, context):
    try:
        response = LogActivity.get_arboles_log()

        return response
    except ValueError as e:
        return LogActivity.error(f"{e}")
    except Exception as error:
        return LogActivity.internal_server_error()