import base64
import json
import boto3
import os
import logging
from botocore.exceptions import ClientError


# Consumos de servicio aws
class Aws():

    # Invocamos las funciones asyncronamente
    def lambdaInvoke(name, data):

        data = json.dumps(data)

        session = boto3.session.Session()
        client = session.client(
            service_name='lambda',
            region_name=os.getenv('REGION')
        )
        response = client.invoke(
            FunctionName=name,
            Payload=data,
            InvocationType='Event'
        )

        return response

    @classmethod
    def get_secret(cls, name='secret-orquestador'):
        """
        Obtener secreto
        param: str
            name llave del nombre del secreto a obtener
        """
        stage = os.getenv('STAGE')

        secretname = f'{stage}/{name}'

        client = cls.get_client('secretsmanager')

        try:
            secret_request = client.get_secret_value(
                SecretId=secretname
            )
        except client.exceptions.ResourceNotFoundException as e:
            raise ValueError(f"No se encontró el secreto {e}")
        except client.exceptions.InvalidParameterException as e:
            raise ValueError(f"InvalidParameterException {e}")
        except client.exceptions.InvalidRequestException as e:
            raise ValueError(f"InvalidRequestException {e}")
        except client.exceptions.DecryptionFailure as e:
            raise ValueError(f"DecryptionFailure {e}")
        except client.exceptions.InternalServiceError as e:
            raise ValueError(f"InternalServiceError {e}")
        except Exception as e:
            raise ValueError(f"Error en el secreto {e}")

        if 'SecretString' in secret_request:
            secret = secret_request['SecretString']
        else:
            secret = base64.b64decode(secret_request['SecretBinary'])

        return json.loads(secret)

    @classmethod
    def get_client(cls, service_name: str):
        """
        Obtener cliente de aws
        param: service_name
            nombre del servicio
        return: client
            cliente de aws
        """
        session = boto3.session.Session()
        client = session.client(
            service_name=service_name,
            region_name=os.getenv('REGION')
        )
        return client

    @classmethod
    def download_file_obj(cls, object_name: str, file_path: str):
        """Download a file from an S3 bucket

        :param object_name:
            S3 object name. If the object is in a folder, include the folder name.
            Example: 'folder_name/file_name.extension'
        :param file_path: 
            Local path where the file will be saved.
            Example: '/path/to/local/file_name.extension'
        :return: True if file was downloaded, else False
        """
        s3_client = cls.get_client('s3')
        try:
            bucket_name = Aws.get_secret()['bucket_s3']
            s3_client.download_file(bucket_name, object_name, file_path)
            return True
        except ClientError as e:
            logging.error(e)
            raise Exception(f"Error al descargar el archivo {e}") from e
        except Exception as e:
            print(f"Error al descargar el archivo: {e}")
            raise Exception(f"Error al descargar el archivo {e}") from e