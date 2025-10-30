import json
import boto3
import os
import base64
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
    
    # Obtiene los secretos
    def getSecret(name):
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=os.getenv('REGION')
        )

        try:
            secret_request = client.get_secret_value(
                    SecretId=name
                )
        except client.exceptions.ResourceNotFoundException:
            raise ValueError("No se encontró el secreto")
        except client.exceptions.InvalidParameterException:
            raise ValueError("No se encontró el secreto")
        except client.exceptions.InvalidRequestException:
            raise ValueError("No se encontró el secreto")
        except client.exceptions.DecryptionFailure:
            raise ValueError("No se encontró el secreto")
        except client.exceptions.InternalServiceError:
            raise ValueError("No se encontró el secreto")
        except Exception:
            raise ValueError("Error en el secreto")

        if 'SecretString' in secret_request:
            secret = secret_request['SecretString']
        else:
            secret = base64.b64decode(secret_request['SecretBinary'])

        return json.loads(secret)

    # subir un archivo al s3
    def subirArchivoS3(bucket_name, path, name):
        session = boto3.session.Session()
        client = session.client(
            service_name='s3',
            region_name=os.getenv('REGION')
        )
        try:
            client.upload_file(path, bucket_name, name)
        except Exception as e:
            raise Exception("Ocurrió un error al subir al s3. "+str(e))
        
    # generar un link de descarga del s3
    def generarLinkDescargaS3(bucket_name, object_name, expiration = 3600):
        session = boto3.session.Session()
        client = session.client(
            service_name='s3',
            region_name=os.getenv('REGION')
        )
        try:
            file_valid = True
            try:
                client.head_object(Bucket=bucket_name, Key=object_name)
            except ClientError as e:
                # raise ValueError("El archivo especificado no existe")
                file_valid = False
            
            if file_valid:
                response = client.generate_presigned_url('get_object',Params={
                'Bucket': bucket_name,
                'Key': object_name
                },
                ExpiresIn=expiration)
            else:
                response = None
            
            return response
        except ClientError as e:
            raise Exception("Ocurrió un error al generar la url. "+str(e))
        except Exception as e:
            raise Exception("Ocurrió un error al generar la url. "+str(e))