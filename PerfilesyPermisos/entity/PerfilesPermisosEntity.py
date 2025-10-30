from utils.Validations import Validations
class PerfilesPermisosEntity:
    @classmethod
    def keyRules(cls, p):
        rules = {
            "crearPerfil":{
                "NOMBRE": [str(), 1, 50],
                "DESCRIPCION": [str(), 1, 150],
                "PERMISOS": [list(), 1, 0],
                "USUARIO": [int(), 1, 20]
            },
            "getPerfil":{
                "ID_PERFIL": [int(), 1]
            },
            "eliminarPerfil":{
                "ID_PERFIL": [int(), 1, 20],
                "COMENTARIO": [str(), 1, 150],
                "USUARIO": [int(), 1, 20]
            },
            "getPerfiles":{
                "NUM_RESULTADOS": [int(), 1],
                "PAGINA_ACTUAL": [int(), 1]
            },
            "editarPerfil":{
                "ID_PERFIL": [int(), 1, 20],
                "NOMBRE": [str(), 1, 50],
                "DESCRIPCION": [str(), 1, 150],
                "PERMISOS": [list(), 1, 0],
                "USUARIO": [int(), 1, 20]
            },
            "validarPermisos":{
                "ID_MODULO": [int(), 1],
                "ID_USUARIO": [int(), 1]
            }
        }
        if p in rules:
            return rules[p]
    
    @classmethod
    def validaList(cls, datos):
        validate = Validations()
        val = True
        response = {}
        for key,value in datos.items():
            keysRule = cls.keyRules(key)
            for  v in value:
                respuesta = validate.validateInput(v, keysRule)
                if respuesta["statusCode"] != 200:
                    val = False
                    response = respuesta
                    break
        return {
            "validate" : val,
            "response" : response
        }

        
