from clases.PermissionsDatabase import PermissionsDatabase
from utils.Response import Response
import json

class ModulesPermissions():
    """
    Esta clase se encargar procesar la informacion de los modulos y permisos.
    """

    # Obtener un listado de todos los modulos existentes.
    @classmethod
    def get_modules(cls):
        
        try:
            # Consultamos los modulos existentes en estado activo.
            rows = PermissionsDatabase.get_modules()

            # Validamos, sí hay elementos en el listado.
            if (len(rows)):
                return Response.success(data = json.loads(str(rows)))
            else:
                return Response.bad_request(message = "No se encontraron datos.")
              
        except Exception as error:
            return Response.internal_server_error(str(error))

    # Obtener un listado de los permisos activos clasificados por modulo.
    @classmethod
    def permissions_by_module(cls):
       
        try:
            rows = PermissionsDatabase.permissions_module()
            
            if(len(rows)):
                data = [];
                modulo = {
                            'ID_MODULO': rows[0].id_module,
                            'DESCRIPCION_MODULO': rows[0].description_module,
                            'PERMISOS': []
                        }
                
                for i in rows:
                    aux = {
                        'ID_PERMISO': i.id_permission,
                        'DESCRIPCION': i.description_permission
                    }

                    if(modulo['ID_MODULO'] == i.id_module):
                        modulo['PERMISOS'].append(aux)
                    else:
                        data.append(modulo)
                        modulo = {
                            'ID_MODULO': i.id_module,
                            'DESCRIPCION_MODULO': i.description_module,
                            'PERMISOS': []
                            }
                        modulo['PERMISOS'].append(aux)
                data.append(modulo)

                return Response.success(data = data)
            else:
                return Response.bad_request(message = "No se encontraron datos.")

        except Exception as error:
            return Response.internal_server_error(str(error))
