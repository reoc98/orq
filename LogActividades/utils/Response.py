import json


# Clase encargada de dar la respuesta aws
class Response():
    # Metodo de respuesta
    @classmethod
    def aws(cls, data: dict):

        data['data'] = data.get('data', [])
        data['error'] = data.get('error', False)

        return {
            "statusCode": data['statusCode'],
            "headers": {
                'Content-Type': 'application/json'
            },
            "body": json.dumps(data)
        }
    
    # Metodo de respuesta
    @classmethod
    def error(cls,  message: str = 'Error del cliente'):
        data = {
            'statusCode': 400,
            'error': True,
            'data': [],
            'message': message,
        }
        return cls.aws(data)

    # Metodo de respuesta
    @classmethod
    def success(cls, data: list = [], message: str = 'Petición exitosa'):
        response = {
            'statusCode': 200,
            'data': data,
            'message': message
        }
        return cls.aws(response)

    # Metodo de respuesta
    @classmethod
    def not_found(cls, message: str = 'Recurso no encontrado'):
        data = {
            'statusCode': 404,
            'error': True,
            'data': [],
            'message': message,
        }
        return cls.aws(data)

    # Metodo de respuesta
    @classmethod
    def internal_server_error(cls):
        data = {
            'statusCode': 500,
            'error': True,
            'data': [],
            'message': 'Error interno del servidor',
        }
        return cls.aws(data)

    # Metodo de respuesta
    @classmethod
    def bad_request(cls, message: str = 'Error en la petición'):
        data = {
            'statusCode': 400,
            'error': True,
            'data': [],
            'message': message,
        }
        return cls.aws(data)