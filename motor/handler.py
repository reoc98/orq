import json
from clases.Motor import Motor

schema = Motor.read_json_file('request_schemas.json')

def create_motor(event, context):
    try:
        request_body = Motor.json_validator(event["body"])
        token_header = Motor.get_token_header(event["headers"])

        # validar que los datos sean correctos
        Motor.schema_validation(schema=schema['create_motor'], document=request_body)
        
        response = Motor.create_motor(payload=request_body, token=token_header)
        return response
    
    except ValueError as e:
        return Motor.error(f"{e}")
    
    except Exception as e:
        return Motor.internal_server_error(str(e))
        
def select_motor(event, context):
    try:
        request_body = Motor.json_validator(event["body"])

        # validar que los datos sean correctos
        Motor.schema_validation(schema=schema['select_motor'], document=request_body)
        
        response = Motor.get_select(request_body['type'])
        return response
    
    except ValueError as e:
        return Motor.error(f"{e}")
    
    except Exception as e:
        return Motor.internal_server_error(str(e))

def delete_motor(event, context):
    try:
        request_body = Motor.json_validator(event["body"])
        token_header = Motor.get_token_header(event["headers"])

        # validar que los datos sean correctos
        Motor.schema_validation(schema=schema['delete_motor'], document=request_body)
        
        response = Motor.delete_motor(request_body, token=token_header)
        return response
    
    except ValueError as e:
        return Motor.error(f"{e}")
    
    except Exception as error:
        return Motor.internal_server_error(str(error))

# Método para eliminar un arbol
def delete_arbol(event, context):
    try:
        # Obtenemos informacion del arbol y token de autorizacion
        request_body = Motor.json_validator(event["body"])
        token_header = Motor.get_token_header(event["headers"])

        # validar datos entrantes sean correctos
        Motor.schema_validation(schema=schema['delete_arbol'], document=request_body)
        
        # Ejecutamos el método para eliminar el arbol
        response = Motor.delete_arbol(request_body, token=token_header)
        return response
    
    except ValueError as e:
        return Motor.error(f"{e}")
    
    except Exception as error:
        return Motor.internal_server_error(str(error))
    