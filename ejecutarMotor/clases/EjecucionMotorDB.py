from models.RequestsOrquestadorModel import RequestsOrquestadorModel
from models.Arbol import Arbol
from models.EjecucionMotor import EjecucionMotor, datetime
from models.ArbolEjecucion import ArbolEjecucion
from models.RiskConsulta import RiskConsulta
from models.ServiceInif import ServiceInif
from clases.Database import Database
import json

class EjecucionMotorDB():
    def __init__(self, mode = 'dbr') -> None:
        # Inicializamos una conexion por el Objeto.
        self.db = Database(mode).session

    def cerrar_conexion(self):
        self.db.invalidate()
        self.db.close()
    
    # Obtener request de orquestador por id
    def get_request_orq(self, id_request):
        try:
            row = self.db.query(
                        RequestsOrquestadorModel
                    ).filter(
                        RequestsOrquestadorModel.id == id_request
                    ).first()
            
            return row
        
        except Exception as e:
            raise ValueError(str(e))

    # Obtener request de orquestador
    def get_ejecuciones_motor(self, id_request):
        try:
            rows = self.db.query(
                    EjecucionMotor,
                    Arbol.id,
                    Arbol.codigo,
                    ArbolEjecucion.tipo,
                    ArbolEjecucion.risk,
                    ArbolEjecucion.risk_array
                ).join(
                    Arbol, Arbol.id == EjecucionMotor.id_arbol
                ).join(
                    ArbolEjecucion, ArbolEjecucion.codigo == Arbol.codigo
                ).filter(
                    ArbolEjecucion.estado == 1,
                    EjecucionMotor.id_request == id_request,
                    EjecucionMotor.estado == 0
                )
            
            return rows
        
        except Exception as e:
            raise ValueError(str(e))

    # guardamos los logs y los datos de respuesta de risk
    def guardarLog(self, id, datos_recibidos, estado = 1, datos_enviados = None, desenlace = None):
        try:
            upd = {
                'datos_request': datos_enviados,
                'datos_response': json.dumps(datos_recibidos),
                'desenlace_contenido': json.dumps(desenlace),
                'estado': estado,
                'fecha_upd': datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            }
            ##Prepara la consulta con los datos que se van actualizar filtrando por id del registro
            query = self.db.query(EjecucionMotor).filter(EjecucionMotor.id == id)
            ##Bincula los nuevos datos que se van actualizar
            query.update(upd)
            self.db.commit()
            
        except Exception as e:
            raise ValueError(str(e))

    # obtenemos la consulta de risk en base al documento
    def obtenerConsulaRisk(self, id_request, documento):
        try: 
            isset = self.db.query(RiskConsulta).filter_by(
                numero_documento = documento).filter_by(
                id_request = id_request).filter_by(
                estado = 1).first()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))

    def upd_ejecucion_siniestro(self, id_request, estado = 1):

        try:
            # se obtienen los id actualizar
            upd = {
                'ejecucion': estado
            }
            # preparamos la consulta a actualizar
            query = self.db.query(
                        RequestsOrquestadorModel
                    ).filter(
                            RequestsOrquestadorModel.id == id_request
                    )
            
            # actualizamos los campos
            query.update(upd)
            self.db.commit()
            
        except Exception as e:
            raise ValueError(str(e))
    
    @staticmethod
    def get_service_inif(id_request, doc_number):
        session = Database('dbr').session
        try:
            service = session.query(
                ServiceInif.id,
                ServiceInif.response
            ).filter_by(
                id_request_orq=id_request,
                numero_documento=doc_number
            ).first()
            return service
        finally:
            session.invalidate()
            session.close()