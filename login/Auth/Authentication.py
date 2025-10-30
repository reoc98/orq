import boto3
import os
from clases.Database import Database
from models.UsuariosModel import UsuariosModel
class Authentication:

    def __init__(self) -> None:
        self.cognito_client = boto3.client(
            'cognito-idp',
            region_name=os.getenv("REGION")
        )

    def login(self, username: str, password: str, refresh_token="") -> dict:
        """
        Iniciar sesión
        :param username: 
            Nombre de usuario
        :param password: 
            Contraseña
        :param refresh_token: 
            Token de refresco
        :return: 
            Tokens de autenticación
        """
            
        if refresh_token:
            flow_type = "REFRESH_TOKEN"
            auth_params = {
                "REFRESH_TOKEN": refresh_token
            }
        else:
            flow_type = "USER_PASSWORD_AUTH"
            auth_params = {
                "USERNAME": username,
                "PASSWORD": password
            }

        status_user = self.validate_user_enable(username)
        if (status_user == 2):
            raise ValueError("Este usuario está inhabilitado.")

        tokens = self.get_tokens(flow_type, auth_params)
        if tokens['AccessToken'] and refresh_token == "":
            tokens['user_id'] = self.get_user(username)
            
            if tokens['user_id'] is None:
                raise ValueError("Usuario no encontrado")
        return tokens

    def get_tokens(self, auth_flow: str, auth_params: dict):
        """
        Obtener tokens de autenticación
        :param auth_flow: 
            Tipo de flujo de autenticación
        :param auth_params: 
            Parámetros de autenticación
        :return: 
            Tokens de autenticación
        """
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=os.getenv('COGNITO_CLIENT_ID'),
                AuthFlow=auth_flow,
                AuthParameters=auth_params
            )
        except self.cognito_client.exceptions.UserNotFoundException as e:
            raise ValueError("Usuario no encontrado")
        except self.cognito_client.exceptions.NotAuthorizedException as e:
            raise UserWarning("Usuario o contraseña incorrectos")
        except self.cognito_client.exceptions.InvalidParameterException as e:
            raise ValueError("Parámetros inválidos")
        # except self.cognito_client.exceptions.InvalidPasswordException as e:
        #     raise ValueError("Contraseña inválida")
        # except self.cognito_client.exceptions.CodeMismatchException as e:
        #     raise ValueError("Código de verificación inválido")
        # except self.cognito_client.exceptions.ExpiredCodeException as e:
        #     raise ValueError("Código de verificación expirado")
            
        tokens_result = response["AuthenticationResult"]

        tokens = {}
        tokens["AccessToken"] = tokens_result["AccessToken"]
        tokens["Idtoken"] = tokens_result["IdToken"]

        if auth_flow == "USER_PASSWORD_AUTH":
            tokens["RefreshToken"] = tokens_result["RefreshToken"]

        return tokens

    def logout(self, access_token: str) -> None:
        """
        Cerrar sesión
        :param access_token: 
            Token de acceso
        :return: 
            None
        """
        
        # logout access token
        
        try:
            self.cognito_client.global_sign_out(
                AccessToken=access_token
            )
        except self.cognito_client.exceptions.UserNotConfirmedException as e:
            raise ValueError("Usuario no confirmado")
        except self.cognito_client.exceptions.NotAuthorizedException as e:
            raise ValueError("Access Token token inválido")
        except self.cognito_client.exceptions.InvalidParameterException as e:
            raise ValueError("Parámetros inválidos")
        except self.cognito_client.exceptions.PasswordResetRequiredException as e:
            raise ValueError("Contraseña expirada")
        except self.cognito_client.exceptions.InternalErrorException as e:
            raise ValueError("Error interno")
        except self.cognito_client.exceptions.ForbiddenException as e:
            raise ValueError("Acceso denegado")
        except self.cognito_client.exceptions.TooManyRequestsException as e:
            raise ValueError("Demasiadas solicitudes")
        except self.cognito_client.exceptions.ResourceNotFoundException as e:
            raise ValueError("Recurso no encontrado")
    
    def get_user(self, email):
        session = Database('dbr').session
        try:
            user = session.query(UsuariosModel).filter(
                UsuariosModel.email == email,
                UsuariosModel.estado == 1
            ).first()
            if user:
                return user.id
            return user
        finally:
            session.invalidate()
            session.close()

    
    def validate_user_enable(self, email):
        session = Database('dbr').session
        try:
            user = session.query(UsuariosModel).filter(
                UsuariosModel.email == email,
                UsuariosModel.estado == 2
            ).first()

            if user:
                return user.estado
            return user
        finally:
            session.invalidate()
            session.close()
