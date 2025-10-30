from utils.Response import Response
from utils.Validations import Validations
from clases.PermissionsDatabase import PermissionsDatabase
from clases.MotorDatabase import MotorDatabase
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from utils.Aws import Aws, base64, os
import json

class Motor(Response, Validations):
    
    @classmethod
    def create_motor(cls, payload, token):
        try:
            request = cls.convert_motor_data(payload)

            # Validamos si el usuario tiene los permisos para relizar esta operación
            resp_permission = cls.validate_permission(user = request["usuario"], type = "CREAR")

            if resp_permission == True:
                # Validamos la existencia de los ID de lo select
                data_rel = cls.valid_items(request["relationship"])

                # Ejecutamos el consumo de Motor
                serv_resp = cls.service(payload=request["motor"], token=token)
                # Revisamos si existe un error en la creacion "Error" = (1: SI, 0:NO)
                if serv_resp["error"] == 0:
                    if cls.build_relationship(data_rel):
                        return cls.success_create(message="¡Motor guardado exitosamente!", data=serv_resp)
                    else:
                        return cls.bad_request()
                
                else: 
                    return cls.bad_request(message=serv_resp["mensaje"], data=serv_resp)

                
            else:
                raise ValueError("No cuenta con los permisos necesarios para realizar esta operación.")
                    
        except Exception as e:
            Type = type(e)
            raise Type(str(e))
            
    @classmethod
    def convert_motor_data(cls, payload):
        try:
            data_relationship = payload["datos"]["datos_relacion"]
            data_relationship["codigo"] = payload["datos"]["datos_configuracion"]["codigo"]
            del payload["datos"]["datos_relacion"]

            return {
                "motor": payload, 
                "relationship": data_relationship,
                "usuario": payload["datos"]["usuario_id"]
                }
        
        except Exception as e:
            raise Exception("Ha ocurrido un error al procesar los datos.")

    @classmethod
    def service(cls, payload, token, action: int = 1):
        try:
            param_secret = "url_motor_eliminacion" if action == 0 else "url_motor_creacion"
            
            response = False
            # Obtenemos los secreto y el Token y la URL de consumo
            secret = Aws.getSecret(str(os.getenv("STAGE"))+"/secret-orquestador")
            
            url = secret[param_secret]

            # Asignamos el token a la estructura
            payload["token"] = token
            
            send = json.dumps(payload)
            send = send.encode("utf-8")

            # Configuramos el Request
            request = Request(url=url, data=send, method="POST")
            # secret manager
            # request.add_header("Id-Token-Cognito", str(token["Idtoken"]))
            # request.add_header("Refresh-Token-Cognito", str(token["RefreshToken"]))
            # request.add_header("Access-Token", payload["token"])
            request.add_header("Access-Control-Allow-Origin", "*")
            request.add_header("Content-Type", "application/json")
            data = urlopen(request, timeout=840).read().decode("utf-8-sig")
            
            if data is None:
                raise Exception("Fallo el servicio del motor "+str(data))
            response = json.loads(data)
            if response is None:
                raise Exception("Fallo el servicio del motor "+str(response))
            
            return response

        except HTTPError as e:
            resp = json.loads(e.read())
        except URLError as e:
            resp = str(e.reason())
        except Exception as e:
            raise Exception("Fallo el servicio del motor "+str(e))
    
    @classmethod
    def build_relationship(cls, payload):
        try:
            
            # data = {
            #     "codigo": payload['codigo'],
            #     "tipo": payload["figura"].nombre,
            #     "risk": payload["fuente"].valor,
            #     "variable_comentario": payload["variable"].variable if payload["variable"] != 0 else None,
            #     "estado": 1
            # }
            # data["risk_array"] = payload["lista_risk"].lista if (data["risk"] == 1 and data["tipo"] == "Interviniente" and payload["lista_risk"] != 0) else None
            # data["vehiculo"] = payload["tipo_motor"].valor if data["tipo"] != "Siniestro" else 0

            resp_db = MotorDatabase.create_relationship(payload)
            
            return not(resp_db is None)

        except Exception as e:
            raise ValueError("No ha sido posible realizar la relación.")
        
    # Funcion para valdiar el permiso que tiene un usuario
    @classmethod
    def validate_permission(cls, user: int, type: str, module: int = 7):
        try:
            data = {
                "USUARIO": user,
                "ID_MODULO": module,
                "PERMISO": type
            }

            resp_db = PermissionsDatabase.consult_permission(data)
            
            return not(resp_db is None)
        
        except Exception as e:
            raise ValueError(str(e))       

    @classmethod
    def get_select(cls, type: str):
        try:
            type_list = ["variable", "figura", "fuente", "lista_risk", "tipo_motor"]

            if type in type_list:
                select_list = MotorDatabase.consult_select(type)

                if len(select_list):
                    list = json.loads(str(select_list))

                    if type == "variable":
                        adicional = [{"id": 0, "nombre": 'Sin comentario', "descripcion": None }]
                        adicional.extend(list)
                        list = adicional

                    return cls.success(list)
                else:
                    return cls.error(message="No se ha encontrado información.")

            else:
                return cls.error(message="No se ha encontrado información.")


        except Exception as e:
            raise Exception(str(e))

    @classmethod
    def valid_items(cls, items: dict):

        try:
            # Validamos la existencia de los ID's
            figura = MotorDatabase.exist_item("figura", items["figura"])

            if figura == None:
                raise ValueError(f"El parámetro (figura) no existe.")
                
            fuente = MotorDatabase.exist_item("fuente", items["fuente"])
            if fuente == None:
                raise ValueError(f"El parámetro (fuente) no existe.")

            # Validamos la condicion de Fuente y Figura
            if (fuente.valor != 1 or figura.nombre != "Interviniente") and items["lista_risk"] != 0:
                raise ValueError(f"No es posible seleccionar una Lista.")

            # Select Opcionales
            if items["lista_risk"] != 0:
                lista_risk = MotorDatabase.exist_item("lista_risk", items["lista_risk"])

                if lista_risk == None:
                    raise ValueError(f"El parámetro (lista_risk) no existe.")
                else:
                    lista_risk = lista_risk.lista

            else:
                lista_risk = None
                
            if items["variable"] != 0:
                variable = MotorDatabase.exist_item("variable", items["variable"])
                if variable == None:
                    raise ValueError(f"El parámetro (variable) no existe.")
                else:
                    variable = variable.variable
            else:
                variable = None

            if figura.nombre != "Siniestro":
                tipo_motor = MotorDatabase.exist_item("tipo_motor", items["tipo_motor"])
                if tipo_motor == None:
                    raise ValueError(f"El parámetro (tipo_motor) no existe.")
                else:
                    vehiculo = tipo_motor.valor
            else:
                if items["tipo_motor"] != 0:
                    raise ValueError(f"No es posible seleccionar debido a que figura es {figura.nombre}.")
                else:
                    vehiculo = 0
                    
            data = {
                "codigo": items['codigo'].upper(),
                "tipo": figura.nombre,
                "risk": fuente.valor,
                "variable_comentario": variable,
                "risk_array": lista_risk,
                "vehiculo": vehiculo,
                "estado": 1
            }
            return data

        except Exception as e:
            Type = type(e)
            raise Type(str(e))

    @classmethod
    def delete_motor(cls, payload, token):
        try:
            # Validamos si el usuario tiene los permisos para relizar esta operación
            resp_permission = cls.validate_permission(user = payload["usuario_id"], type = "ELIMINAR")

            if resp_permission == True:
                
                motor = MotorDatabase.exist_motor(payload['arbol_id'])

                if motor is not None:
                    serv_resp = cls.service(payload=payload, token=token, action=0)

                    if serv_resp["error"] == 0:
                    
                        if cls.delete_relationship(motor):
                            return cls.success()
                        else:
                            return cls.bad_request()
                    
                    else: 
                        return cls.bad_request(message=serv_resp["mensaje"], data=serv_resp)
                    
                else:
                    return cls.bad_request(message="Este motor no existe.")

            elif resp_permission == False:
                return Response.bad_request("No cuenta con los permisos necesarios para realizar esta operación.")
                    
        except Exception as e:
            raise Exception(str(e))
        
    @classmethod
    def delete_relationship(cls, motor):
        try:
            payload= {
                "estado": 0
            }
            codigo_motor = motor.codigo

            MotorDatabase.delete_relationship(payload, codigo_motor)
            
            return True

        except Exception as e:
            raise Exception("No ha sido posible eliminar la relación.")
        
    @classmethod
    def delete_arbol(cls, payload, token):
        try:
            # Validamos si el usuario tiene los permisos para relizar esta operación
            resp_permission = cls.validate_permission(user=payload["usuario_id"], type="ELIMINAR", module=3)
            if resp_permission != True:
                return Response.bad_request("No cuenta con los permisos necesarios para realizar esta operación.")

            # Validamos la existencia del arbol
            arbol = MotorDatabase.exist_arbol(payload['arbol_id'])
            if arbol is None:
                return cls.bad_request(message="Este árbol no existe.")
            

            # Buscamos si el arbol esta relacionado en alguna estructura
            motores = MotorDatabase.find_inside_motor(payload['arbol_id'])
            if motores.num_motores > 0:
                return cls.bad_request(message="No fue posible realizar la eliminación \n \
                                       Este árbol se encuentra asociado a otros motores o árboles")

            # Se agrega la data adicional que recibirá el servicio de motor
            payload["op"] = 4
            payload["entidad"] = 0
            payload["token"] = token 

            serv_resp = cls.service(payload=payload, token=token, action=0)

            if serv_resp["error"] == 0:
                return cls.success()
            else: 
                return cls.bad_request(message=serv_resp["mensaje"], data=serv_resp)
                    
        except Exception as e:
            raise Exception(str(e))
