import json
from models.ModulosModel import ModulosModel
from clases.Database import Database
from utils.Response import Response
class Modulos():
    
    def get_all(self):
        response = Response()
        db = Database('dbr').session
    
        try:
            rows = db.query(ModulosModel).filter(
                ModulosModel.ACTIVO==1
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
