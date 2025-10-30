from utils.Response import Response
from utils.Validations import Validations
from clases.Usuario import Usuario 
from entity.UserEntity import UserEntity

validate = Validations()
userEntity = UserEntity()
usuario = Usuario()


# Funcion del handler que se encarga de realizar la creacion de usuarios
def create_user(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = userEntity.keyRules('form_usuario')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                usuario = Usuario()
                response = usuario.create_user(data)

        return response
    
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as error:
        return usuario.armadoBody(str(error), 500)

# Funcion del handler que se encarga de establecer la contraseña del usuario
def set_password(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = userEntity.keyRules('set_password')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                usuario = Usuario()
                response = usuario.set_password(data)

        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as error:
        return usuario.armadoBody(str(error), 500)

# Funcion del handler que se encarga de validar que el usuario no este
# verificado
def valid_link(event, context):    
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = userEntity.keyRules('valid_link')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                usuario = Usuario()
                response = usuario.valid_link(data)

        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as error:
        return usuario.armadoBody(str(error), 500)

# metodo encargado de auto confirmar los usuarios de cognito.        
def PreSignUpOrquestador(event, context):
    """Handler/Function for return"""
    event["response"]["autoConfirmUser"] = True
    event["response"]["autoVerifyEmail"] = True

    return event

# Funcion que se encarga de obtener todos los usuarios 
def get_users(event, context):
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = userEntity.keyRules('get_users')

            # se validan los datos obtenidos
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                usuario = Usuario()
                response = usuario.get_users(data)

        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as e:
        return usuario.armadoBody(str(e), 500)

# Funcion que se encarga de recibir ID de usuario y obtener la informacion del usuario
def get_user(event, context): 
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            #Se recibe el ID del usuario  
            data = response['data']
            keysRule = userEntity.keyRules('get_user')

            # se validan los datos obtenidos
            response = validate.validateInput(data, keysRule)

            if response["statusCode"] == 200:
                usuario = Usuario()
                response = usuario.get_user(data)

        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)    
    except Exception as e:
        return usuario.armadoBody(str(e), 500)

# Funcion que se encarga de obtener todos los perfiles 
def get_perfiles(event, context):
    try:
        response = usuario.get_perfiles()
        return response

    except Exception as e:
        return usuario.armadoBody(str(e), 500)
        
        
 # Funcion que se encarga de obtener los estados disponibles de un usuario 
def get_state_users(event, context):
    try:
        response = usuario.get_state_users()
        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as e:
        return usuario.armadoBody(str(e), 500) 

# Funcion para obtener y validar los datos  de la edicion de usuario
def edit_user(event, context):
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = userEntity.keyRules('edit_user')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                usuario = Usuario()
                response = usuario.edit_user(data)

        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as error:
        return usuario.armadoBody(str(error), 500)

# Funcion para habilitar y desabilitar usuario
def change_state_user(event, context):
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            data = response['data']
            keysRule = userEntity.keyRules('change_state_user')

            # se validan los datos.
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                usuario = Usuario()
                response = usuario.change_state_user(data)

        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as error:
        return usuario.armadoBody(str(error), 500)

def delete_user(event, context): 
    try:
        response = validate.json_validator(event['body'])
        if response["statusCode"] == 200:
            #Se recibe el ID del usuario  
            data = response['data']
            keysRule = userEntity.keyRules('delete_user')

            # se validan los datos obtenidos
            response = validate.validateInput(data, keysRule)
            if response["statusCode"] == 200:
                usuario = Usuario()
                response = usuario.delete_user(data)

        return response
    except ValueError as error:
        return usuario.armadoBody(str(error), 400)
    except Exception as e:
        return usuario.armadoBody(str(e), 500)