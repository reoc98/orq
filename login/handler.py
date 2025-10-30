from Auth.Authentication import Authentication as Auth
from utils.Response import Response
from utils.Validations import Validations
from clases.Login import Login 
from entity.LoginEntity import LoginEntity

responseData = Response()
validate = Validations()
loginEntity = LoginEntity()

# Funcion para recuperar la contraseña del usuario
def send_email_recover_password(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = loginEntity.keyRules('send_email_recover_password')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                login = Login()
                response = login.send_email_recover_password(data)

        return response
    except ValueError as error:
        return responseData.armadoBody(
            message=str(error),
            statusCode=400
            )
    except Exception as error:
        return responseData.armadoBody(str(error), 500)

# Funcion para recuperar la contraseña del usuario
def valid_link_recovery_pass(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = loginEntity.keyRules('valid_link_recovery_pass')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                login = Login()
                response = login.valid_link_recovery_pass(data)

        return response
    except ValueError as error:
        return responseData.armadoBody(
            message=str(error),
            statusCode=400
        )
    except Exception as error:
        return responseData.armadoBody(str(error), 500)

# Funcion para recuperar la contraseña del usuario
def recover_password(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = loginEntity.keyRules('recover_password')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                login = Login()
                response = login.recover_password(data)

        return response
    except ValueError as error:
        return responseData.armadoBody(
            message=str(error),
            statusCode=400
        )
    except Exception as error:
        return responseData.armadoBody(str(error), 500)

# Funcion que valida los modulos que puede ver un usuario
def get_modules_by_user(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = loginEntity.keyRules('modules_by_user')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:

                # Se invoca a la funcion encargada realizar el insert
                login = Login()
                response = login.get_modules_by_user(data)

        return response
    except ValueError as error:
        return responseData.armadoBody(
            message=str(error),
            statusCode=400
        )
    except Exception as error:
        return responseData.armadoBody(str(error), 500)

# Funcion que valida los submodulos de un modulo que puede ver un usuario
def get_submodules_by_user(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = loginEntity.keyRules('submodules_by_user')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:

                # Se invoca a la funcion encargada realizar el insert
                login = Login()
                response = login.get_submodules_by_user(data)

        return response
    except ValueError as error:
        return responseData.armadoBody(
            message=str(error),
            statusCode=400
        )
    except Exception as error:
        return responseData.armadoBody(str(error), 500)
    
def login(event, context):
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            auth = Auth()

            request_body = response['data']

            email = request_body["email"]
            password = request_body["password"]

            response = auth.login(email, password)
            if response:
                response = responseData.armadoBody(
                    message = "Login exitoso", 
                    statusCode = 200, 
                    data = response
                )
            else:
                response = responseData.armadoBody(
                    message = "Error al iniciar sesión", 
                    statusCode = 400,
                    data = response
                )

    except KeyError as e:
        response = responseData.armadoBody(
            message = f"Error al iniciar sesión, parametro {e} no encontrado",
            statusCode = 400
        )
    except ValueError as e:
        response = responseData.armadoBody(
            message=f'{e}',
            statusCode=400
        )
    except UserWarning as e:
        response = responseData.armadoBody(
            message=f'{e}',
            statusCode=401
        )
    except Exception as e:
        response = responseData.armadoBody(
            message = f"Error interno del servidor",
            statusCode = 500
        )
    return response


def refresh_token(event, context):
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            auth = Auth()

            request_body = response['data']

            refresh_token = request_body["refresh_token"]

            response = auth.login("", "", refresh_token)
            if response:
                response = responseData.armadoBody(
                    message="Petición exitosa",
                    statusCode=200,
                    data=response
                )
            else:
                response = responseData.armadoBody(
                    message="Error al refrescar el token",
                    statusCode=400,
                    data=response
                )

    except KeyError as e:
        response = responseData.armadoBody(
            message=f"Error al iniciar sesión, parametro {e} no encontrado",
            statusCode=400
        )
    except ValueError as e:
        response = responseData.armadoBody(
            message=f"Error al iniciar sesión",
            statusCode=400
        )
    except Exception as e:
        response = responseData.armadoBody(
            message = f"Error interno del servidor",
            statusCode = 500
        )

    return response


def logout(event, context):
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            auth = Auth()

            request_body = response['data']

            access_token = request_body["access_token"]

            response = auth.logout(access_token)
            response = responseData.armadoBody(
                message="Petición exitosa",
                statusCode=200,
                data=response
            )

    except KeyError as e:
        response = responseData.armadoBody(
            message=f"Error al iniciar sesión, parametro {e} no encontrado",
            statusCode=400
        )
    except ValueError as e:
        response = responseData.armadoBody(
            message=f"Error al iniciar sesión",
            statusCode=400
        )
    except Exception as e:
        response = responseData.armadoBody(
            message = f"Error interno del servidor",
            statusCode = 500
        )

    return response
