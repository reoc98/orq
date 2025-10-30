from models.RequestsOrquestadorModel import RequestsOrquestadorModel
from models.ValorParametroModel import ValorParametroModel
from models.PerfilUsuariosModel import PerfilUsuariosModel
from models.PerfilPermisosModel import PerfilPermisosModel
from models.Ciudades import Ciudades as CiudadesModel
from models.TipoPermisoModel import TipoPermisoModel
from models.TipoDocumento import TipoDocumento
from models.PerfilesModel import PerfilesModel
from models.UsuariosModel import UsuariosModel
from models.PermisosModel import PermisosModel
from models.ModulosModel import ModulosModel
from clases.Database import Database
from utils.Response import Response
from sqlalchemy.sql import func
from datetime import datetime
import json


class RequestsOrquestador():
    def __init__(self, payload = {}):
        self.payload = payload    
        
    ##Inserta un nuevo registro en la tabla REQUESTS_ORQUESTADOR
    def insert_requests_orquestador(self):
        response = Response()
        db = Database('dbw').session
        try:
            
            ##Prepara los datos para insertarlos
            row = RequestsOrquestadorModel(self.payload)
            ##Bincula los datos
            db.add(row)
            ##Envia los datos a la DB
            db.commit()
            ##Responde el servicio
            return response.armadoBody("Proceso exitoso.", 201,json.loads(str(row)))
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
    
    def update_requests_orquestador(self,id_registro):
        response = Response()
        db = Database('dbw').session
        try:
            ##Prepara los datos para insertarlos
            row = RequestsOrquestadorModel(self.payload)
            ##Validamos que si existe un id_registro para controlar el proceso
            isset = db.query(RequestsOrquestadorModel).filter_by(id = id_registro).first()
            
            ##Sino encuentra un registro se preparan los datos pora insertarlos
            if(isset == None):
                return response.armadoBody("No se encontro registro para actualizar.", 400)
            
            ##Prepara la consulta con los datos que se van actualizar filtrando por id del registro
            query = db.query(RequestsOrquestadorModel).filter(RequestsOrquestadorModel.id == id_registro)
            ##Bincula los nuevos datos que se van actualizar
            query.update(self.payload)
            db.commit()

            ##Responde el servicio
            return response.armadoBody("Proceso exitoso.", 200)
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def consult_state_received(cls):
        db = Database('dbr').session
        try:
            
            consult = db.query(ValorParametroModel).filter(
                ValorParametroModel.codigo == 'status_received',
                ValorParametroModel.estado == 1,
            )
            rows = consult.all()
            
            return [str(row) for row in rows]
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def validate_city_code(cls, city_code, department_code):
        db = Database('dbr').session
        try: 
            result = db.query(CiudadesModel
                ).filter( CiudadesModel.codigo == city_code
                ).filter(CiudadesModel.codigo_departamento == department_code).first()
            
            return result            
        except Exception as error:
            raise ValueError(str(error))
        finally:
            db.invalidate()
            db.close()

    # Se conuslta el tipo de documento mediante el prefijo
    @classmethod
    def buscar_tipo_documento(cls, prefijo):
        db = Database('dbr').session
        try:
            
            consult = db.query(TipoDocumento.codigo).filter(
                TipoDocumento.estado == 1,
                TipoDocumento.prefijo_request == prefijo
            )
            row = consult.first()
            
            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    def validar_fecha_hora(date, time):
        try:
            # Convertimos lo valores a STR, para hacer validacion y conversion a Date
            date = str(date)
            time = str(time)

            # Se valida la estructura de las Fecha y Hora
            if(len(date) != 8):
                return None
            
            if(len(time)==3):
                time = f"0{time}"

            elif(len(time)==2):
                time = f"00{time}"
                
            elif(len(time)==1):
                time = f"000{time}"

            elif(time==0):
                time = f"000{time}"

            # Se convierten los valores de la fecha y hora
            date_time = f"{date}{time}"

            # Se convierten a Tipo DateTime para validar si la fecha ingresada es valida
            fecha_hora = datetime.strptime(date_time, '%Y%m%d%H%M')
            # Reasina la fecha aplicando los segundos y retornando
            fecha_nuevo_formato = fecha_hora.strftime('%Y%m%d%H%M%S')
            return str(fecha_nuevo_formato)

        except Exception as e:
            return None

    @classmethod
    def consult_permission(self, email_user):
        db = Database('dbr').session

        try:
            # Se arma la consulta con teniendo en cuenta usuario y modulo, para obtener los permisos relacionados
            query = db.query(func.distinct(PermisosModel.id).label('ID'), PermisosModel, TipoPermisoModel
                ).join(
                    TipoPermisoModel, TipoPermisoModel.id == PermisosModel.id_tipo_permiso
                ).join(
                    ModulosModel, ModulosModel.id == PermisosModel.id_modulo
                ).join(
                    PerfilPermisosModel, PerfilPermisosModel.id_permiso == PermisosModel.id
                ).join(
                    PerfilesModel, PerfilesModel.id == PerfilPermisosModel.id_perfil
                ).join(
                    PerfilUsuariosModel, PerfilUsuariosModel.id_perfil == PerfilesModel.id
                ).join(
                    UsuariosModel, UsuariosModel.id == PerfilUsuariosModel.id_usuario
                ).filter(
                    PermisosModel.activo == 1,
                    PerfilPermisosModel.estado == 1,
                    PerfilesModel.estado == 1,
                    PerfilUsuariosModel.estado == 1,
                    ModulosModel.id == 1,
                    TipoPermisoModel.nombre == "ENVIAR_RQ",
                    UsuariosModel.email == email_user,
                    UsuariosModel.verificado == 1,
                    UsuariosModel.estado == 1
                )

            row = query.first()         
            
            # Se valida la informacion del perfil de que exista
            return row

        except Exception as error:
            raise ValueError("Error interno del servidor")
        
        finally:
            db.invalidate()
            db.close()
