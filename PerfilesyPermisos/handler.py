from clases.ModulesPermissions import ModulesPermissions
from clases.Perfiles import Perfiles
from clases.PerfilesPermisos import PerfilesPermisos
from utils.Response import Response
from utils.Validations import Validations
from entity.PerfilesPermisosEntity import PerfilesPermisosEntity


# Funcion para obtener Modulos
def getModulos(event, context):
    try:
        return ModulesPermissions.get_modules()
    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion para obtener los permisos
def permisos(event, context):
    try:
        return ModulesPermissions.permissions_by_module()
    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion para crear perfil
def crearPerfil(event, context):
    try:
        response = Validations.json_validator(event['body'])
        if response["statusCode"] == 200:
            payload = response['data']
            keysRule = PerfilesPermisosEntity.keyRules('crearPerfil')

            # se validan los datos.
            response = Validations.validateInput(payload, keysRule)
            if response["statusCode"] == 200:
                response = Validations.verifyValues(payload, keysRule)
                if response["statusCode"] == 200:
                    # Se invoca a la funcion encargada realizar el insert
                    response = PerfilesPermisos.crearPerfil(payload)
            
        return response
    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion que se encarga de obtener todos los perfiles 
def getPerfiles(event, context):
    try:
        response = Validations.json_validator(event['body'])
        if response["statusCode"] == 200:
            payload = response['data']
            keysRule = PerfilesPermisosEntity.keyRules('getPerfiles')

            # se validan los datos obtenidos
            response = Validations.validateInput(payload, keysRule)
            if response["statusCode"] == 200:
                response = Perfiles.get_all(payload)

        return response

    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion que se encarga de recibir ID de perfil y obtener los usuarios asignados al perfil
def getPerfil(event, context): 
    try:
        response = Validations.json_validator(event['body'])
        if response["statusCode"] == 200:
            payload = response['data']
            #Se recibe el ID del perfil  
            keysRule = PerfilesPermisosEntity.keyRules('getPerfil')

            # se validan los datos obtenidos
            response = Validations.validateInput(payload, keysRule)

            if response["statusCode"] == 200:
                response = Perfiles.get_one(payload)
                
        return response
        
    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion para eliminar Perfiles, Recibe el ID del perfil y el comentario
def eliminarPerfil(event, context):
    try:
        response = Validations.json_validator(event['body'])
        if response["statusCode"] == 200:
            payload = response['data']
            keysRule = PerfilesPermisosEntity.keyRules('eliminarPerfil')

            # se validan los datos.
            response = Validations.validateInput(payload, keysRule)
            if response["statusCode"] == 200:
                response = Validations.verifyValues(payload, keysRule)
                if response["statusCode"] == 200:
                    # Se invoca a la funcion encargada realizar el insert
                    response = PerfilesPermisos.eliminarPerfil(payload)
            
        return response
    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion para editar perfil
def editarPerfil(event, context):
    try:
        response = Validations.json_validator(event['body'])
        if response["statusCode"] == 200:
            payload = response['data']
            keysRule = PerfilesPermisosEntity.keyRules('editarPerfil')

            # se validan los datos.
            response = Validations.validateInput(payload, keysRule)
            if response["statusCode"] == 200:
                response = Validations.verifyValues(payload, keysRule)
                if response["statusCode"] == 200:
                    # Se invoca a la funcion encargada realizar el insert
                    response = PerfilesPermisos.editarPerfil(payload)
                
            return response
    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion para obtener perfil y Permisos
def getPerfilPermisos(event, context):
    try:
        response = Validations.json_validator(event['body'])
        if response["statusCode"] == 200:
            payload = response['data']
            keysRule = PerfilesPermisosEntity.keyRules('getPerfil')

            # se validan los datos.
            response = Validations.validateInput(payload, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                response = PerfilesPermisos.getPerfilPermisos(payload)
                
            return response
    except Exception as e:
        return Response.internal_server_error(str(e))

# Funcion para valdiar los permisos que tiene un usuario
def validatePermissions(event, context):
    try:
        response = Validations.json_validator(event['body'])
        if response["statusCode"] == 200:
            payload = response['data']
            keysRule = PerfilesPermisosEntity.keyRules('validarPermisos')

            # se validan los datos.
            response = Validations.validateInput(payload, keysRule)
            if response["statusCode"] == 200:
                # Se invoca a la funcion encargada realizar el insert
                response = PerfilesPermisos.validatePermissions(payload)
            
        return response
    except Exception as e:
        return Response.internal_server_error(str(e))
