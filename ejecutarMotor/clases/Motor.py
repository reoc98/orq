import json
from urllib.request import Request, urlopen
from utils.Aws import Aws, base64, os
from urllib.error import HTTPError, URLError



# Clase para consumos de los servicios hacia risk
class Motor():
    def __init__(self) -> None:
        try:
            secret = Aws.getSecret(str(os.getenv('STAGE'))+"/secret-orquestador")
            # Obtenemos el token
            self.token_orq = self.token(secret)
            self.url_motor_consumo = secret["url_motor_consumo"]
            
        except ValueError as e:
            raise ValueError(e)
        
        except Exception as e:
            raise ValueError("Ha ocurrido un error en la ejecución de los motores.")

    def ejecutar_motor(self, send_data):
        # Armamos la estructura de retorno
        data = {
            'error': 2,
            'desenlace': None,
            'resp': ''
        }
        resp = None
        err_back = 0

        try:
            # Consumimos el servicio del motor
            resp = self.ejecutar(send_data)
            
        except Exception as e:
            err_back = 1
            resp = str(e)
        
        finally:
            # Al finalizar el metodos validamos respuesta del consumo
            if resp is not None:
                # Revisamos que no haya errores
                if err_back == 1:     
                    data['desenlace'] = {"resultado": "0", "semaforo": "0", "mensaje": "blanco"}

                elif ('error' in resp) and (resp['error'] == 0):
                    data['error'] = 1
                    data['desenlace'] = resp['datos']['desenlace_contenido']
            else:
                data['desenlace'] = {"resultado": "0", "semaforo": "0", "mensaje": "blanco"}
            

            data['resp'] = resp
        return data

    # Obtenemos el token del servicio de risk
    def token(self, secret):
        response = False

        # secret manager
        url = secret["url_motor_login"]
        send_data = {
            "email": str(secret["user_motor"]),
            "password": str(secret["pass_motor"])
        }

        send_token = json.dumps(send_data)
        send_token = send_token.encode('utf-8')

        try:
            # se consume el servicio y se lee los datos
            request = Request(url=url, data=send_token, method="POST")
            request.add_header("Content-Type", "application/json")
            data = urlopen(request, timeout=28).read().decode('utf-8-sig')
            info = json.loads(data)

            # validamos el token de risk
            if 'statusCode' in info:
                if info['statusCode'] == 200:
                    response = info['data']
                else:
                    raise Exception('Error al obtener el token del motor '+str(info))
            else:
                raise Exception('No se encontró el token del motor '+str(info))
        
        except HTTPError as e:
            resp_http_error = e.read()
            resp_http_error = resp_http_error.decode('utf-8')
            print('***HTTPError***', e, resp_http_error)
            raise ValueError('Ha ocurrido un error al obtener el Token.')
            
        except URLError as e:
            print('***URLError REASON***', e, e.reason())
            raise ValueError(f'***URLError***: {str(e)}')

        except Exception as e:
            Type = type(e)
            raise Type(str(e))

        return response

    # Cosumo del servicio motor_reglas_procesos
    def ejecutar(self, send_data):
        # Obtenemos el Token y Url de consumo de la instancia del objeto
        token = self.token_orq
        url = self.url_motor_consumo

        # Le damos formado a la data a enviar 
        send = json.dumps(send_data)
        send = send.encode('utf-8')
        
        try:
            # Creamos el consumo con Request
            request = Request(url=url, data=send, method="POST")

            # Agregamos los  header
            request.add_header("Id-Token-Cognito", str(token['Idtoken']))
            request.add_header("Refresh-Token-Cognito", str(token['RefreshToken']))
            request.add_header("Access-Token", str(token['AccessToken']))
            request.add_header("Access-Control-Allow-Origin", "*")
            request.add_header("Content-Type", "application/json")

            # Consumimos el servicio y la respues la guardamos en una variable.
            data = urlopen(request, timeout=1000).read().decode('utf-8-sig')

            # Validamos la respuestas que recibimo
            if data is None:
                raise ValueError("Fallo el servicio del motor (data) "+str(data))
            
            # En el caso de que se haya recibido bien, lo convertimos a Diccionario 
            response = json.loads(data)

            # Vemos si la conversion es NONE/NULL
            if response is None:
                raise ValueError("Fallo el servicio del motor (response) "+str(response))
            
            return response
            
        except HTTPError as e:
            resp_http_error = e.read()
            resp_http_error = resp_http_error.decode('utf-8')

            return json.loads(resp_http_error)

            # raise ValueError(str(data_value_error))

        except URLError as e:
            raise ValueError(f'***URLError***: {str(e)}')

        except Exception as e:
            Type = type(e)
            raise Type(str(e))
