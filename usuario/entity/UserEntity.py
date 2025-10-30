from utils.Validations import Validations
class UserEntity:
    def keyRules(self, p):
        rules = {
            "form_usuario": {
                "CODIGO_CE": [str(), 1],
                "NOMBRES": [str(), 1],
                "APELLIDOS": [str(), 1],
                "EMAIL": [str(), 1],
                "ESTADO": [int(), 1],
                "USUARIO": [int(), 1],
                "PERFILES": [list(), 1],
            },
            "set_password": {
                "ID_USUARIO": [str(), 1],
                "PASSWORD": [str(), 1],
                "CONFIRM_PASSWORD": [str(), 1],
            },
            "valid_link": {
                "ID_USUARIO": [str(), 1]
            },
            "get_users": {
                "NUM_RESULTADOS": [int(), 1],
                "PAGINA_ACTUAL": [int(), 1],
            },
            "get_user": {
                "ID_USUARIO": [int(), 1],
            },
            "edit_user": {
                "ID_USUARIO": [int(), 1],
                "CODIGO_CE": [str(), 1],
                "NOMBRES": [str(), 1],
                "APELLIDOS": [str(), 1],
                "EMAIL": [str(), 1],
                "ESTADO": [int(), 1],
                "USUARIO": [int(), 1],
                "PERFILES": [list(), 1],
                "COMENTARIO": [str(), 0,150],
            },
            "change_state_user": {
                "ID_USUARIO": [int(), 1],
                "ESTADO": [int(), 1],
                "USUARIO": [int(), 1],
                "COMENTARIO": [str(), 0,150],
            },
            "delete_user": {
                "ID_USUARIO": [int(), 1],
                "COMENTARIO": [str(), 1,150],
                "USUARIO": [int(), 1],
            }
        }
        if p in rules:
            return rules[p]
        
    def validaList(self, datos):
        validate = Validations()
        val = True
        response = {}
        for key,value in datos.items():
            keysRule = self.keyRules(key)
            for  v in value:
                if len(v) == 0:
                    continue
                respuesta = validate.validateInput(v, keysRule)
                if respuesta["statusCode"] != 200:
                    val = False
                    response = respuesta
                    break
        return {
            "validate" : val,
            "response" : response
        }

        
