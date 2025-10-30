from json import loads
from clases.ServiceInif import ServiceInif
from utils.Response_v2 import Response

def start(event, context):
    try:
        if event['body'] is None:
            raise Exception("Cuerpo de la peticion invalido.")
        if isinstance(event['body'], str):
            event['body'] = loads(event['body'])
        request = event['body']
        id_request_orq = request['id_request_orq']
        figure = request['figure']

        inif = ServiceInif(id_request_orq, figure)
        inif.run_service()

        return Response.success()

    except Exception as error:
        print(error)
        # validar si existe la variable id_request_orq
        if 'id_request_orq' not in locals():
            return Response.bad_request("Falta el id_request_orq.")
        if 'figure' not in locals():
            figure = {}
            # return Response.bad_request("Falta la figura.")
        
        inif_error = ServiceInif(id_request_orq, figure)
        inif_error.insert(
            request={},
            response=str(error),
            status_code=-500
        )
        return Response.internal_server_error()