import boto3
from utils.Response import Response
# from os import environ as os_environ
from os import environ as os_environ


class Cognito(Response):

    # Funcion construsctor de la clase.
    def __init__(self, client_id=""):
        # se hace la coneccion con aws con boto3 y se utiliza el servicio de cognito-idp.
        self.client = boto3.client(
            service_name='cognito-idp'
        )
        # client_id obtenido del environment del yamil.
        self.client_id = client_id
        self.user_pool_id = os_environ.get("COGNITO_USER_POOL_ID", "")

    # Funcion encargada de crear el usuario en aws.
    def create_user_cognito(self, datos):
        # se reciben los datos necesarios para crear el usuario.
        username = datos["username"]
        password = datos["password"]
        # se consume el servicio sing_up encargado de crear el usuario en aws.
        response = self.client.sign_up(
            ClientId=self.client_id,
            Username=username,
            Password=password
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
    # metodo que actualiza los atributos de los usuarios en cognito.
    def update_user_cognito(self,datos):

        try:
            # se consume el servicio initiate_auth encargado de crear el token.
            response = self.client.update_user_attributes( 
                UserAttributes = [ 
                    { 
                        'Name' :  'email', 
                        'Value' :  datos["email"] 
                    }, 
                ], 
                AccessToken = datos["token"]
            )
            # se organizan los datos para la respuesta.
            status_code = 200
            data = "proceso exitoso."
        except (
            self.client.exceptions.ResourceNotFoundException,
            self.client.exceptions.InvalidParameterException,
            self.client.exceptions.CodeMismatchException,
            self.client.exceptions.ExpiredCodeException,
            self.client.exceptions.NotAuthorizedException,
            self.client.exceptions.UnexpectedLambdaException,
            self.client.exceptions.UserLambdaValidationException,
            self.client.exceptions.InvalidLambdaResponseException,
            self.client.exceptions.TooManyRequestsException,
            self.client.exceptions.AliasExistsException,
            self.client.exceptions.InvalidSmsRoleAccessPolicyException,
            self.client.exceptions.InvalidSmsRoleTrustRelationshipException,
            self.client.exceptions.InvalidEmailRoleAccessPolicyException,
            self.client.exceptions.CodeDeliveryFailureException,
            self.client.exceptions.PasswordResetRequiredException,
            self.client.exceptions.UserNotFoundException,
            self.client.exceptions.UserNotConfirmedException,
            self.client.exceptions.InternalErrorException,
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

        return self.armadoBody(data, status_code)

    # metodo que actualiza la contraseña usuarios en cognito.
    def admin_set_user_password(self,datos):

        try:

            username = datos["username"]
            password = datos["password"]
            # se consume el servicio initiate_auth encargado de crear el token.
            response = self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=username,
                Password=password,
                Permanent=True
            )
            # se organizan los datos para la respuesta.
            status_code = 200
            data = "proceso exitoso."
        except (
            self.client.exceptions.ResourceNotFoundException,
            self.client.exceptions.NotAuthorizedException,
            self.client.exceptions.InternalErrorException,
            self.client.exceptions.TooManyRequestsException,
            self.client.exceptions.InvalidParameterException,
            self.client.exceptions.InvalidPasswordException
        ) as e:
            data = str(e)
            status_code = 400
        except self.client.exceptions.UserNotFoundException as e:
            data = "Usuario no encontrado"
            status_code = 400
        except KeyError:
            data = "Invalid parameters"
            status_code = 400
        except Exception as e:
            data = str(e)
            status_code = 500
        # Se retorna respuesta.

        return self.armadoBody(data, status_code)
    # metodo que deshabilita el usuario en cognito.
    def admin_disable_user(self,username):

        try:
            # se consume el servicio initiate_auth encargado de crear el token.
            response = self.client.admin_disable_user( 
            UserPoolId=self.user_pool_id,
            Username=username
            )
            # se organizan los datos para la respuesta.
            status_code = 200
            data = "proceso exitoso."
        except (
            self.client.exceptions.ResourceNotFoundException,
            self.client.exceptions.InvalidParameterException,
            self.client.exceptions.TooManyRequestsException,
            self.client.exceptions.NotAuthorizedException,
            self.client.exceptions.UserNotFoundException,
            self.client.exceptions.InternalErrorException
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

        return self.armadoBody(data, status_code)

    # metodo que habilitar el usuario en cognito.
    def admin_enable_user(self,username):

        try:
            # se consume el servicio initiate_auth encargado de crear el token.
            response = self.client.admin_enable_user( 
            UserPoolId=self.user_pool_id,
            Username=username
            )
            # se organizan los datos para la respuesta.
            status_code = 200
            data = "proceso exitoso."
        except (
            self.client.exceptions.ResourceNotFoundException,
            self.client.exceptions.InvalidParameterException,
            self.client.exceptions.TooManyRequestsException,
            self.client.exceptions.NotAuthorizedException,
            self.client.exceptions.UserNotFoundException,
            self.client.exceptions.InternalErrorException
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

        return self.armadoBody(data, status_code)
        
    # Funcion encargada de eliminar el usuario en aws.
    def delete_user_cognito(self, datos):
        # se reciben los datos necesarios para eliminar el usuario.
        username = datos["INFORMACION_BASICA"]["EMAIL"]
        # se consume el servicio admin_delete_user encargado de eliminar el usuario en aws.
        response = self.client.admin_delete_user(
            UserPoolId=self.user_pool_id,
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
