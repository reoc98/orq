from utils.Validations import Validations
class VariableEntity:
    def keyRules(self, p):
        rules = {
            "receive_request": {
                "id_regla":[int(), 1,11],
                "id_request_orquestador":[int(), 1,11]
            },
            "validar_poliza": {
                "numero_poliza":[int(), 1,20]
            },
            "get_tokens_orquestador":{
                "username": [str(), 1,0],
                "password": [str(), 1,0]
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

        
