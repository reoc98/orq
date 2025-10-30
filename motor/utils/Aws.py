import json
import boto3
import os
import base64

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
