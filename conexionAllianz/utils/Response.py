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