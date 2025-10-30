from utils.Validations import Validations
class LoginEntity:
    def keyRules(self, p):
        rules = {
            "send_email_recover_password": {
                "EMAIL": [str(), 1]
            },
            "recover_password": {
                "ID_USUARIO": [str(), 1],
                "ID_RECUPERAR_CONTRASENA": [int(), 1],
                "PASSWORD": [str(), 1],
                "CONFIRM_PASSWORD": [str(), 1]
            },
            "modules_by_user": {
                "ID_USUARIO": [int(), 1],
            }            ,
            "valid_link_recovery_pass": {
                "ID_RECUPERAR_CONTRASENA": [int(), 1],
                "ID_USUARIO": [str(), 1]
            },
            "submodules_by_user": {
                "ID_USUARIO": [int(), 1],
                "ID_MODULO": [int(), 1],
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

        
