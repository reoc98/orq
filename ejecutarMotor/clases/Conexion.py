from clases.Database import Database
from models.RequestsEnviados import RequestsEnviados
from utils.Aws import Aws
import os
import contextlib
import OpenSSL.crypto
import requests
import tempfile
import base64
from requests.exceptions import Timeout

# Clase para consumos de los servicios hacia risk
class Conexion():
    @classmethod
    def consumo_promotec(cls, id_request, id_response, estructura_envio):
        # Se obtiene los valores de los secretos
        secret = Aws.getSecret(str(os.getenv("STAGE")) + "/secret-orquestador")

        # Sacamos el URL y password de consumo
        url = secret["url_enviar_motor_consumo"]
        pass_pfx_byte = bytes(secret["pass_enviar_motor_consumo"], 'utf-8')
        bucket_s3 = secret["bucket_s3"]

        file_path = cls.get_pfx_file('PROMOTEC.pfx', bucket_s3)

        try:
            with cls.pfx_to_pem(file_path, pass_pfx_byte) as cert:
                headers = {'Content-type': 'application/json'}
                peticion = requests.post(
                    url,
                    cert=cert,
                    data=estructura_envio,
                    headers=headers,
                    timeout=30  # Puedes ajustar el tiempo según necesidad
                )
            
            estado = 1 if peticion.status_code == 201 else 0

            data_res = {
                "id_request": id_request,
                "id_response": id_response,
                "servicio": url,
                "status_code": peticion.status_code,
                "response": peticion.text,
                "estado": estado
            }

        except Timeout as e:
            estado = 0
            data_res = {
                "id_request": id_request,
                "id_response": id_response,
                "servicio": url,
                "status_code": 408,
                "response": f"Timeout al consumir servicio: {str(e)}",
                "estado": estado
            }

        except Exception as e:
            estado = 0
            data_res = {
                "id_request": id_request,
                "id_response": id_response,
                "servicio": url,
                "status_code": 500,
                "response": f"Error inesperado: {str(e)}",
                "estado": estado
            }

        cls.guardar_envio_request(data_res)
        return estado

    @contextlib.contextmanager
    def pfx_to_pem(pfx_path, pfx_password):
        """ Decrypts the .pfx file to be used with requests. """

        with tempfile.NamedTemporaryFile(suffix=".pem",delete=False) as t_pem:
            f_pem = open(t_pem.name, "wb")
            pfx = open(pfx_path, "rb").read()
            p12 = OpenSSL.crypto.load_pkcs12(pfx, pfx_password)
            f_pem.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))
            f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))
            ca = p12.get_ca_certificates()
            if ca is not None:
                for cert in ca:
                    f_pem.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
            f_pem.close()
            yield t_pem.name

    @classmethod
    def get_pfx_file(cls, name, bucket_s3):
        try:
            s3_object = Aws.get_object(bucket_s3, f"certificados/{name}")
            response = s3_object['Body'].read()

            tmp_dir = os.getenv('TMP')
            file_path = f'{tmp_dir}{name}'
            code_file = base64.b64encode(response)

            with open(file_path, "wb") as fh:
                fh.write(base64.decodebytes(code_file))

        
            return file_path
  
        except Exception as e:
            raise ValueError("No ha sido posible obtener el certificado.")
        
    @classmethod
    def guardar_envio_request(cls, payload):
        db = Database('dbw').session
        try:
            row = RequestsEnviados(**payload)
            db.add(row)
            db.commit()

            return row.id
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()