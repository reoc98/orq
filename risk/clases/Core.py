import json
from urllib.request import Request, urlopen
from utils.Aws import Aws, base64


# Clase para consumos de los servicios hacia risk
class Core():

    # Obtenemos el token del servicio de risk
    def token(self, secret):
        response = False
        # secret manager
        url = secret["url_token"]
        access = str(secret["usuario"])+':'+str(secret["password"])
        # se codifica en base64 para enviar la auth basic
        auth = base64.b64encode(access.encode("utf-8"))
        # se consume el servicio y se lee los datos
        request = Request(url=url, method="GET")
        request.add_header("Content-Type", "application/json")
        request.add_header("Authorization", "Basic "+str(auth.decode("utf-8")))
        data = urlopen(request, timeout=28).read().decode('utf-8-sig')
        info = json.loads(data)
        # validamos el token de risk
        if 'token' in info:
            if info['token'] is not None:
                response = info['token']
            else:
                raise Exception('Token de risk vacio '+str(info))
        else:
            raise Exception('No se encontró token de risk '+str(info))

        return response

    # Consumir el servicio de risk
    def consultarRisk(self, send_data):
        response = False

        secret = Aws.getSecret("risk-orq")
        # Obtenemos el token
        token = self.token(secret)
        
        url = secret["url_risk"]
        send_data = json.dumps(send_data)
        send_data = send_data.encode('utf-8')
        # se consume el servicio y se lee los datos
        request = Request(url=url, data=send_data, method="POST")
        # secret manager
        request.add_header(
            "Authorization", "Bearer "+str(token))
        
        request.add_header("Access-Control-Allow-Origin", "*")
        request.add_header("Content-Type", "application/json")
        data = urlopen(request, timeout=800).read().decode('utf-8-sig')
        response = json.loads(data)

        return response
