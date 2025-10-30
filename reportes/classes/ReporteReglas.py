from models.Arbol import Arbol as ArbolModel 
from models.EjecucionMotor import EjecucionMotor as EjecucionMotorModel
from models.RequestsOrquestador import RequestsOrquestador
from utils.Validation import Validation
from utils.Response import Response
from classes.Database import Database
from classes.PermissionsDatabase import PermissionsDatabase
from sqlalchemy.sql import func
import json
import math

class ReporteReglas(Response, Validation):          

    @classmethod
    def __query_create_filter(cls, session, request_body):
        query = session.query(
            EjecucionMotorModel
        ).outerjoin(
            ArbolModel,
            EjecucionMotorModel.codigo_arbol == ArbolModel.codigo
        )

        if "nombre_regla" in request_body:
            if (len(request_body['nombre_regla'].replace(' ',''))) > 0:
                query = query.filter(func.replace(ArbolModel.nombre, ' ', '').like(
                    f"%{request_body['nombre_regla'].replace(' ','')}%"))
        
        return query
    
    # Función encargada de obtener el listado de reglas
    @classmethod
    def get_reglas(cls, request_body):
 
        session = Database("dbr").session
        try:
            resp_permission = cls.validate_permission(user = request_body['id_usuario'], type = "LISTAR")
            if resp_permission == False:
                raise ValueError("No cuenta con los permisos necesarios para realizar esta operación.")
        
            limit = int(request_body['num_resultados'])
            page_now = int(request_body['pagina_actual'])
            
            offset = (page_now - 1) * limit

            result = cls.__query_create_filter(
                 session, request_body)
            result = result.group_by(EjecucionMotorModel.codigo_arbol).limit(limit).offset(offset).all()

            if len(result) == 0:
                raise ValueError("No se encontraron datos")
            
            rules_list = []

            for ejecucion_motor in result:
                desenlace_contenido = session.query(
                    EjecucionMotorModel.desenlace_contenido
                ).join(
                    RequestsOrquestador, RequestsOrquestador.id == EjecucionMotorModel.id_request
                ).filter(
                    EjecucionMotorModel.codigo_arbol == ejecucion_motor.codigo_arbol,
                    RequestsOrquestador.ejecucion == 4,
                    RequestsOrquestador.estado == 1,
                    EjecucionMotorModel.estado == 1
                ).all()

                positive = 0
                negative = 0
                invalidate = 0
                validations = len(desenlace_contenido)
                
                if len(desenlace_contenido) != 0:
                    for contenido in desenlace_contenido:

                        semaforo = json.loads(contenido.desenlace_contenido.replace("\'", "\""))
                        
                        if semaforo is None:
                            invalidate = invalidate + 1
                        else:
                            if "semaforo" not in semaforo:
                                invalidate = invalidate + 1
                            else:
                                if int(semaforo["semaforo"]) == 1:
                                    positive = positive + 1
                                elif int(semaforo["semaforo"]) in (2,3):
                                    negative = negative + 1
                                else:
                                    invalidate = invalidate + 1
                else:
                    validations = 1

                # Obtenemos el nombre del motor
                name = session.query(
                        ArbolModel.nombre
                    ).filter(
                        ArbolModel.codigo == ejecucion_motor.codigo_arbol
                    ).first()


                rules_list.append({
                    'codigo_regla': ejecucion_motor.codigo_arbol,
                    'nombre_regla': "" if name is None else name.nombre,
                    'validaciones': (positive + negative + invalidate),
                    'positivas': {
                        'cantidad': positive,
                        'porcentaje': round((positive/validations)*100, 2)
                    },
                    'negativas': {
                        'cantidad': negative,
                        'porcentaje': round((negative/validations)*100, 2)
                    },
                    'no_validadas': {
                        'cantidad': invalidate,
                        'porcentaje': round((invalidate/validations)*100, 2)
                    }
                })

            registers = cls.__query_create_filter(
                 session, request_body)
            registers = registers.group_by(EjecucionMotorModel.codigo_arbol).all()

            pages = math.ceil(len(registers) / limit)
                    
            rows = {'paginacion':{
                        'pagina_actual':int(request_body['pagina_actual']),
                        'total_paginas':pages,
                        'total_registros': len(registers),
                        'registros_por_pagina':len(result)
                    },
                    'listado': rules_list
                }

            return cls.success(data = rows)
        except ValueError as e:
            return cls.error(message=f'{e}')
        
        except Exception as error:
            return cls.internal_server_error()
        finally:
            session.invalidate()
            session.close()
        
    # Funcion para valdiar el permiso que tiene un usuario
    @classmethod
    def validate_permission(cls, user: int, type: str, module: int = 9):
        try:
            data = {
                "USUARIO": user,
                "ID_MODULO": module,
                "PERMISO": type
            }

            resp_db = PermissionsDatabase.consult_permission(data)
            
            if resp_db is not None:
                return {'estado': True, "email": resp_db.CORREO}
            else:
                return False

        except Exception as e:
            raise ValueError(str(e))