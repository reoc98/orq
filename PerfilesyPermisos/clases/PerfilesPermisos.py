from clases.PermissionsDatabase import PermissionsDatabase
from clases.ProfilePermissionsDatabase import ProfilePermissionsDatabase
from utils.Response import Response
import json


class PerfilesPermisos():
    
    @classmethod
    def crearPerfil(cls, datos):

        try:
            # Validamos si el usuario tiene los permisos para relizar esta operación
            resp_permission = cls.validate_permission(user = datos['USUARIO'], type = 'CREAR')
            
            if resp_permission == True:
                cls.format_data(datos)

                # Se consulta en la tabla un perfil con el nombre ingresado
                consultaPerfil = ProfilePermissionsDatabase.get_by_name(datos['NOMBRE'])
                
                if len(datos['PERMISOS']):

                    if consultaPerfil is None:
                        valid_permissions = ProfilePermissionsDatabase.validate_permissions(datos['PERMISOS'])

                        if len(datos['PERMISOS']) == valid_permissions.number_permissions:
                            # Se crea el perfil con su información, retornando como fue guardada (id). 
                            profile = ProfilePermissionsDatabase.createProfile(datos)

                            # Obtenemos los permisos de Listar/Visualizar de los modulos que son cabecera
                            ProfilePermissionsDatabase.get_cab_permissions(datos['PERMISOS'])
                            
                            # Asociamos los permisos al perfil antes creado por medio el id
                            ProfilePermissionsDatabase.add_permissions_profile(datos['PERMISOS'], profile.id, datos['USUARIO'])

                            # Guardamos en el log de actividades
                            cls.save_log_activity(id_profile=profile.id, type="PER_CREA", user=datos['USUARIO'])

                            return Response.success_create(message="Registro creado exitosamente.")
                            
                        else:
                            return Response.bad_request(message="Ha ingresado algún permiso inválido.")

                    else:
                        return Response.bad_request(message="Ya existe un perfil con ese nombre.", data={'EXISTE_PERFIL': True})
                
                else:
                    return Response.bad_request(message="Debes seleccionar por lo menos 1 permiso.")

            elif resp_permission == False:
                return Response.bad_request("No cuenta con los permisos necesarios para realizar esta operación.")

        except Exception as error:
            return Response.internal_server_error(str(error))
        
    @classmethod
    def eliminarPerfil(cls, data):

        try:
            # Validamos si el usuario tiene los permisos para relizar esta operación
            resp_permission = cls.validate_permission(user = data['USUARIO'], type = 'ELIMINAR')
            
            if resp_permission == True:
                # Se consulta si el perfil ha sido eliminado o no existe
                profile = ProfilePermissionsDatabase.get_profile(data['ID_PERFIL'])
                
                if profile != None and profile.estado != 0:
                    # Guardamos en el log de actividades
                    cls.save_log_activity(id_profile=profile.id, type="PER_ELIM", user=data['USUARIO'], comment=data['COMENTARIO'])

                    # Eliminamos los permisos relacionados al perfil
                    ProfilePermissionsDatabase.delete_permissions(data['ID_PERFIL'])

                    # Eliminados el perfil
                    ProfilePermissionsDatabase.delete_profile(data['ID_PERFIL'])

                    return Response.success(message="Registro eliminado exitosamente.")
                
                elif profile != None and profile.estado == 0:
                    return Response.bad_request("Este perfil ya ha sido eliminado.")
                
                else: 
                    return Response.bad_request("Este perfil no existe.")

            elif resp_permission == False:
                return Response.bad_request(message="No cuenta con los permisos necesarios para realizar esta operación.", data={'PERMISOS': False})

        except Exception as error:
            return Response.internal_server_error(str(error))
        
    @classmethod
    def editarPerfil(cls, data):

        try:
            # Validamos si el usuario tiene los permisos para relizar esta operación
            resp_permission = cls.validate_permission(user = data['USUARIO'], type = 'EDITAR')
            
            if resp_permission == True:
                # Se consulta si el perfil ha sido eliminado o existe
                profile = ProfilePermissionsDatabase.get_profile(data['ID_PERFIL'])
                
                if profile != None and profile.estado != 0:
                    cls.format_data(data)

                    if len(data['PERMISOS']):
                        # Validamos todos los permisos ingresados
                        valid_permissions = ProfilePermissionsDatabase.validate_permissions(data['PERMISOS'])

                        if len(data['PERMISOS']) == valid_permissions.number_permissions:
                            # Se consulta en la tabla un perfil con el nombre ingresado
                            consultaPerfil = ProfilePermissionsDatabase.get_by_name(name=data['NOMBRE'], act=2, id_profile=data['ID_PERFIL'])

                            if consultaPerfil is None:
                                # Obtenemos la información antes de la edición
                                inf_anterior = cls.get_profile_log(data['ID_PERFIL'])

                                ProfilePermissionsDatabase.update_profile_permissions(data)

                                # Guardamos en el log de actividades
                                cls.save_log_activity(id_profile=profile.id, type="PER_EDIT", user=data['USUARIO'], inf_before=inf_anterior)

                                return Response.success(message="Cambios guardados exitosamente.")
                            
                            else:
                                return Response.bad_request(message="Ya existe un perfil con ese nombre.", data={'EXISTE_PERFIL': True})

                        else:
                            return Response.bad_request(message="Ha ingresado algún permiso inválido.")
                        
                    else:
                        return Response.bad_request(message="Debes seleccionar por lo menos 1 permiso.")

                elif profile != None and profile.estado == 0:
                    return Response.bad_request("Este perfil ya ha sido eliminado.")
                
                else: 
                    return Response.bad_request("Este perfil no existe.")

            elif resp_permission == False:
                return Response.bad_request("No cuenta con los permisos necesarios para realizar esta operación.")

        except Exception as error:
            return Response.internal_server_error(str(error))
    
    @classmethod
    def getPerfilPermisos(cls, data):     
        
        try:
            profile = ProfilePermissionsDatabase.get_profile(data['ID_PERFIL'])
                
            if profile != None and profile.estado == 1:
                permissions = ProfilePermissionsDatabase.get_profile_permissions(data['ID_PERFIL'])

                profile_permissions = {
                    "PERFIL": json.loads(str(profile)),
                    "PERMISOS": permissions
                }

                return Response.success(data=profile_permissions)

            else:
                return Response.bad_request("Este perfil no existe.")

        except Exception as error:
            return Response.internal_server_error(str(error))

    @classmethod
    def validatePermissions(cls, datos):
        response = Response()
        try:
            permission = ProfilePermissionsDatabase.consult_permissions(datos)

            # Se valida la informacion del perfil de que exista
            if (len(permission)):
                rows = []
                # recorre los resultados obtenidos para crear lista
                for permiso in permission:
                    rows.append({
                    'ID': permiso.PermisosModel.id,
                    'DESCRIPCION': permiso.PermisosModel.descripcion,
                    'TIPO': permiso.TipoPermisoModel.nombre})
                    
                return Response.success(data=rows)
            else:
                return Response.bad_request(message="No se encontraron datos.")

        except Exception as error:
            return Response.internal_server_error(str(error))

    # Funcion para validar y ajustar el fotrmato del texto
    @classmethod
    def borrarEspacionAdicionales(self, word: str):
        try:
            # Se convierte la palabra a minuscula y se eliminas los espacio externos
            palabra = word.lower().strip()

            # Se eliminan los espacios repetidos entre palabras
            palabra = " ".join(palabra.split())
            
            return palabra
        
        except Exception as error:
            raise ValueError(str(error))
       
    @classmethod
    def format_data(cls, data: list, type: int = 1):

        if type == 1:
            # Recibimos los parametros de la peticion
            data['NOMBRE'] = cls.borrarEspacionAdicionales(data['NOMBRE'])
            data['DESCRIPCION'] = data['DESCRIPCION'].lower()


    # Funcion para valdiar el permiso que tiene un usuario
    @classmethod
    def validate_permission(cls, user: int, type: str):
        try:
            data = {
                'USUARIO': user,
                'ID_MODULO': 4,
                'PERMISO': type
            }

            resp_db = PermissionsDatabase.consult_permission(data)
            
            return not(resp_db is None)
        
        except Exception as error:
            raise ValueError(str(error))
        
    @classmethod
    def save_log_activity(cls, id_profile: int, type: str, inf_before = '', comment: str = '', user: int = ''):
        try:
            activity_type = ProfilePermissionsDatabase.get_activity(type)
            
            if not(activity_type is None):
                inf_actual = cls.get_profile_log(id_profile)
                
                row = {
                        'id_tipo_actividad': activity_type.id,
                        'entidad': id_profile,
                        'inf_anterior': json.dumps(inf_before) if inf_before != '' else '',
                        'inf_actual': json.dumps(inf_actual),
                        'comentario': comment,
                        'usuario': user
                    }

            resp = ProfilePermissionsDatabase.save_log(row)

            return (resp == None)
            
        except Exception as error:
            raise ValueError(str(error))
        
    
    @classmethod
    def get_profile_log(cls, id_profile: int):
        try:
            resp = ProfilePermissionsDatabase.get_profile_permission(id_profile)

            listaPermisos = []
        
            # Se asocian los permisos con los modulos y se organiza en una estructura 
            for modulo in resp['modules']:
                permisoModulo = []
                
                for i in resp['permissions']:
                    if modulo.id == i.id_modulo:
                        permisoAux = {
                            "ID_PERMISO": i.id,
                            "DESCRIPCION": i.descripcion
                        }
                        permisoModulo.append(permisoAux)

                if len(permisoModulo) > 0:
                    moduloAux = {
                        'ID_MODULO': modulo.id,
                        'DESCRIPCION_MODULO': modulo.descripcion,
                        'INFO_PERMISOS': permisoModulo
                    }

                    listaPermisos.append(moduloAux)

            permisos = {
                "PERFIL": json.loads(str(resp['profile'])),
                "PERMISOS": listaPermisos
            }

            # Se envia la inforacion del perfil con los permisos asociados categorizado por modulos
            return permisos
        
        except Exception as error:
            raise ValueError(str(error))
    