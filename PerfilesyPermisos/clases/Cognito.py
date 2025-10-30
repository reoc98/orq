
import json
import boto3
from utils.Response import Response


class Cognito(Response):

    # Funcion construsctor de la clase.
    def __init__(self, client_id=""):
        # se hace la coneccion con aws con boto3 y se utiliza el servicio de cognito-idp.
        self.client = boto3.client(
            service_name='cognito-idp'
        )
        # client_id obtenido del environment del yamil.
        self.client_id = client_id

    # Funcion encargada de crear el usuario en aws.
    def create_user_cognito(self, datos):
        # se reciben los datos necesarios para crear el usuario.
        username = datos["username"]
        password = datos["password"]
        email = datos["email"]
        # se consume el servicio sing_up encargado de crear el usuario en aws.
        response = self.client.sign_up(
            ClientId=self.client_id,
            Username=username,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
            ],
        )
        # se valida la respuesta del servicio
        if "statusCode" in response:
            message = response["message"]
            statusCode = response["statusCode"]
            response = ""
        else:
            message = "servicio exitoso"
            statusCode = 200

        # Se retorna respuesta.
        return self.armadoBody(message, statusCode, response)

    # Funcion encargada de eliminar el usuario en aws.

    def delete_user_cognito(self, datos):
        # se reciben los datos necesarios para eliminar el usuario.
        username = datos["username"]
        # se consume el servicio admin_delete_user encargado de eliminar el usuario en aws.
        response = self.client.admin_delete_user(
            UserPoolId='us-east-1_uIIudFt9z',
            Username=username
        )

        # se valida la respuesta del servicio
        if "statusCode" in response:
            message = response["message"]
            statusCode = response["statusCode"]
            response = ""
        else:
            message = "servicio exitoso"
            statusCode = 200

        # Se retorna respuesta.
        return self.armadoBody(message, statusCode, response)

    # Funcion encargada de generar el token para las apis.

    def get_tokens(self, datos):
        try:
            # se reciben los datos necesarios para general el token.
            username = datos["username"]
            password = datos["password"]

            auth_params = {"USERNAME": username, "PASSWORD": password}
            # se consume el servicio initiate_auth encargado de crear el token.
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters=auth_params,
            )
            # Se captura la key de donde vienen los datos.
            response = response["AuthenticationResult"]
            # se organizan los datos para la respuesta.
            data = {
                "AccessToken": response["AccessToken"],
                "RefreshToken": response["RefreshToken"],
                "IdToken": response["IdToken"],
            }
            status_code = 200
        except (
            self.client.exceptions.InvalidParameterException,
            self.client.exceptions.UserLambdaValidationException,
            self.client.exceptions.UserNotFoundException,
            self.client.exceptions.PasswordResetRequiredException,
            self.client.exceptions.NotAuthorizedException
        ) as e:
            data = str(e)
            status_code = 400
        except KeyError:
            data = "Invalid parameters"
            status_code = 400

        except Exception as e:
            data = str(e)
            status_code = 500
        # Se retorna respuesta.

        return self.armadoBody("", status_code, data)

    # Funcion encargada de inactivar los token.
    def revoke_tokens(self, datos):
        try:
            # se reciben los datos necesarios para inactivar el token.
            refreshToken = datos["refreshToken"]

            # se consume el servicio initiate_auth encargado de crear el token.
            response = self.client.revoke_token(
                Token=refreshToken,
                ClientId=self.client_id
            )
            # se organizan los datos para la respuesta.
            data = {
                "data": True
            }
            status_code = 200
        except (
            self.client.exceptions.TooManyRequestsException,
            self.client.exceptions.InternalErrorException,
            self.client.exceptions.UnauthorizedException,
            self.client.exceptions.InvalidParameterException,
            self.client.exceptions.UnsupportedOperationException,
            self.client.exceptions.UnsupportedTokenTypeException,
            self.client.exceptions.ForbiddenException
        ) as e:
            data = str(e)
            status_code = 400
        except KeyError:
            data = "Invalid parameters"
            status_code = 400

        except Exception as e:
            data = str(e)
            status_code = 500
        # Se retorna respuesta.

        return self.armadoBody("", status_code, data)
