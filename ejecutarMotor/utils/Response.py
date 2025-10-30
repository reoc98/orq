import json

class Response():
    # Funcion encargada de armar el formato de respuesta de las apis
    def armadoBody(self, message, statusCode, data = ""):

        if data == "":
            response = {
                "message" : message,
                "statusCode" : statusCode
            }

        else:
            response = {
                "message" : message,
                "statusCode" : statusCode,
                "data" : data

            }

        return {"statusCode" : statusCode, "body": json.dumps(response),
            "headers": {'Content-Type': 'application/json'}}
    
    def json_validator(self, data):   
        try:
            payload = json.loads(data)

            if "error" in payload:
                return True
            else:
                return False
            
        except Exception as error:
            print("json_validator_error", error)
            return False