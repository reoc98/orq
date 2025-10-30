
from models.RequestsOrquestadorModel import RequestsOrquestadorModel
from models.Arbol import Arbol
from models.ResponseOrquestador import ResponseOrquestador
from models.RequestsEnviados import RequestsEnviados
from models.EjecucionMotor import EjecucionMotor, datetime
from models.ArbolEjecucion import ArbolEjecucion
from models.RiskConsulta import RiskConsulta
from models.ServiceInif import ServiceInif
from clases.Database import Database
from utils.Aws import Aws, os
import json

class Ejecucion():
    def __init__(self, payload = {}):
        self.payload = payload    

    # Obtener request de orquestador
    def obtenerRequestOrq(self, ejecucion):
        db = Database('dbr').session
        try:
            isset = db.query(RequestsOrquestadorModel
                    ).filter(
                        RequestsOrquestadorModel.ejecucion == ejecucion,
                        RequestsOrquestadorModel.risk == 1,
                        RequestsOrquestadorModel.estado == 1
                    ).all()

            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.invalidate()
            db.close()

    # Obtener request de orquestador por id
    def obtenerRequestOrqID(self, id):
        db = Database('dbr')
        try:
            isset = db.session.query(RequestsOrquestadorModel).filter_by(id = id).first()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # Obtener la ejecucion del motor por id
    def obtenerEjecucionMotorID(self, id):
        db = Database('dbr')
        try:
            isset = db.session.query(EjecucionMotor).filter_by(id = id).first()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # obtenemos la consulta de risk en base al documento
    def obtenerConsulaRisk(self, id_request, documento):
        db = Database('dbr')
        try:
            isset = db.session.query(RiskConsulta).filter_by(
                numero_documento = documento).filter_by(
                id_request = id_request).filter_by(
                estado = 1).first()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    def obtener_service_inif(self, id_request, tipo_figura, numero_documento):
        db = Database('dbr').session
        try:
            consulta = db.query(
                ServiceInif.response
            ).filter_by(
                id_request_orq = id_request,
                tipo_figura = tipo_figura,
                numero_documento = numero_documento
            ).order_by(
                ServiceInif.id.desc()
            ).first()

            return consulta
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.invalidate()
            db.close()

    # Obtenemos los motores activos a ejecutar
    def obtenerMotores(self):
        db = Database('dbr')
        try:
            isset = db.session.query(Arbol).filter_by(activo = 1).filter_by(padre = 1).all()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # Obtenemos el motor por id
    def obtenerMotorID(self, id):
        db = Database('dbr')
        try:
            isset = db.session.query(
                Arbol.id,
                Arbol.codigo,
                ArbolEjecucion.tipo,
                ArbolEjecucion.risk,
                ArbolEjecucion.risk_array).filter(
                Arbol.id == id).filter(
                ArbolEjecucion.estado == 1).join(Arbol.arbolEjecucion).first()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # Se prepara la tabla y la ejecucion de los arboles
    def prepararMotor(self, id_request, id_arbol, figura, codigo_arbol):

        db = Database('dbw')
        try:
            figura = json.dumps(figura)
            ##Prepara los datos para insertarlos
            row = EjecucionMotor(id_request, id_arbol, figura, codigo_arbol)
            ##Bincula los datos
            db.session.add(row)
            ##Envia los datos a la DB
            db.session.commit()
            info = {
                "id_ejecucion": row.id,
                "id_arbol": id_arbol,
                "id_request": id_request
            }

            # llamamos la lambda asyncrona
            Aws.lambdaInvoke(
                    'allianz-orq-motor'
                    + '-'+str(os.getenv('STAGE'))
                    + '-ejecucionMotor',
                    info)
            
        except Exception as error:
            return None
        finally:
            db.session.invalidate()
            db.session.close()

    # guardamos los logs y los datos de respuesta de risk
    def guardarLog(self, id, datos_recibidos, estado = 1, datos_enviados = None, desenlace = None):

        db = Database('dbw')
        try:
            upd = {
                'datos_request': datos_enviados,
                'datos_response': json.dumps(datos_recibidos),
                'desenlace_contenido': json.dumps(desenlace),
                'estado': estado,
                'fecha_upd': datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            }
            ##Prepara la consulta con los datos que se van actualizar filtrando por id del registro
            query = db.session.query(EjecucionMotor).filter(EjecucionMotor.id == id)
            ##Bincula los nuevos datos que se van actualizar
            query.update(upd)
            db.session.commit()
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # actualizamos un request especifico
    def actualizarEstadoRequest(self, id, estado = 1):
        db = Database('dbw')
        try:
        
            upd = {
                'ejecucion': estado
            }
            ##Prepara la consulta con los datos que se van actualizar filtrando por id del registro
            query = db.session.query(RequestsOrquestadorModel).filter(RequestsOrquestadorModel.id == id)
            
            ##Bincula los nuevos datos que se van actualizar
            query.update(upd)
            db.session.commit()
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # actualizamos masivamente a estado en ejecucion
    def actualizarEstadosMasivos(self, data, estado = 1):

        db = Database('dbw')
        try:
            # se obtienen los id actualizar
            listado_id = [req.id for req in data]
            upd = {
                'ejecucion': estado
            }
            # preparamos la consulta a actualizar
            query = db.session.query(RequestsOrquestadorModel).filter(RequestsOrquestadorModel.id.in_(listado_id))
            
            # actualizamos los campos
            query.update(upd)
            db.session.commit()
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # se valida si el motor esta en la tabla de ejecucion
    def validarMotores(self, codigo):

        db = Database('dbr')
        try:
            isset = db.session.query(ArbolEjecucion).filter_by(codigo = codigo).filter_by(estado = 1).first()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # obtenemos la figura correspondiente del array
    def obtenerFigura(self, request, figura, tipo):

        almacenamiento = []
        # recorremos el array
        for row in request["figuras_personas"]:

            if row["tipo_figura"] == figura:
                # validamos si es interviniente
                if tipo == 0:
                    return row
                else:
                    almacenamiento.append(row)

        return almacenamiento

    # obtenemos el vehiculo correspondiente del array
    def obtenerVehiculo(self, request, figura, tipo):

        almacenamiento = []
        # recorremos el array
        for row in request["figuras_vehiculo"]:

            if row["tipo_figura"] == figura:
                # validamos si es interviniente
                if tipo == 0:
                    return row
                else:
                    almacenamiento.append(row)

        return almacenamiento

    # obtenemos el risk correspondiente
    def obtenerRisk(self, request, risk):

        almacenamiento = []
        if "resultados" in request:
            # recorremos el array
            for row in request["resultados"]:
                if row["lista"] == risk:
                    return row

        return almacenamiento

    # Obtener consultas por id request en ejecucion motor
    def obtenerPorIdEjecucion(self, id, estado = None):
        db = Database('dbr')
        try:
            if estado == None:
                isset = db.session.query(EjecucionMotor).filter(
                    EjecucionMotor.id_request == id).filter(
                    EjecucionMotor.estado != 3).all()
            else:
                isset = db.session.query(EjecucionMotor).filter(
                    EjecucionMotor.id_request == id).filter(
                    EjecucionMotor.estado == estado).all()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # Obtenemos los dias de ocurrencia del secreto
    def diasOcurrencia(self):
        secret = Aws.getSecret(str(os.getenv('STAGE'))+"/secret-orquestador")
        return secret["dias_ocurrencia"]

    # Obtener el nombre del motor
    def obtenerNombreMotor(self, id):
        db = Database('dbr')
        try:
            isset = db.session.query(Arbol.nombre, 
                                    ArbolEjecucion.tipo, 
                                    ArbolEjecucion.vehiculo, 
                                    ArbolEjecucion.codigo, 
                                    ArbolEjecucion.variable_comentario,
                                    Arbol.activo
                                    ).filter(
                Arbol.id == id).join(Arbol.arbolEjecucion).first()
            
            # se valida si hay registro
            if(isset == None):
                return None
            
            return isset
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # guardamos la estructura
    def guardarEstructura(self, id_request, datos):
        db = Database('dbw')
        try:
            # Prepara los datos para insertarlos
            row = ResponseOrquestador(id_request, json.dumps(datos))
            # Bincula los datos
            db.session.add(row)
            # Envia los datos a la DB
            db.session.commit()

            data =  { "id": row.id, "estructura_envio": row.estructura_envio }
            return data
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.session.invalidate()
            db.session.close()

    # Obtenemos toda la informacion de los motores ejecutados
    def motores_ejecucion_request(self, id, estado = None):
        db = Database('dbr').session
        try:
            
            consult = db.query( Arbol.id.label("id_arbol"),
                                Arbol.nombre,
                                Arbol.activo, 
                                ArbolEjecucion.tipo, 
                                ArbolEjecucion.vehiculo, 
                                ArbolEjecucion.codigo, 
                                ArbolEjecucion.variable_comentario,
                                EjecucionMotor.id_arbol,
                                EjecucionMotor.datos_request,
                                EjecucionMotor.desenlace_contenido,
                                EjecucionMotor.figura
                    ).join(
                        Arbol, Arbol.id == EjecucionMotor.id_arbol
                    ).join(
                        ArbolEjecucion
                    ).filter(
                        EjecucionMotor.id_request == id,
                        EjecucionMotor.estado == estado
                    ).order_by(
                        EjecucionMotor.id.asc()
                    )
            
            rows = consult.all()
            
            return rows
        
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.invalidate()
            db.close()

    def enviar_motor(self, id_response, id_request):
        db = Database('dbw')
        try:
            
            info = {
                "id_response": id_response,
                "id_request": id_request
            }

            # llamamos la lambda asyncrona
            Aws.lambdaInvoke(
                    'allianz-orq-motor'
                    + '-'+str(os.getenv('STAGE'))
                    + '-consumo_serv_motor',
                    info)
            
        except Exception as error:
            return None
        finally:
            db.session.invalidate()
            db.session.close()

    # Buscamos la estructura de envio del request
    def buscar_datos_envio(self, id_response):
        db = Database('dbr').session
        try:
            # Prepara los datos para insertarlos
            consult = db.query(ResponseOrquestador
                        ).filter(
                            ResponseOrquestador.id == id_response
                        )
            row = consult.first()

            return row
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.invalidate()
            db.close()

        # Buscamos la estructura de envio del request
    def buscar_request_enviados(self, id_request):
        db = Database('dbr').session
        try:
            # Prepara los datos para insertarlos
            consult = db.query(RequestsEnviados
                        ).filter(
                            RequestsEnviados.id_request == id_request
                        )
            row = consult.all()

            return row
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.invalidate()
            db.close()


    # actualizamos un request especifico
    def update_resp_orq(self, response_orq):
        db = Database('dbw').session
        try:
            db.add(response_orq)
            db.commit()
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.invalidate()
            db.close()

    def reintentar_ejecucion(self, ejecucion_motor):
        db = Database('dbw').session
        try:
            db.add(ejecucion_motor)
            db.commit()
            
        except Exception as e:
            raise ValueError(str(e))
        finally:
            db.invalidate()
            db.close()
