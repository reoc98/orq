from models.PermisosModel import PermisosModel
from models.ModulosModel import ModulosModel
from models.PerfilesModel import PerfilesModel
from models.PerfilPermisosModel import PerfilPermisosModel
from models.TipoPermisoModel import TipoPermisoModel
from models.TipoActividadModel import TipoActividadModel
from models.LogActividadesModel import LogActividadesModel
from models.PerfilUsuariosModel import PerfilUsuariosModel
from models.UsuariosModel import UsuariosModel
from clases.Database import Database
from sqlalchemy.sql import func, and_

class ProfilePermissionsDatabase():

    @classmethod
    def createProfile(cls, data: list):
        db = Database('dbw').session

        try:
            # Se intancia un modelo con los datos ingresado para crear el perfil
            perfil = [PerfilesModel(
                                nombre = data['NOMBRE'], 
                                descripcion = data['DESCRIPCION'],
                                usuario = data['USUARIO']
                                )]
            
            # se crea el perfil y se utiliza el "return_defaults", para retornar el id con el cual se guardó.
            db.bulk_save_objects(perfil, return_defaults = True) 
            db.commit()
  
            return perfil[0]

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def add_permissions_profile(cls, data: list, id_profile: int, user: int):
        db = Database('dbw').session

        try:
            # Ejecutamos un cliclo para guardar los datos de todos lo permisos que estarán asociado a ese perfil
            permissions = [ { 'id_permiso': i, 'id_perfil': id_profile, 'usuario': user } for i in data ]

            #Ejecutamo el query masivo con todos los permisos para el perfil
            db.bulk_insert_mappings(PerfilPermisosModel, permissions)
            db.commit()
  
            return True

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    # Obtener el perfil, permisos y modulos para guardar en el LOG
    @classmethod
    def get_profile_permission(cls, id_profile: int):
        db = Database('dbr').session

        try:
            # Consultamos el perfil.
            consult = db.query(PerfilesModel).filter(
                PerfilesModel.id == id_profile
            )
            profile = consult.first()

            # Se consultas los permisos asociados al perfil
            consult = db.query(PermisosModel).join(
                                PerfilPermisosModel, PermisosModel.id == PerfilPermisosModel.id_permiso
                            ).filter(
                                PerfilPermisosModel.id_perfil == id_profile, 
                                PerfilPermisosModel.estado == 1
                            )
            permissions = consult.all()
            
            # Se consulta el listado de los modulos
            consult = db.query(ModulosModel).filter(
                        ModulosModel.activo == 1
                    ).order_by(ModulosModel.id)
            modules = consult.all()
            
            return {
                'profile': profile,
                'permissions': permissions,
                'modules': modules
            }

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    # Revisar si existe un perfil con el mismo nombre
    @classmethod
    def get_by_name(cls, name: str, act: int = 1, id_profile: int = 0):
        db = Database('dbr').session

        try:
            # Consultamos un perfil buscando por el nombre
            consult =  db.query(PerfilesModel
                    ).filter(
                        PerfilesModel.nombre == name,
                        PerfilesModel.estado == 1
                    )

            if (act == 2 and id_profile != 0): consult = consult.filter(PerfilesModel.id != id_profile)

            row = consult.first()

            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    # Revisar si los permisos ingresados estan habilitados o existen
    @classmethod
    def validate_permissions(cls, permissions: list):
        db = Database('dbr').session

        try:
            # Consultamos un perfil buscando por el nombre
            consult =  db.query(
                        func.count(PermisosModel.id).label('number_permissions'),
                    ).filter(
                        PermisosModel.id.in_(permissions)
                    )

            row = consult.first()

            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    # 
    @classmethod
    def get_cab_permissions(cls, permissions: list):
        db = Database('dbr').session

        try:
            # Consultamos todos los modulos asociados a los permisos seleccionados.
            consult =  db.query(PermisosModel.id_modulo).distinct().filter(PermisosModel.id.in_(permissions))
            modules = consult.all()

            modules_id = [ { i.id_modulo } for i in modules ]

            # Buscamos los modulos que tienen cabecera
            consult = db.query(ModulosModel.cabecera,ModulosModel.id).distinct().filter(ModulosModel.id.in_(modules_id)).filter(ModulosModel.cabecera != 0)
            cabeceras = consult.all()

            # ** MEJORAR **
            # Se obtienen los permisos de vizualizacion de cabecera.
            cabeceraDatos = []
            for pos in cabeceras:
                md = pos.id
                cab = pos.cabecera
                # Prepara los datos para insertarlos
                id_listar = db.query(
                    ModulosModel.descripcion,
                    PermisosModel.id
                ).join(
                    PermisosModel, 
                    and_(
                        PermisosModel.id_modulo == ModulosModel.id,
                        PermisosModel.activo == 1)
                ).join(
                    TipoPermisoModel, 
                    TipoPermisoModel.id == PermisosModel.id_tipo_permiso
                ).filter(
                    TipoPermisoModel.nombre == 'LISTAR',
                    ModulosModel.id == md,
                    PermisosModel.id.in_(permissions)).all()
                if len(id_listar) > 0:
                    cabeceraDatos.append(cab)

            if len(cabeceraDatos) > 0:
                # Buscamos el permiso de esa cabecera
                cabeceraPermisos = db.query(PermisosModel.id).filter(
                    PermisosModel.id_modulo.in_(cabeceraDatos)
                ).filter(PermisosModel.activo == 1).filter(PermisosModel.id_tipo_permiso == 2).all()

                # Se le agrega el permiso del modulo principal al array de permisos del usuario
                for row in cabeceraPermisos:
                    permissions.append(row.id)

            return permissions
            # ** MEJORAR **
            
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def get_activity(cls, type: str):
        db = Database('dbr').session
        try:
            # Buscamos en la tabla Tipo_Activida el registro con el codigo de la actividad
            consult = db.query(TipoActividadModel
                           ).filter(
                                TipoActividadModel.codigo == type
                            )
            row = consult.first()

            return row
            
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    #Funcion encargada de guardar en la tabla Log la eliminacion del usuario
    @classmethod
    def save_log(self, data: list):
        db = Database('dbw').session     
        try:
            # Se arma la estructura y se guarda en el Log de actividades
            logActividad = LogActividadesModel(data)
            db.add(logActividad) 

            return db.commit()

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    # Consulta la informacion de los perfiles.
    @classmethod
    def get_profile(cls, id_profile: int):
        db = Database('dbr').session

        try:
            # Consultamos el perfil.
            consult = db.query(PerfilesModel).filter(
                PerfilesModel.id == id_profile
            )
            profile = consult.first()

            return profile

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def delete_permissions(cls, id_profile: int):
        dbw = Database('dbw').session

        try:
            # Prepara la consulta con los datos que se van actualizar filtrando por id del perfil el ESTADO en 1 (1 = Habilitado, 0 = Deshabilitado)
            PerfilesUsuarios = dbw.query(PerfilUsuariosModel).filter(
                                            PerfilUsuariosModel.id_perfil == id_profile, 
                                            PerfilUsuariosModel.estado == 1
                                        )
            # Se realizar el ajuste del estado cambiando a 0 de los usuarios para deshabilitar dicho perfil (1 = Habilitado, 0 = Deshabilitado)
            PerfilesUsuarios.update({'estado': 0})

            return dbw.commit()

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            dbw.invalidate()
            dbw.close()

    @classmethod
    def delete_profile(cls, id_profile: int):
        dbw = Database('dbw').session


        try:
            # Se realiza el cambio de estado del perfil a 0 (1 = Existe, 0 = Eliminado)
            dbw.query(PerfilesModel).filter(
                    PerfilesModel.id == id_profile
                ).update({'estado': 0})

            return dbw.commit()

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            dbw.invalidate()
            dbw.close()


    @classmethod
    def update_profile_permissions(cls, data):
        db = Database('dbr').session
        dbw = Database('dbw').session

        try:
            # ** MEJORAR **
            # Se realiza el cambio sobre los campos del permiso.
            dbw.query(PerfilesModel).filter(PerfilesModel.id == data['ID_PERFIL']).update({'nombre': data['NOMBRE'], 'descripcion': data['DESCRIPCION']})

            # Obtenemos todos los permisos asociados al perfil antes de la edicion
            permisosPerfil = db.query(PerfilPermisosModel).filter(PerfilPermisosModel.id_perfil == data['ID_PERFIL']).all()

            # Prepara la consulta con los datos que se van actualizar filtrando por id del perfil
            perfilPermisos = db.query(PerfilPermisosModel).filter(
                    PerfilPermisosModel.id_perfil == data['ID_PERFIL']
                ).all()
                                
            # Se le agrega permiso al modulo principal en caso de que un submodulo tenga permiso
            moduloPermiso = db.query(PermisosModel.id_modulo).distinct().filter(PermisosModel.id.in_(data['PERMISOS'])).all()
            moduloDatos = [ { i.id_modulo } for i in moduloPermiso ]

            # buscamos si tienen modulo con cabecera
            cabecera = db.query(ModulosModel.cabecera,ModulosModel.id).distinct().filter(ModulosModel.id.in_(moduloDatos)).filter(ModulosModel.cabecera != 0).all()
            cabeceraDatos = []
            for pos in cabecera:
                md = pos.id
                cab = pos.cabecera
                            # Prepara los datos para insertarlos
                id_listar = db.query(
                    ModulosModel.descripcion,
                    PermisosModel.id
                ).join(
                    PermisosModel, 
                    and_(
                        PermisosModel.id_modulo == ModulosModel.id,
                        PermisosModel.activo == 1)
                ).join(
                    TipoPermisoModel, 
                    TipoPermisoModel.id == PermisosModel.id_tipo_permiso
                ).filter(
                    TipoPermisoModel.nombre == 'LISTAR',
                    ModulosModel.id == md,
                    PermisosModel.id.in_(data['PERMISOS'])).all()
                if len(id_listar) > 0:
                    cabeceraDatos.append(cab)
            # Validamos si se le va a dar permiso de acceder a cabeceras con submodulos y permisos de listar
            if len(cabeceraDatos) > 0:
                # Buscamos el permiso de esa cabecera
                cabeceraPermisos = db.query(PermisosModel.id).filter(
                    PermisosModel.id_modulo.in_(cabeceraDatos)
                ).filter(PermisosModel.activo == 1).filter(PermisosModel.id_tipo_permiso == 2).all()

                # Se le agrega el permiso del modulo principal al array de permisos del usuario
                for row in cabeceraPermisos:
                    data['PERMISOS'].append(row.id)
            else:
                # Si no existe ninguna cabecera las quitamos de los permisos
                cabecera = db.query(ModulosModel.cabecera).distinct().filter(ModulosModel.cabecera != 0).all()
                cabeceraDatos = [ { i.cabecera } for i in cabecera ]

                # Buscamos el permiso de esa cabecera
                cabeceraPermisos = db.query(PermisosModel.id).filter(
                    PermisosModel.id_modulo.in_(cabeceraDatos)
                ).filter(PermisosModel.activo == 1).filter(PermisosModel.id_tipo_permiso == 2).all()
                
                for row in cabeceraPermisos:
                    if row.id in data['PERMISOS']:
                        data['PERMISOS'].remove(row.id)


            # Se realiza el cambio de a los permisos sobre ese perfil.
            dbw.query(PerfilPermisosModel).filter(PerfilPermisosModel.id_perfil == data['ID_PERFIL']).update({'estado': 0})

            perfilPERMISOS = []

            # Ejecutamos un cliclo para recorrer los perfiles que han sido asignados
            for permiso in data['PERMISOS']:
                sw = True

                for perfilPer in perfilPermisos:
                    if permiso == perfilPer.id_permiso:
                        sw = False
                
                if sw == True:
                    # Ejecutamos un cliclo para guardar los datos de todos lo permisos que estarán asociado a ese perfil
                    perfilPERMISOS.append({ 'id_permiso': permiso, 'id_perfil': data['ID_PERFIL'] })
                else:
                    dbw.query(PerfilPermisosModel).filter(PerfilPermisosModel.id_permiso == permiso).update({'estado': 1})
            
            #Ejecutamo el query masivo con todos los permisos para el perfil
            dbw.bulk_insert_mappings(PerfilPermisosModel, perfilPERMISOS)
            dbw.commit()
            # ** MEJORAR **

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()
            dbw.invalidate()
            dbw.close()


    @classmethod
    def get_profile_permissions(cls, id_profile: int):
        db = Database('dbr').session

        try:
            # ** MEJORAR **
            # Se consultas los permisos asociados al perfil
            permisosPerfil = db.query(PerfilPermisosModel, PermisosModel).join(
                                PermisosModel, PermisosModel.id == PerfilPermisosModel.id_permiso
                            ).filter(
                                PerfilPermisosModel.id_perfil == id_profile, PerfilPermisosModel.estado == 1
                            ).all()

            # Se consulta el listado de los modulos cabecera
            modulos_aux = db.query(func.distinct(ModulosModel.cabecera).label('id')).filter(
                        ModulosModel.cabecera != 0
                    ).all()
            
            modulos_cab = []
            for mod_cab in modulos_aux:
                modulos_cab.append(mod_cab.id)

            # Se consulta el listado de los modulos son los modulos que son cabecera
            modulos = db.query(ModulosModel).filter(
                        ModulosModel.activo == 1,
                        ModulosModel.id.not_in(modulos_cab)
                    ).order_by(ModulosModel.id).all()

            listaPermisos = []
    
            # Se asocian los permisos con los modulos y se organiza en una estructura 
            for modulo in modulos:
                permisoModulo = []
                
                for i in permisosPerfil:
                    if modulo.id == i.PermisosModel.id_modulo:
                        permisoAux = {
                            "ID_PERMISO": i.PermisosModel.id,
                            "DESCRIPCION": i.PermisosModel.descripcion
                        }
                        permisoModulo.append(permisoAux)

                moduloAux = {
                    'ID_MODULO': modulo.id,
                    'DESCRIPCION_MODULO': modulo.descripcion,
                    'INFO_PERMISOS': permisoModulo
                }

                listaPermisos.append(moduloAux)

            return listaPermisos
            # ** MEJORAR **
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    # Funcion para consultar los permiso de un usuario
    @classmethod
    def consult_permissions(cls, data: list):
        db = Database('dbr').session

        try:
            # Se arma la consulta con teniendo en cuenta usuario y modulo, para obtener los permisos relacionados
            permisosPerfil = db.query(func.distinct(PermisosModel.id).label('id'), PermisosModel, TipoPermisoModel).join(
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
                    UsuariosModel.id == data['ID_USUARIO'],
                    ModulosModel.id == data['ID_MODULO']
                ).order_by(
                    PermisosModel.id
                ).all()

            return permisosPerfil
                
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()