from classes.Database import Database
from sqlalchemy.sql import func
from models.profile_permissions.PermisosModel import PermisosModel
from models.profile_permissions.ModulosModel import ModulosModel
from models.profile_permissions.TipoPermisoModel import TipoPermisoModel
from models.profile_permissions.PerfilPermisosModel import PerfilPermisosModel
from models.profile_permissions.PerfilesModel import PerfilesModel
from models.profile_permissions.PerfilUsuariosModel import PerfilUsuariosModel
from models.UsuariosModel import UsuariosModel

class PermissionsDatabase:
    """
    Esta clase se encargar consultar los modulos y permisos relacionados, Modulos de un usuario.
    """

    @classmethod
    def consult_permission(self, data: list):
        db = Database('dbr').session

        try:
            consult = db.query(func.distinct(PermisosModel.id).label('ID'), 
                               PermisosModel.descripcion.label('DESCRIPCION'), 
                               TipoPermisoModel.nombre.label('TIPO'),
                               UsuariosModel.email.label('CORREO')
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
