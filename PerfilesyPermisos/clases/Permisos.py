import json
from models.PermisosModel import PermisosModel
from models.ModulosModel import ModulosModel
from clases.Database import Database
from utils.Response import Response
class Permisos():
   
    def get_all(self):
        response = Response()
        db = Database('dbr').session

        try:
            rows = db.query(PermisosModel).filter(
                PermisosModel.ACTIVO == 1
            ).all()
            if (len(rows)):
                return response.armadoBody("Servicio exitoso.", 200, json.loads(str(rows)))
            else:
                return response.armadoBody("No se encontraron datos.", 400)
            
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    def ModulosPermisos(self):
        response = Response()
        db = Database('dbr').session
        
        try:
            rows = db.query(ModulosModel.ID, ModulosModel.DESCRIPCION, PermisosModel.ID, PermisosModel.DESCRIPCION).join(
                ModulosModel, ModulosModel.ID == PermisosModel.ID_MODULO).filter(
                    ModulosModel.ACTIVO == 1
                ).filter(
                    PermisosModel.ACTIVO == 1
                ).filter(
                    ModulosModel.VISIBLE == 1
                ).order_by(ModulosModel.ID, PermisosModel.ID).all()
          
            if(len(rows)):
                data = [];

                modulo = {
                            'ID_MODULO': rows[0][ModulosModel.ID],
                            'DESCRIPCION_MODULO': rows[0][ModulosModel.DESCRIPCION],
                            'PERMISOS': []
                        }

                for i in rows:
                    aux = {
                        'ID_PERMISO': i[PermisosModel.ID],
                        'DESCRIPCION': i[PermisosModel.DESCRIPCION]
                    }

                    if(modulo['ID_MODULO'] == i[ModulosModel.ID]):
                        modulo['PERMISOS'].append(aux)
                    else:
                        data.append(modulo)
                        modulo = {
                            'ID_MODULO': i[ModulosModel.ID],
                            'DESCRIPCION_MODULO': i[ModulosModel.DESCRIPCION],
                            'PERMISOS': []
                            }
                        modulo['PERMISOS'].append(aux)
                data.append(modulo)

                return response.armadoBody("Servicio exitoso.", 200, data)
            else:
                return response.armadoBody("No se encontraron datos.", 400)

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()