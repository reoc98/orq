from utils.Response import Response

from clases.ProcesoMotorDB import ProcesoMotorDB
from utils.Aws import Aws, os
import json

# Clase para consumos de los servicios hacia risk
class ProcesoMotorC():
    def __init__(self) -> None:
        self.responseData = Response()
        self.motor_dbr = None
        self.motor_dbw = None
    
    def procesar_siniestros(self):
        try:
            # Se obtiene los valores de los secretos
            secret = Aws.getSecret(str(os.getenv("STAGE"))+"/secret-orquestador")
            limit_request = secret["limite_motor_consumo"]
            reintentos = secret["maximo_reintento_motor"]

            # Inicializamos la conexion de escritura
            self.motor_dbr = ProcesoMotorDB()
            # Obtenemos los Request/Siniestro y revisamos si hay por ejecutar
            requests = self.motor_dbr.get_request_orq(ejecucion=0, limit=limit_request, max_reintentos = reintentos)
            if len(requests)==0:
                return self.responseData.armadoBody("No hay Ssiniestros para ejecutar.", 400)
            
            # Obtenemos todos lo Motores a ejecutar y revisamos si hay para ejecutar
            motores_ejecucion = self.motor_dbr.get_motores_ejecutar()
            if len(motores_ejecucion)==0:
                return self.responseData.armadoBody("No hay motores para ejecutar.", 400)

            # Inicializamos la conexion de escritura
            self.motor_dbw = ProcesoMotorDB('dbw')
            num_reintentos = 0

            for request in requests:
                motores_siniestros = self.motor_dbr.total_motores_ejecucion(request.id)
                if motores_siniestros['total'] == 0:
                    motores_a_ejecutar = []
                    for motor_ejecutar in motores_ejecucion:
                        json_request = json.loads(request.request.replace("\'", "\""))

                        motor = motor_ejecutar.Arbol
                        arbol_ejecucion = motor_ejecutar.ArbolEjecucion

                        # Validamos el tipo de Motor a Ejecutar
                        if arbol_ejecucion.tipo == "Interviniente":

                            # Revisamos si es vehiculo o persona
                            if arbol_ejecucion.vehiculo == 0:
                                # si no es para un vehiculo obtenemos tipo de figura
                                figura = self.obtenerFigura(json_request, arbol_ejecucion.tipo, 1)

                            else:
                                # si es para un vehiculo obtenemos figura vehiculo
                                figura = self.obtenerVehiculo(json_request, arbol_ejecucion.tipo, 1)
                                

                            for data_figura in figura:
                                motores_a_ejecutar.append(self.preprara_estructura(request.id, motor.id, data_figura, motor.codigo))

                        else:
                            # validamos si el motor es para un vehiculo
                            if arbol_ejecucion.vehiculo == 0:
                                # obtenemos el tipo de figura
                                figura = self.obtenerFigura(json_request, arbol_ejecucion.tipo, 0)
                            else:
                                # si es para un vehiculo obtenemos figura vehiculo
                                figura = self.obtenerVehiculo(json_request, arbol_ejecucion.tipo, 0)

                            # si el tipo de figura no existe lo guardamos en null
                            if len(figura) == 0:
                                figura = None
                            motores_a_ejecutar.append(self.preprara_estructura(request.id, motor.id, figura, motor.codigo))

                    # Guardamos los motores a ejecutar
                    self.motor_dbw.preparar_motores_ejecutar(motores_a_ejecutar)
                else:
                    num_reintentos += 1
                    reintentar = request.reintentar + 1
                    self.motor_dbw.contar_reintento(request.id, reintentar)

                self.ejecutar_request(request.id)

            response = self.responseData.armadoBody("Proceso De Preparacion Finalizado. " \
                                                    f"Se van a Ejecutar {len(requests)} Siniestros, " \
                                                    f"donde {num_reintentos} son Reintentos.", 200)

            return response

        except Exception as error:
            respt = self.responseData.armadoBody(str(error), 400)
            return respt
        
        finally:
            # Cerramos las conexiones abiertas
            if self.motor_dbr is not None:
                self.motor_dbr.cerrar_conexion()
            if self.motor_dbw is not None:
                self.motor_dbw.cerrar_conexion()

    # *** MEJORAR ***
    # Guardar figura para preparación de motor
    def preprara_estructura(self, request_id, motor_id, data_figura, motor_codigo):
        return  {
            "id_request": request_id,
            "id_arbol": motor_id,
            "figura": json.dumps(data_figura),
            "codigo_arbol": motor_codigo
        }
    
    # Se prepara la tabla y la ejecucion de los arboles
    def ejecutar_request(self, id_request):
        try:
            info = {
                "id_request": id_request
            }

            # llamamos la lambda asyncrona
            Aws.lambdaInvoke(
                    'allianz-orq-motor'
                    + '-'+str(os.getenv('STAGE'))
                    + '-ejecucionMotor',
                    info)
            
        except Exception as error:
            raise ValueError(str(error))

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