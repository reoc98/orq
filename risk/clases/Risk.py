
from models.RequestsOrquestadorModel import RequestsOrquestadorModel
from models.RiskConsulta import RiskConsulta, datetime
from models.TipoDocumento import TipoDocumento
from clases.Database import Database
from utils.Response import Response
from utils.Aws import Aws, os
import json

class Risk():
    def __init__(self, payload = {}):
        self.payload = payload    

    # Obtener request de orquestador
    def obtenerRequestOrq(self, id):
        db = Database('dbr')
        try:
            isset = db.session.query(RequestsOrquestadorModel).filter_by(id = id).first()
            # se valida si hay registro
            if(isset == None):
                return None
        
            return isset
        finally:
            db.session.invalidate()
            db.session.close()

    # Se prepara la tabla y la ejecucion de consulta a risk
    def prepararRisk(self, id_request, data):

        db = Database('dbw')
        try:
            for info_data in data:
                ##Prepara los datos para insertarlos
                row = RiskConsulta(id_request, info_data)
                ##Bincula los datos
                db.session.add(row)
                ##Envia los datos a la DB
                db.session.commit()
                info = { "id": row.id }
                # llamamos la lambda asyncrona
                Aws.lambdaInvoke(
                        'allianz-orq-risk'
                        + '-'+str(os.getenv('STAGE'))
                        + '-procesoRisk',
                        info)
        except Exception as error:
            return None
        finally:
            db.session.invalidate()
            db.session.close()
    
    # Obtenemos los datos de risk consulta para enviarlo a risk
    def ObtenerRiskConsulta(self, id):
        db = Database('dbr')
        try:
            isset = db.session.query(RiskConsulta).filter_by(id = id).first()
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        finally:
            db.session.invalidate()
            db.session.close()

    # guardamos los logs y los datos de respuesta de risk
    def guardarLog(self, id, datos_recibidos, estado = 1, datos_enviados = None):

        db = Database('dbw')
        try:
            upd = {
                'data_envio': datos_enviados,
                'data_response': json.dumps(datos_recibidos),
                'estado': estado,
                'fecha_upd': datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            }
            ##Prepara la consulta con los datos que se van actualizar filtrando por id del registro
            query = db.session.query(RiskConsulta).filter(RiskConsulta.id == id)
            ##Bincula los nuevos datos que se van actualizar
            query.update(upd)
            db.session.commit()
        finally:
            db.session.invalidate()
            db.session.close()

    # Obtener request de orquestador de los que aun faltan por risk
    def obtenerPendienteRisk(self):
        db = Database('dbr')
        try:
            isset = db.session.query(RequestsOrquestadorModel).filter_by(risk = 0).all()
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        finally:
            db.session.invalidate()
            db.session.close()

    # Obtener consultas por id request
    def obtenerPorIdRequest(self, id, estado = None):
        db = Database('dbr')
        try:
            if estado == None:
                isset = db.session.query(RiskConsulta).filter(RiskConsulta.id_request == id).all()
            else:
                isset = db.session.query(RiskConsulta).filter(
                    RiskConsulta.id_request == id).filter(
                    RiskConsulta.estado == 1).all()
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        finally:
            db.session.invalidate()
            db.session.close()

    # guardamos los logs y los datos de respuesta de risk
    def actualizarEstadoRequest(self, id, estado = 1):

        db = Database('dbw')
        try:
            upd = {
                'risk': estado
            }
            ##Prepara la consulta con los datos que se van actualizar filtrando por id del registro
            query = db.session.query(RequestsOrquestadorModel).filter(RequestsOrquestadorModel.id == id)
            ##Bincula los nuevos datos que se van actualizar
            query.update(upd)
            db.session.commit()
        finally:
            db.session.invalidate()
            db.session.close()

    # Se conuslta el tipo de documento mediante el prefijo
    def buscar_tipo_documento(self, prefijo):
        db = Database('dbr').session
        try:
            
            consult = db.query(TipoDocumento.codigo).filter(
                TipoDocumento.estado == 1,
                TipoDocumento.prefijo_request == prefijo
            )
            row = consult.first()
            
            if row is not None:
                return row.codigo
            else:
                return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()
        