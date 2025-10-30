from models.RequestsOrquestador import RequestsOrquestador as RequestsOrquestadorModel
from models.ResponseOrquestador import ResponseOrquestador as ResponseOrquestadorModel
from models.ReportesSiniestros import ReportesSiniestros as ReporteSiniestrosModel
from models.EstadosReportes import EstadosReportes as EstadosReportesModel
from models.Departamentos import Departamentos as DepartamentosModel
from models.TipoFecha import TipoFecha as TipoFechaModel
from models.Ciudades import Ciudades as CiudadesModel
from models.Meses import Meses as MesesModel

from classes.Database import Database
from classes.PermissionsDatabase import PermissionsDatabase

from utils.Response import Response
from utils.Validation import Validation

from sqlalchemy.sql import func, desc, and_
from datetime import datetime

import json
import math

class ReporteSiniestros(Response, Validation):          

    # consulta encargada de obtener tipos de fechas
    @classmethod
    def __query_tipofecha(cls, type):
        session = Database("dbr").session
        try :
            return session.query(
                TipoFechaModel
            ).filter(
                TipoFechaModel.id == type
            ).first()
        except Exception as e:
            return cls.internal_server_error(str(e))
        finally:
            session.invalidate()
            session.close()
        
    
    @classmethod
    def __validate_date_now(cls, name, date):
        # valida que la fecha sea mayor a 1 de enero de 2023
        minimum_date = datetime.strptime("2023-01-01", '%Y-%m-%d')
        if date < minimum_date: 
            raise ValueError(
                f"La fecha {name} no puede ser menor a 1 de enero de 2023")
        # valida que la fecha no sea mayor a la fecha actual
        if date > datetime.now():  
            raise ValueError(
                f"La fecha {name} no puede ser mayor a la fecha actual")
        
        
    # Funcion para dar formato a la fecha
    @classmethod
    def __format_date(cls, date):
        try:
            # Le damos el formato con el cual va a entrar y salir para hacer el cambio del formato
            entry = '%d-%m-%Y'
            out = '%Y-%m-%d'

            dateFormat = datetime.strptime(date, entry)
            formatted_date = dateFormat.strftime(out)
            
            return formatted_date
        except Exception as error:
            return False 
        
    # Funcion encragada de crear filtros en la consulta del listado
    @classmethod
    def build_filter(cls, request_body):
        try:
            filter_list = []
             # valida que se recibe un numero de siniestro a filtrar
            if 'no_siniestro' in request_body:    
                filter_list.append(RequestsOrquestadorModel.numero_siniestro.like(f"%{request_body['no_siniestro']}%")) 
                        
            # valida que se recibe un numero de siniestro a filtrar
            if 'departamento' in request_body:
                if request_body['departamento'] != 0:
                    filter_list.append(DepartamentosModel.id == request_body['departamento'])  

             # valida que se recibe un numero de siniestro a filtrar
            if 'ciudad' in request_body: 
                if request_body['departamento'] != 0:   
                    filter_list.append(CiudadesModel.id == request_body['ciudad'])

            # valida que se recibe fecha a filtrar
            if 'tipo_fecha' in request_body:

                if request_body['tipo_fecha'] != 0:
                    tipo_fecha = cls.__query_tipofecha(request_body['tipo_fecha'])
                    
                    #se valida el tipo de fecha a filtrar: entrada o salida
                    if tipo_fecha.descripcion == "De ocurrencia":
                        table = RequestsOrquestadorModel.fecha_hora_ocurrencia
                    elif tipo_fecha.descripcion == "Salida":
                        table = ResponseOrquestadorModel.fecha_reg

                    #se crea filtro depende la fecha enviada por la peticion
                    if 'fecha_inicial' in request_body:
                        filter_list.append(
                            table >= request_body['fecha_inicial']+' 00:00:00')
                    if 'fecha_final' in request_body:
                        filter_list.append(
                            table <= request_body['fecha_final']+' 23:59:59')
                
            return filter_list
        except Exception as error:
            return ValueError("Error al realizar filtros del listado") 
        
    # Función encargada de obtener el listado de siniestros
    @classmethod
    def get_siniestros(cls, request_body):
        resp_permission = cls.validate_permission(user = request_body['id_usuario'], type = "LISTAR")
        if resp_permission == False:
            raise ValueError("No cuenta con los permisos necesarios para realizar esta operación.")
        
        if 'tipo_fecha' in request_body:
        
            #valida que reciba mínimo una fecha para filtrar
            if 'fecha_inicial' not in request_body and 'fecha_final' not in request_body:
                raise ValueError (
                    "Debe seleccionar la fecha inicial o fecha final")
            elif 'fecha_inicial' in request_body and 'fecha_final' in request_body:
                #valida que la fecha inicial sea menor que fecha final
                if request_body['fecha_inicial'] > request_body['fecha_final']:
                    raise ValueError (
                        "La fecha inicial debe ser menor que la fecha final")

            if 'fecha_inicial' in request_body:    
                initial_formatted = cls.__format_date(request_body['fecha_inicial'])
                if initial_formatted == False:
                    raise ValueError(
                        'Formato de fecha inicial incorrecto')
                
                cls.__validate_date_now('inicial', datetime.strptime(
                            initial_formatted, '%Y-%m-%d'))
                
                request_body['fecha_inicial'] = initial_formatted

            if 'fecha_final' in request_body:
                final_formatted = cls.__format_date(request_body['fecha_final'])
                if final_formatted == False:
                    raise ValueError(
                        'Formato de fecha final incorrecto')
                
                cls.__validate_date_now('final', datetime.strptime(
                            final_formatted, '%Y-%m-%d'))
                
                request_body['fecha_final'] = final_formatted
        
        db = Database("dbr").session
        try: 

            limit = int(request_body['num_resultados'])
            page_now = int(request_body['pagina_actual'])
            
            offset = (page_now - 1) * limit

            subquery = db.query(
                RequestsOrquestadorModel.numero_siniestro,
                func.max(RequestsOrquestadorModel.id).label('max_id'),
                func.count().label('validations')
            ).filter(
                RequestsOrquestadorModel.risk == 1,
                RequestsOrquestadorModel.ejecucion == 4,
                RequestsOrquestadorModel.estado == 1
            ).group_by(
                RequestsOrquestadorModel.numero_siniestro
            ).subquery()

            query = db.query(
                RequestsOrquestadorModel.id,
                RequestsOrquestadorModel.numero_siniestro,
                RequestsOrquestadorModel.fecha_reg,
                RequestsOrquestadorModel.fecha_hora_ocurrencia.label("ocurrence_date"),
                ResponseOrquestadorModel.fecha_reg.label("out_date"),
                RequestsOrquestadorModel.cod_ciudad.label("city_code"),
                CiudadesModel.descripcion.label("city_description"),
                DepartamentosModel.codigo.label("department_code"),
                DepartamentosModel.descripcion.label("department"),
                EstadosReportesModel.nombre,
                EstadosReportesModel.id.label("id_status"),
                subquery.c.validations,
            ).join(
                subquery, and_(
                    RequestsOrquestadorModel.numero_siniestro == subquery.c.numero_siniestro,
                    RequestsOrquestadorModel.id == subquery.c.max_id
                )
            ).join(
                EstadosReportesModel, 
                RequestsOrquestadorModel.id_estados_reportes == EstadosReportesModel.id
            ).outerjoin(
                ResponseOrquestadorModel, 
                RequestsOrquestadorModel.id == ResponseOrquestadorModel.id_request
            ).outerjoin(
                DepartamentosModel, 
                RequestsOrquestadorModel.cod_departamento == DepartamentosModel.codigo
            ).outerjoin(
                CiudadesModel, 
                and_(RequestsOrquestadorModel.cod_ciudad == CiudadesModel.codigo,
                     DepartamentosModel.codigo == CiudadesModel.codigo_departamento)
            )

            filter = cls.build_filter(request_body)

            query = query.filter(
                    *filter
                ).group_by(
                    RequestsOrquestadorModel.numero_siniestro
                ).order_by(
                    desc(RequestsOrquestadorModel.fecha_reg))
            
            results = query.limit(limit).offset(offset).all()

            if results == []:
                raise ValueError("No se encontraron datos.")

            registers = query.all()
            pages = math.ceil(len(registers) / int(request_body['num_resultados']))
        
            sinister_list = []
            for sinister in results:
                row = {'id': sinister.id,
                    'no_siniestro': sinister.numero_siniestro,
                    'fecha_salida': "" if sinister.out_date == None else datetime.strftime(sinister.out_date, "%d-%m-%Y %H:%M:%S"),
                    'fecha_hora_ocurrencia': "" if sinister.ocurrence_date == None else datetime.strftime(sinister.ocurrence_date, "%d-%m-%Y %H:%M:%S"),
                    'ciudad': sinister.city_description,
                    'departamento': sinister.department,
                    'validaciones': sinister.validations,
                    'estado': sinister.nombre,
                    'estado_id': sinister.id_status
                }

                sinister_list.append(row)
                  
            data = {'paginacion':{
                    'pagina_actual':page_now,
                    'total_paginas':pages,
                    'total_registros': len(registers),
                    'registros_por_pagina':len(results)
                   },
                'listado': sinister_list
               }

            return cls.success(data = data)
        except ValueError as e:
            return cls.error(message=f'{e}')
        except Exception as error:
            return cls.internal_server_error()
        finally:
            db.invalidate()
            db.close()

    # Función encargada de obtener los tipos de fecha que se puedan filtrar
    @classmethod
    def get_tipo_fecha(cls):
        
        db = Database("dbr").session
        try:

            result = db.query(TipoFechaModel).all()
            
            if len(result) == 0:
                raise ValueError("No se encontraron datos.")
        
            return cls.success(data = json.loads(str(result)))
        except Exception as error:
            return cls.internal_server_error(str(error))
        finally:
            db.invalidate()
            db.close()

    # Función encargada de obtener los tipos de fecha que se puedan filtrar
    @classmethod
    def get_cities(cls, id_department):
        
        db = Database("dbr").session
        
        try:
            result = db.query(
                        CiudadesModel
                    ).join(
                        DepartamentosModel,
                        CiudadesModel.codigo_departamento == DepartamentosModel.codigo
                    ).filter( 
                        CiudadesModel.estado == 1
                    )
            
            if id_department == 0:
                result = result.all()
            else:
                result = result.filter( 
                    DepartamentosModel.id == id_department
                ).all()
            
            if len(result) == 0:
                raise ValueError("No se encontraron datos.")
            
            data = json.loads(str(result))

            dic_todos = {
                "id": 0,
                "codigo": "000",
                "descripcion": "Todos"
            }

            data.insert(0, dic_todos)
        
            return cls.success(data)
        except ValueError as error:
            return cls.error(str(error))
        except Exception as error:
            return cls.internal_server_error(str(error))
        finally:
            db.invalidate()
            db.close()

    # Función encargada de obtener los tipos de fecha que se puedan filtrar
    @classmethod
    def get_departments(cls):
        
        db = Database("dbr").session
        try:

            result = db.query(DepartamentosModel
                        ).filter( 
                            DepartamentosModel.estado == 1    
                        ).all()
            
            if len(result) == 0:
                raise ValueError("No se encontraron datos.")
        
            data = json.loads(str(result))

            dic_todos = {
                "id": 0,
                "codigo": "00",
                "descripcion": "Todos"
            }

            data.insert(0, dic_todos)

            return cls.success(data)
        except Exception as error:
            return cls.internal_server_error(str(error))
        finally:
            db.invalidate()
            db.close()

    # Función encargada de obtener los meses del año
    @classmethod
    def get_months(cls):
        
        db = Database("dbr").session
        try:

            result = db.query(MesesModel).all()
            
            if len(result) == 0:
                raise ValueError("No se encontraron datos.")
        
            return cls.success(data = json.loads(str(result)))
        except Exception as error:
            return cls.internal_server_error(str(error))
        finally:
            db.invalidate()
            db.close()
    
    # Funcion para valdiar el permiso que tiene un usuario
    @classmethod
    def validate_permission(cls, user: int, type: str, module: int = 8):
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