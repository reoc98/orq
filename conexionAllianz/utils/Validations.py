from utils.Response import Response
import json
from datetime import datetime

class Validations(Response):

    # funcion auxiliar para mostrar mensajes de error como respuesta
    def auxFunction(self, auxKeys):
        keys = ""

        keys = "".join([f"{key}, " for key in auxKeys])

        message = keys[:-2]

        return message

    # funcion que valida la entrada de datos
    def verifyValues(self, data, keysRule):

        notTypeKeys = []

        cont = 1

        for key in data:
            if not(type(data[key]) == type(keysRule[key][0])):

                typeValue = str(type(keysRule[key][0])).replace("class", "").replace("<", "").replace(">", "").replace("'", "")

                notTypeKeys.append(f"{cont} - el campo {key} debe ser de tipo{typeValue}")

                cont += 1
            # valida el numero limite de caracteres
            elif  len(keysRule[key]) > 2:
                if (len(str(data[key])) >  keysRule[key][2]) and keysRule[key][2] > 0:
                    notTypeKeys.append(f"{cont} - El campo {key} supera el límite de caracteres establecidos ({keysRule[key][2]}).")

                    cont += 1
            # valida el formato fecha
            if len(keysRule[key]) > 3:
                try:
                    if data[key]:
                        if (keysRule[key][2] == len(str(data[key]))):
                        
                            if keysRule[key][2] == 6:
                                data[key] = int(f'{data[key]}01')

                            datetime.strptime(str(data[key]), '%Y%m%d')
                            cont += 1
                        else:
                            notTypeKeys.append(f"{cont} - El campo {key} no cumple con los caracteres establecidos ({keysRule[key][2]}).")
                            cont += 1

                except ValueError:
                    notTypeKeys.append(f"{cont} - El campo {key} no es una fecha válida.")
                    cont += 1

        if len(notTypeKeys) > 0:

            if len(notTypeKeys) > 1:
                return self.armadoBody(notTypeKeys, 400)

            else:
                message = notTypeKeys[0][4:]
                statusCode = 400

        else:
            # badKeys = [key for key, value in data.items() if type(value) == str if str(value).replace(" ","").isnumeric()] 

            # message = self.auxFunction(badKeys)

            # if len(badKeys) > 1:
            #     message = f"los campos {message} no pueden ser numericos."
            #     statusCode = 400

            # elif len(badKeys) == 1:
            #     message = f"el campo {message} no puede ser numerico"
            #     statusCode = 400

            # else:
            message = "proceso exitoso"
            statusCode = 200

        return self.armadoBody(message, statusCode)

    # funcion que valida el envio de los campos rqueridos
    def validateInput(self, data, keysRule):

        try:
            notInKeysRule = [key for key in keysRule if not(key in data.keys()) and keysRule[key][1] == 1]
            notInData = [key for key in data.keys() if not(key in keysRule)]
            
            if len(notInKeysRule) > 0:
                message = self.auxFunction(notInKeysRule)

                if len(notInKeysRule) > 1:
                    message = f"los campos {message} no están siendo enviados."
                else:
                    message = f"el campo {message} no está siendo enviado"

            elif len(keysRule) < len(data):
                message = f"solo debe enviar los datos requeridos"

            elif len(notInData):
                message  = self.auxFunction(notInData)
                message = f"Solo debe enviar los datos requeridos.Los campos ({message}) no deben ser enviados."

            else:
                return self.validateInputEmpty(data, keysRule)

            return self.armadoBody(message, 400)

        except Exception as error:
            return self.armadoBody(str(error), 400)

    # funcion que valida que los datos no estén llegando vacios
    def validateInputEmpty(self, data, keysRule):
        try:
            emptyKeys = [key for key, value in data.items() if type(value) != bool if (len(str(value).replace(" ", "")) == 0 or (type(value) != int and type(value) != float and value != None and len(value) == 0)) and keysRule[key][1] == 1]

            if len(emptyKeys) > 0:
                message = self.auxFunction(emptyKeys)

                if len(emptyKeys) > 1:
                    message = f"los campos {message} no deben estar vacíos."

                else:
                    message = f"el campo {message} no debe estar vacío."

                return self.armadoBody(message, 400)

            else:
                return self.verifyValues(data, keysRule)

        except Exception as error:
            return self.armadoBody(str(error), 400)

    def json_validator(self, data):   
        try:
            payload = json.loads(data)
            return { "message": "OK", "statusCode": 200, "data": payload }
        
        except Exception as error:
            return self.armadoBody("El formato no corresponde al requerido.", 400)

    def get_token_header(self, data_header):   
        try:
            
            token = data_header.get("authorization", False)
            if not(token):
                raise Exception()
            
            return token
            
        except Exception as error:
            raise ValueError("El formato Header no corresponde al requerido.")
