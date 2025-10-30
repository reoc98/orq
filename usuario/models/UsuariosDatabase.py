
from models.UsuariosModel import UsuariosModel
from models.PerfilUsuariosModel import PerfilUsuariosModel
from models.PerfilesModel import PerfilesModel
from models.EstadosUsuarioModel import EstadosUsuarioModel
from models.TipoActividadModel import TipoActividadModel
from models.LogActividadesModel import LogActividadesModel
from models.PerfilPermisosModel import PerfilPermisosModel
from models.ModulosModel import ModulosModel
from models.PermisosModel import PermisosModel
from models.TipoPermisoModel import TipoPermisoModel
from clases.Database import Database
from sqlalchemy import update
from utils.Response import Response
from sqlalchemy.sql import func
import json
import math

class UsuariosDatabase():
        
    # Inserta un nuevo registro en la tabla USUARIOS
    def insert_user(self, payload):
        response = Response()
        db = Database('dbw').session

        try:
            ##Prepara los datos para insertarlos
            row = UsuariosModel(payload)
            ##Bincula los datos
            db.add(row)
            ##Envia los datos a la DB
            db.commit()
            datos_usuario = json.loads(str(row))

            ##Responde el servicio
            return response.armadoBody("Proceso exitoso.", 201, datos_usuario)
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Inserta un nuevo registro en la tabla PERFIL_USUARIOS
    def insert_profile_user(self, payload):
        response = Response()
        db = Database('dbw').session

        try:
            ##Prepara los datos para insertarlos
            row = PerfilUsuariosModel(payload)
            ##Bincula los datos
            db.add(row)
            ##Envia los datos a la DB
            db.commit()

            ##Responde el servicio
            return response.armadoBody("Proceso exitoso.", 201)
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el correo ya existe
    def valid_email(self, email):
        response = Response()
        db = Database('dbr').session

        try:
            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.EMAIL == email, 
                UsuariosModel.ESTADO != 0
            ).first()

            if search is None:
                resp = response.armadoBody("Correo disponible.", 200)
            else:
                resp = response.armadoBody("El correo ya existe.", 400)

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el correo ya existe
    def val_codigo_ce_unique(self, codigo_ce):
        response = Response()
        db = Database('dbr').session

        try:
            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.CODIGO_CE == codigo_ce, 
                UsuariosModel.ESTADO != 0
            ).first()

            if search is None:
                resp = True
            else:
                resp = False

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el usuario existe
    def valid_user(self, id_usuario):
        response = Response()
        db = Database('dbr').session

        try:
            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.ID == id_usuario, 
                UsuariosModel.ESTADO != 0
            ).first()

            if search is None:
                resp = response.armadoBody("El usuario no existe.", 400)
            else:
                resp = response.armadoBody("OK.", 200, json.loads(str(search)))

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el link ya fue verificado
    def valid_link(self, id_usuario):
        response = Response()
        db = Database('dbr').session

        try:
            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.ID == id_usuario, 
                UsuariosModel.ESTADO != 0,
                UsuariosModel.VERIFICADO == 0,
            ).first()

            if search is None:
                msj = "El usuario ya fue verificado."
                resp = response.armadoBody(msj, 400)
            else:
                resp = response.armadoBody("OK.", 200, json.loads(str(search)))

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Funcion encargada de realizar la actualizacion de la contraseña
    def update_pass_user(self, payload):
        response = Response()
        db = Database("dbw").session

        try:
            update_values = {
                "PASSWORD": payload["PASSWORD"],
                "VERIFICADO": 1
            }

            db.execute(
                update(UsuariosModel).where(
                    UsuariosModel.ID == payload["ID_USUARIO"]
                ).values(update_values)
            )
            db.commit()

            # Responde el servicio
            return response.armadoBody("Contraseña actualizada.", 200)

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Funcion encargada de recibir todos los usuarios
    def get_users(self, payload):
        response = Response()
        db = Database("dbr").session

        try:
            limit = int(payload['NUM_RESULTADOS'])
            page_now = int(payload['PAGINA_ACTUAL'])

            offset = (page_now - 1) * limit

            #Recibe todos los usuarios de la BD
            result = db.query(UsuariosModel.ID,
            UsuariosModel.CODIGO_CE,
            UsuariosModel.NOMBRES,
            UsuariosModel.APELLIDOS,
            UsuariosModel.EMAIL,
            UsuariosModel.ESTADO
            ).filter(
                UsuariosModel.ESTADO != 0
            ).limit(limit).offset(offset).all()

            #conteo de cantidad de registros
            registers = db.query(func.count(UsuariosModel.ID).label('PAGINAS')).filter(UsuariosModel.ESTADO != 0).first()
            #operacion para obtener numero de paginas a mostrar
            pages = math.ceil(registers.PAGINAS / limit)
            
            users_list = []
            # recorre los resultados obtenidos para crear lista de diccionarios
            for user in result:
                
                # valida el estado del usuario
                if(user.ESTADO == 1):
                    state = 'Habilitado'
                elif (user.ESTADO == 2):
                    state = 'Congelado'

                users_list.append(
                    {'ID': user.ID,'CODIGO_CE':user.CODIGO_CE,
                    'NOMBRES': user.NOMBRES,
                    'APELLIDOS': user.APELLIDOS,
                    'EMAIL': user.EMAIL,
                    'ESTADO': state}
                )

            rows = {
                    'PAGINACION':{
                            'PAGINA_ACTUAL':page_now,
                            'TOTAL_PAGINAS':pages,
                            'TOTAL_REGISTROS': registers.PAGINAS,
                            'REGISTROS_POR_PAGINA':limit
                        },
                    'LISTADO': users_list
                }

            if (len(result)):
                return response.armadoBody("Servicio exitoso.", 200, rows)
            else:
                return response.armadoBody("No se encontraron datos.", 400)

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()


    def get_perfiles_byuser(self, id_user):
        db = Database("dbr").session

        try:
            #Recibe los perfiles asignados al usuario dado
            result = db.query(PerfilUsuariosModel.ID.label('ID_PERFILUSUARIOS'),
            PerfilesModel.ID.label('ID_PERFIL'),
            PerfilesModel.NOMBRE
                ).join(
                    PerfilesModel,
                    PerfilUsuariosModel.ID_PERFIL == PerfilesModel.ID
                ).filter(
                    PerfilUsuariosModel.ID_USUARIO == id_user,
                    PerfilesModel.ESTADO == 1,
                    PerfilUsuariosModel.ESTADO == 1
                ).all()
            
            rows = []
            #valida si se recibió algún dato 
            if (len(result)):
                # recorre los resultados obtenidos para crear lista
                for user_perfil in result:
                    rows.append({
                        'ID_PERFILUSUARIOS' : user_perfil.ID_PERFILUSUARIOS,    
                        'ID': user_perfil.ID_PERFIL,
                        'NOMBRE': user_perfil.NOMBRE})
            return rows
        
        except Exception as error:
            return None
        
        finally:
            db.invalidate()
            db.close()

    # Funcion encargada de recibir los perfiles asignados a un usuario
    def get_user(self, payload):
        response = Response()

        try:
            rows = self.get_perfiles_byuser(payload['ID'])
                
            user_info = {'ID': payload['ID'],'CODIGO_CE':payload['CODIGO_CE'],
                        'NOMBRES': payload['NOMBRES'],
                        'APELLIDOS': payload['APELLIDOS'],
                        'EMAIL': payload['EMAIL'],
                        'ID_ESTADO': payload['ESTADO'] }

            data = {
                'INFORMACION_BASICA': user_info,
                'PERFILES':rows
            }

            return response.armadoBody("Servicio exitoso.", 200, data)

        except Exception as error:
            return response.armadoBody(str(error), 500)

    # Funcion encargada de recibir todos los perfiles creados
    def get_perfiles(self):
        response = Response()
        db = Database("dbr").session

        try:
            #Recibe todos los perfiles activos de la BD
            result = db.query(PerfilesModel.ID,
            PerfilesModel.NOMBRE
            ).filter(
                PerfilesModel.ESTADO == 1
            ).all()

            rows = []
            if (len(result)):
                # recorre los resultados obtenidos para crear lista
                for user_perfil in result:

                    rows.append({
                    'ID': user_perfil.ID,
                    'NOMBRE': user_perfil.NOMBRE})
                return response.armadoBody("Servicio exitoso.", 200, rows)
            else:
                return response.armadoBody("No se encontraron datos.", 400)

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
    
    # Funcion encargada de recibir todos los estados que puede tener un usuario
    def get_state_users(self):
        response = Response()
        db = Database("dbr").session

        try:
            #Recibe todos los estados de la BD
            result = db.query(EstadosUsuarioModel.ID,
            EstadosUsuarioModel.DESCRIPCION
            ).all()

            rows = []
            if (len(result)):
                # recorre los resultados obtenidos para crear lista
                for state_user in result:

                    rows.append({
                    'ID': state_user.ID,
                    'DESCRIPCION': state_user.DESCRIPCION})
                return response.armadoBody("Servicio exitoso.", 200, rows)
            else:
                return response.armadoBody("No se encontraron datos.", 400)

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Validar si el correo, está repetido, (Editar Usuario)
    def valid_email_edit(self, payload):
        response = Response()
        db = Database('dbr').session

        try:
            email = payload['EMAIL']
            id_usuario = int(payload['ID_USUARIO'])

            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.EMAIL == email, 
                UsuariosModel.ESTADO != 0,
                UsuariosModel.ID != id_usuario
            ).first()

            if search is None:
                resp = response.armadoBody("Correo disponible.", 200)
            else:
                resp = response.armadoBody("El correo ya se encuentra asociado a otro usuario.", 400)

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el codigo ce ya existe, para editar
    def val_codigo_ce_unique_edit(self, data):
        response = Response()
        db = Database('dbr').session

        try:
            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.CODIGO_CE == data['CODIGO_CE'], 
                UsuariosModel.ESTADO != 0,
                UsuariosModel.ID != data['ID_USUARIO']
            ).first()

            if search is None:
                resp = True
            else:
                resp = False

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
    
    # Editar un registro ya existente en la tabla USUARIOS
    def update_user(self, payload):
        response = Response()
        db = Database('dbw').session

        try:
            update_values = {
                "CODIGO_CE": payload["CODIGO_CE"],
                "NOMBRES": payload["NOMBRES"].lower(),
                "APELLIDOS": payload["APELLIDOS"].lower(),
                "EMAIL": payload["EMAIL"],
                "ESTADO": payload["ESTADO"]
            }

            if "VERIFICADO" in payload:
                update_values["VERIFICADO"] = payload["VERIFICADO"]

            db.execute(
                update(UsuariosModel).where(
                    UsuariosModel.ID == payload["ID_USUARIO"]
                ).values(update_values)
            )
            db.commit()

            # Responde el servicio
            return response.armadoBody("Cambios guardados exitosamente.", 200)
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
    
    # Se desabilitan los perfiles asignados a un usuario
    def disable_profile_user(self, id_usuario):
        response = Response()
        db = Database('dbw').session

        try:
            db.execute(
                update(PerfilUsuariosModel).where(
                    PerfilUsuariosModel.ID_USUARIO == id_usuario
                ).values({"ESTADO": 0})
            )
            db.commit()

            # Consulta los perfiles asicaciado al usuario
            search = db.query(PerfilUsuariosModel).filter(
                PerfilUsuariosModel.ID_USUARIO == id_usuario
            ).all()

            # Responde el servicio
            return response.armadoBody("OK.", 200, json.loads(str(search)))
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Se Habilitan los perfiles asignados a un usuario
    def enable_profile_user(self, id_perfil_usu):
        response = Response()
        db = Database('dbw').session
        
        try:
            db.execute(
                update(PerfilUsuariosModel).where(
                    PerfilUsuariosModel.ID == id_perfil_usu
                ).values({"ESTADO": 1})
            )
            db.commit()

            # Responde el servicio
            return response.armadoBody("OK.", 200)
        
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Editar un registro ya existente en la tabla USUARIOS
    def change_state_user(self, payload):
        response = Response()
        db = Database('dbw').session

        try:
            update_values = {
                "ESTADO": payload["ESTADO"]
            }

            db.execute(
                update(UsuariosModel).where(
                    UsuariosModel.ID == payload["ID_USUARIO"]
                ).values(update_values)
            )

            db.commit()

            # Responde el servicio
            return response.armadoBody("Cambios guardados exitosamente.", 200)
        
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Funcion encargada de eliminar un usuario
    def delete_user(self, id_user):
        response = Response()
        db = Database("dbw").session

        try:
            #Se actualiza el estado del usuario a eliminado
            db.query(UsuariosModel
            ).filter(
                UsuariosModel.ID == id_user
                ).update(
                    {'ESTADO': 0})
            #Se actualiza el estado en la tabla perfil_usuarios
            db.query(PerfilUsuariosModel
            ).filter(
                PerfilUsuariosModel.ID_USUARIO == id_user
                ).update(
                    {'ESTADO': 0})   

            db.commit()
            
            return response.armadoBody("Registro eliminado exitosamente.", 200)
                
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
            

    #Funcion encargada de obtener Id de la actividad a realizar
    def get_IdActividad(self, codigoActividad):
        db = Database('dbr').session
        
        try:
            # Buscamos en la tabla Tipo_Activida el registro con el codigo de la actividad
            row = db.query(TipoActividadModel
            ).filter(
                TipoActividadModel.CODIGO == codigoActividad
                ).first()
            
            # Validamos la existencia del codigo, y hacemos un return De la data
            if(row != None):
                return row.ID
            else:
                return False
            
        except Exception as error:
            return { 'error': 1, 'data': str(error) }
        
        finally:
            db.invalidate()
            db.close()

    #Funcion encargada de guardar en la tabla Log la eliminacion del usuario
    def save_log(self, user_data, data, activity_type):
        response = Response()
        db = Database('dbr').session
        dbw = Database('dbw').session   
        try:
            #se obtiene el id de la actividad
            id_activity_type = self.get_IdActividad(activity_type)
            
            if id_activity_type:
                rows = {'ID_TIPO_ACTIVIDAD': id_activity_type,
                        'ENTIDAD': data['ID_USUARIO'],
                        'INF_ANTERIOR': json.dumps(user_data['INF_ANTERIOR']),
                        'INF_ACTUAL': json.dumps(user_data['INF_ACTUAL']),
                        'COMENTARIO': data.get('COMENTARIO',""),
                        'USUARIO': data['USUARIO']}
                
                # Se guarda el Log de actividades los datos del proceso
                logActividad =LogActividadesModel(rows)
                
                #Se ejecuta el query y se cierra la conexión
                dbw.add(logActividad) 
                if dbw.commit() == None:
                    resp = response.armadoBody("OK", 201)
                else:
                    resp = response.armadoBody("Error al guardar el log", 400)

                return resp

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
            dbw.invalidate()
            dbw.close()

    # Funcion para consultar el estado de verificado por usuario
    def val_verified(self, id_user):
        response = Response()
        db = Database('dbr').session

        try:

            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.ID == id_user,
                UsuariosModel.ESTADO != 0,
                UsuariosModel.VERIFICADO == 1
            ).first()

            # Se valida con True o False, si está veridicado el usuario
            resp = not(search is None)

            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
            
    def consult_permission(self, data):
        response = Response()
        db = Database('dbr').session

        try:
            # Se arma la consulta con teniendo en cuenta usuario y modulo, para obtener los permisos relacionados
            permisosPerfil = db.query(func.distinct(PermisosModel.ID).label('ID'), PermisosModel, TipoPermisoModel).join(
                    TipoPermisoModel, TipoPermisoModel.ID == PermisosModel.ID_TIPO_PERMISO
                ).join(
                    ModulosModel, ModulosModel.ID == PermisosModel.ID_MODULO
                ).join(
                    PerfilPermisosModel, PerfilPermisosModel.ID_PERMISO == PermisosModel.ID
                ).join(
                    PerfilesModel, PerfilesModel.ID == PerfilPermisosModel.ID_PERFIL
                ).join(
                    PerfilUsuariosModel, PerfilUsuariosModel.ID_PERFIL == PerfilesModel.ID
                ).join(
                    UsuariosModel, UsuariosModel.ID == PerfilUsuariosModel.ID_USUARIO
                ).filter(
                    PermisosModel.ACTIVO == 1,
                    PerfilPermisosModel.ESTADO == 1,
                    PerfilesModel.ESTADO == 1,
                    PerfilUsuariosModel.ESTADO == 1,
                    UsuariosModel.ID == data['ID_USUARIO'],
                    ModulosModel.ID == data['ID_MODULO']
                ).order_by(
                    PermisosModel.ID
                ).all()

            # Se valida la informacion del perfil de que exista
            if (len(permisosPerfil)):
                rows = []
                # recorre los resultados obtenidos para crear lista
                for permiso in permisosPerfil:
                    rows.append({
                    'ID': permiso.PermisosModel.ID,
                    'DESCRIPCION': permiso.PermisosModel.DESCRIPCION,
                    'TIPO': permiso.TipoPermisoModel.NOMBRE})
                    
                return response.armadoBody("Servicio exitoso.", 200, rows)
            else:
                return response.armadoBody("No se encontraron datos.", 400)
                
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
