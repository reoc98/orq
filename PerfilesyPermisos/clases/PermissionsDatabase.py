from models.PermisosModel import PermisosModel
from models.ModulosModel import ModulosModel
from models.TipoPermisoModel import TipoPermisoModel
from models.PerfilPermisosModel import PerfilPermisosModel
from models.PerfilesModel import PerfilesModel
from models.PerfilUsuariosModel import PerfilUsuariosModel
from models.UsuariosModel import UsuariosModel
from clases.Database import Database
from sqlalchemy.sql import func

class PermissionsDatabase:
    """
    Esta clase se encargar consultar los modulos y permisos relacionados, Modulos de un usuario.
    """

    @classmethod
    def get_modules(cls):
        db = Database('dbr').session
    
        try:
            consult = db.query(ModulosModel).filter(
                ModulosModel.activo == 1
                )
            rows = consult.all()

            return rows
    
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def permissions_module(cls):
        db = Database('dbr').session
        
        try:
            consult = db.query(ModulosModel.id.label("id_module"), 
                               ModulosModel.descripcion.label("description_module"), 
                               PermisosModel.id.label("id_permission"), 
                               PermisosModel.descripcion.label("description_permission")
                ).join(
                ModulosModel, ModulosModel.id == PermisosModel.id_modulo
                ).filter(
                    ModulosModel.activo == 1,
                    PermisosModel.activo == 1,
                    ModulosModel.visible == 1
                ).order_by(ModulosModel.id, PermisosModel.id)
            rows = consult.all()
          
            return rows

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def consult_permission(self, data: list):
        db = Database('dbr').session

        try:
            consult = db.query(func.distinct(PermisosModel.id).label('ID'), 
                               PermisosModel.descripcion.label('DESCRIPCION'), 
                               TipoPermisoModel.nombre.label('TIPO')
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
                    UsuariosModel.id == data['USUARIO'],
                    ModulosModel.id == data['ID_MODULO'],
                    TipoPermisoModel.nombre == data['PERMISO']
                ).order_by(
                    PermisosModel.id
                )
            row = consult.first()

            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()