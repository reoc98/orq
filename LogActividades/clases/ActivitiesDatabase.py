from models.TipoActividadModel import TipoActividadModel
from models.LogActividadesModel import LogActividadesModel
from models.UsuariosModel import UsuariosModel
from models.PerfilesModel import PerfilesModel 
from models.PeriodosModel import PeriodosModel 
from models.ArbolModel import ArbolModel
from clases.Database import Database
from sqlalchemy.sql import func, or_
from datetime import datetime
import math
#import traceback


class ActivitiesDatabase():  
    
    # funcion encargada de crear los filtros correspondientes a
    #usuario, perfil, arbol y motor
    @classmethod
    def entity_filter(cls, payload, body):
        filters = []
        #
        if "ID_AFECTADO" not in payload and "ID_TIPO_ACTIVIDAD_USUARIO" in payload:
            payload["ID_TIPO_ACTIVIDAD_USUARIO"] = None
        if "ID_PERFIL" not in payload and "ID_TIPO_ACTIVIDAD_PERFIL" in payload:
            payload["ID_TIPO_ACTIVIDAD_PERFIL"] = None
        if "ID_MOTOR" not in payload and "ID_TIPO_ACTIVIDAD_MOTOR" in payload:
            payload["ID_TIPO_ACTIVIDAD_MOTOR"] = None
        if "ID_ARBOL" not in payload and "ID_TIPO_ACTIVIDAD_ARBOL" in payload:
            payload["ID_TIPO_ACTIVIDAD_ARBOL"] = None

        for key, value in body.items():
            if key in payload:
                if (payload[key] == 0 
                    or payload[key] == "0"):
                    
                    filters.append(
                        getattr(TipoActividadModel, "modulo") == value[1]
                    )
                elif payload[key] != None:
                    filters.append(
                        getattr(LogActividadesModel, value[0]) == payload[key]
                    )
        return filters
    

    # funcion encargada de crear los filtros en el log de actividades
    @classmethod
    def create_filter_bd(cls, payload, body):
        try:
            filters = []

            # valida que se recibe un usuario que ejecuta la actividad para filtrar
            if 'ID_USUARIO' in payload:    
                if payload['ID_USUARIO'] != 0:
                    filters.append(LogActividadesModel.usuario == payload['ID_USUARIO']) 
            
            if 'ID_PERIODO' in payload and payload['ID_PERIODO'] == 2:
                filters.append(LogActividadesModel.fecha_reg.between(
                    payload['FECHA_INICIAL']+' 00:00:00', 
                    payload['FECHA_FINAL']+' 23:59:59')) 

            for key, value in body.items():
                if key not in payload:
                    filters.append(TipoActividadModel.modulo != value[1]) 

            return filters
        
        except Exception as error:
            return { 'status': 500, 'data': str(error) }


    # funcion encargada de obtener la lista de actividades realizadas
    @classmethod 
    def get_log(cls, payload):
        
        db = Database("dbr").session
        try:
            limit = int(payload['NUM_RESULTADOS'])
            page_now = int(payload['PAGINA_ACTUAL'])

            offset = (page_now - 1) * limit
            
            #Recibe todas las actividades del log
            query = db.query(LogActividadesModel.id, 
            LogActividadesModel.fecha_reg,
            UsuariosModel.codigo_ce,
            UsuariosModel.nombres,
            UsuariosModel.apellidos,
            TipoActividadModel.nombre.label('tipo_actividad'),
            LogActividadesModel.entidad,
            TipoActividadModel.modulo
            ).outerjoin(
                UsuariosModel, 
                LogActividadesModel.usuario == UsuariosModel.id
            ).outerjoin(
                TipoActividadModel, 
                LogActividadesModel.id_tipo_actividad == TipoActividadModel.id
            )
            
            body_entity = {
            "ID_AFECTADO": ["entidad", 1],
            "ID_PERFIL" : ["entidad", 4],
            "ID_MOTOR" : ["entidad", 7],
            "ID_ARBOL" : ["entidad", 3]
            }

            body_activity = {
                "ID_TIPO_ACTIVIDAD_USUARIO" : ["id_tipo_actividad", 1],
                "ID_TIPO_ACTIVIDAD_PERFIL" : ["id_tipo_actividad", 4],
                "ID_TIPO_ACTIVIDAD_MOTOR" : ["id_tipo_actividad", 7],
                "ID_TIPO_ACTIVIDAD_ARBOL" : ["id_tipo_actividad", 3]
            }

            # Unimos los Bodys para el metodo "create_filter_bd"
            body_act_ent = { **body_entity,  **body_activity }

            #invoca funcion de crear los filtros
            filters = cls.create_filter_bd(payload, body_act_ent)
            
            #filtro por entidades en log de actividades
            entity_filters = cls.entity_filter(payload, body_entity)

            #filtro por tipo de actividad
            type_filters = cls.entity_filter(payload, body_activity)

            #ordena de manera descendente
            result = query.filter(
                *filters,
                or_(*entity_filters),
                or_(*type_filters)
            ).order_by(
                LogActividadesModel.fecha_reg.desc()
            )
            result = result.limit(limit).offset(offset).all()
            

            #conteo de cantidad de registros
            query_pages = db.query(func.count(LogActividadesModel.id).label('paginas')
            ).outerjoin(
                UsuariosModel, 
                LogActividadesModel.usuario == UsuariosModel.id
            ).outerjoin(
                TipoActividadModel, 
                LogActividadesModel.id_tipo_actividad == TipoActividadModel.id
            )

            # Nuevamente se unen en caso de modificacion una de sus parte
            body_act_ent = { **body_entity,  **body_activity }

            registers = cls.create_filter_bd(payload, body_act_ent)
            registers = query_pages.filter(
                *filters,
                or_(*entity_filters),
                or_(*type_filters)
            ).first()
            #operacion para obtener numero de paginas a mostrar
            pages = math.ceil(registers.paginas / limit)

            activities_list = []
            # recorre los resultados obtenidos para crear lista de diccionarios
            if (len(result)):
                for activity in result:
                    affected = None
                    #valida el tipo actividad
                    if(activity.modulo == 4):
                        #Recibe el nombre del perfil afectado por la actividad
                        affected = db.query(
                            PerfilesModel.nombre.label('nombre')
                        ).join(
                            LogActividadesModel, 
                            PerfilesModel.id == LogActividadesModel.entidad
                        ).filter(    
                            LogActividadesModel.id ==activity.id
                        ).first()    
                    
                    elif (activity.modulo == 1):
                        #Recibe el nombre del usuario afectado por la actividad
                        affected = db.query(
                            UsuariosModel.codigo_ce.label('nombre')
                        ).join(
                            LogActividadesModel, 
                            UsuariosModel.id == LogActividadesModel.entidad
                        ).filter(    
                            LogActividadesModel.id == activity.id
                        ).first()
                        
                    elif (activity.modulo == 3 or activity.modulo == 7):
                        #Recibe el nombre del nombre de arbol de desicion afectado por la actividad
                        affected = db.query(
                            ArbolModel.nombre.label('nombre')
                        ).join(
                            LogActividadesModel, 
                            ArbolModel.codigo == LogActividadesModel.entidad
                        ).filter(    
                            LogActividadesModel.id == activity.id
                        ).first()

                    name = "" if activity.nombres is None else activity.nombres
                    lastname = "" if activity.apellidos is None else activity.apellidos

                    #crear diccionarios
                    activities_list.append(
                        {'ID': activity.id,
                        'CODIGO': activity.codigo_ce,
                        'NOMBRE': name +" "+ lastname,
                        'FECHA': datetime.strftime(activity.fecha_reg, "%d-%m-%Y %H:%M:%S"),
                        'TIPO_ACTIVIDAD': activity.tipo_actividad, 
                        'AFECTADO': "" if affected is None else affected.nombre}
                        )
                        
                    
                rows = {'PAGINACION':{
                        'PAGINA_ACTUAL':page_now,
                        'TOTAL_PAGINAS':pages,
                        'TOTAL_REGISTROS': registers.paginas,
                        'REGISTROS_POR_PAGINA':limit
                        },
                    'LISTADO': activities_list
                    }
                return {'status': 200, 'data': rows}
            else:
                return {'status': 400}

        except Exception as error:
            return {'status': 500, 'data': str(error)}
        finally:
            db.invalidate()
            db.close()

    # funcion encargada de obtener los usuarios
    @classmethod 
    def get_users_log_bd(cls, option):
        db = Database("dbr").session
        try:
            
            #valida si el usuarios sera quien ejecuta la accion o usuario afectado
            if(option == 1):
                result = db.query( func.distinct(LogActividadesModel.usuario).label('id'),
                UsuariosModel.codigo_ce
                ).join(UsuariosModel,
                    LogActividadesModel.usuario == UsuariosModel.id
                ).all()

            elif (option == 2):
                result = db.query(UsuariosModel.id,
                UsuariosModel.codigo_ce
                ).all()
            
            return result
    
        except Exception as error:
            return { 'status': 500, 'data': str(error) }
        finally:
            db.invalidate()
            db.close()

    # funcion encargada de obtener todos los perfiles
    @classmethod 
    def get_profiles_log_bd(cls):
        db = Database("dbr").session
        try:

            result = db.query(PerfilesModel.id,
                PerfilesModel.nombre
            ).all()
        
            return result

        except Exception as error:
            print (error)
            return { 'status': 500, 'data': str(error) }
        finally:
            db.invalidate()
            db.close()

    # funcion encargada de obtener todos los tipos de actividades
    @classmethod 
    def get_activity_type_bd(cls, payload):
        db = Database("dbr").session
        try:

            result = db.query(TipoActividadModel.id,
                TipoActividadModel.nombre
            ).filter(
                TipoActividadModel.modulo == payload['ID_MODULO'],
                TipoActividadModel.estado == 1
            ).all()
            
            return result

        except Exception as error:
            return { 'status': 500, 'data': str(error) }
        finally:
            db.invalidate()
            db.close()
    
    # Funcion para obtener las actividades
    @classmethod
    def get_activity_bd(cls, id_activity):
        db = Database("dbr").session
        try:
            result = db.query(
                LogActividadesModel, TipoActividadModel, UsuariosModel
            ).join(
                TipoActividadModel, 
                LogActividadesModel.id_tipo_actividad == TipoActividadModel.id
            ).join(
                UsuariosModel,
                LogActividadesModel.usuario == UsuariosModel.id
            ).filter(
                LogActividadesModel.id == id_activity
            ).first()
            
            if result is None:
                return {'status': 400}
            else:
                return {'status': 200, 'data': result}
            
        except Exception as error:
            return { 'status': 500, 'data': str(error)}
        finally:
            db.invalidate()
            db.close()

    # Funcion para obtener las actividades
    @classmethod
    def get_user(cls, id_user):
        db = Database("dbr").session
        try:
            result = db.query(
                UsuariosModel.fullname.label("nombre") 
            ).filter(
                UsuariosModel.id == id_user
            ).first()
            
            return result
            
        except Exception as error:
            return { 'status': 500, 'data': str(error) }
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def get_perfil(cls, id_perfil):
        db = Database("dbr").session
        try:
            result = db.query(
                PerfilesModel.nombre
            ).filter(
                PerfilesModel.id == id_perfil
            ).first()
            
            return result
            
        except Exception as error:
            return {'status': 500, 'data': str(error)}
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def get_arbol(cls, id_arbol):
        db = Database("dbr").session
        try:
            result = db.query(
                ArbolModel.nombre
            ).filter(
                ArbolModel.codigo == id_arbol
            ).first()
            
            return result
            
        except Exception as error:
            return {'status': 500, 'data': str(error)}
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def get_period_bd(cls):
        db = Database("dbr").session
        try:

            result = db.query(PeriodosModel).all()
            
            return result
        except Exception as error:
            return {'status': 500, 'data': str(error)}
        finally:
            db.invalidate()
            db.close()

    # funcion encargada de obtener todos los perfiles
    @classmethod 
    def get_arboles_log_bd(cls, tipo):
        db = Database("dbr").session
        try:

            result = db.query(
                ArbolModel.codigo,
                ArbolModel.nombre
            ).filter(
                ArbolModel.padre == tipo
            ).group_by(
                ArbolModel.codigo
            ).order_by(
                ArbolModel.id.desc()
            ).all()
        
            return result

        except Exception as error:
            return {'status': 500, 'data': str(error)}
        finally:
            db.invalidate()
            db.close()
