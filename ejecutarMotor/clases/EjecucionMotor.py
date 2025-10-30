from utils.Response import Response
from clases.Motor import Motor
from clases.EjecucionMotorDB import EjecucionMotorDB
from utils.Aws import Aws, os
import json
from datetime import datetime



# Clase para consumos de los servicios hacia risk
class EjecucionMotor():

    def __init__(self) -> None:
        self.responseData = Response()
        self.Motor = Motor()
        self.motor_dbr = None
        self.motor_dbw = None

    def ejecutar_request(self, id_request):
        try:
            # Inicializamos la conexion de escritura
            self.motor_dbr = self.motor_dbr = EjecucionMotorDB()

            # Buscamos el Request/Siniestro y vemos si existe
            request = self.motor_dbr.get_request_orq(id_request)
            if request == None:
                raise ValueError(f"El Request que se ha recibido no existe({id_request}).")

            # Obtenemos todos los motores a ejecutar
            ejecucion_motores = self.motor_dbr.get_ejecuciones_motor(id_request)

            # Empezamos a armar la data a enviar Iniciando con la data general
            datos = json.loads(request.request.replace("\'", "\""))
            datos['id_request_orquestador'] = request.id
            datos['dias_ocurrencia'] = self.get_dias_ocurrencia()

            # Inicializamos la conexion de escritura
            self.motor_dbw = EjecucionMotorDB('dbw')

            # Recorremos las ejecuciones para ralizar el connsumo
            for ejecucion_motor in ejecucion_motores:
                obj_ejecucion_motor = ejecucion_motor.EjecucionMotor
                # Generamos la informacion
                send_data = self.generar_data_send(ejecucion_motor, datos, id_request)

                self.consumo_motor_reglas(send_data, obj_ejecucion_motor.id)
                
                # validamos la respuesta del motor

            self.motor_dbw.upd_ejecucion_siniestro(id_request)
            return self.responseData.armadoBody("Se ejecutaron los motores", 200, [])

        except Exception as error:
            respt = self.responseData.armadoBody(str(error), 400)
            return respt
        
        finally:
            # Cerramos las conexiones abiertas
            if self.motor_dbr is not None:
                self.motor_dbr.cerrar_conexion()
            if self.motor_dbw is not None:
                self.motor_dbw.cerrar_conexion()
    
    def consumo_motor_reglas(self, send_data, id_ejecucion):
        try:
            if send_data != False:
                resp_motor = self.Motor.ejecutar_motor(send_data)
            else:
                raise ValueError("No se ha ejecutado el servicio, debido a que ocurrio un error al generar la data")

            # guardamos los logs
            self.motor_dbw.guardarLog(id=id_ejecucion,
                    datos_recibidos=resp_motor['resp'],
                    estado=1,
                    datos_enviados=json.dumps(send_data),
                    desenlace=resp_motor['desenlace']
                )
        except Exception as e:
            self.motor_dbw.guardarLog(id=id_ejecucion,
                    datos_recibidos=f"***Exception***: {str(e)}",
                    estado=1,
                    datos_enviados=json.dumps(send_data),
                    desenlace={"resultado": "0", "semaforo": "0", "mensaje": "blanco"}
                )

        


    # **** MEJORAR ***
    def generar_data_send(self, ejecucion_motor, datos_send, id_request):
        try:
            data = datos_send.copy()
            # Si es interviniente se coloca los campos en el array
            if ejecucion_motor.tipo == "Interviniente":
                # obtenemos la ejecucion del motor para saber el tipo persona
                figura_ejecucion = ejecucion_motor.EjecucionMotor
                info_figura = json.loads(figura_ejecucion.figura.replace("\'", "\""))

                # le agregamos el tipo figura a los datos a enviar
                for key, valor in info_figura.items():
                    data[str(key)] = valor

                # validamos si es un interviniente de risk
                if ejecucion_motor.risk == 1:
                    # obtenemos la consulta de risk del interviniente y validamos
                    risk = self.motor_dbr.obtenerConsulaRisk(id_request, info_figura['num_doc_figura'])

                    if risk != None:
                        # obtenemos la respuesta de risk y filtramos el datos que necesita el motor
                        info_risk = json.loads(risk.data_response)
                        resp_risk = self.obtenerRisk(info_risk, ejecucion_motor.risk_array)
                        if resp_risk:
                            # le agregamos los datos de risk a los datos a enviar
                            for key, valor in resp_risk.items():
                                data_r = valor
                                if isinstance(data_r, bool):
                                    data_r = str(data_r).lower()
                                data[str(key)] = data_r
                elif ejecucion_motor.risk == 2:
                    inif = EjecucionMotorDB.get_service_inif(id_request, info_figura['num_doc_figura'])
                    # if not inif:
                    #     raise ValueError(f"No se encontro informacion en INIF para el documento {info_figura['num_doc_figura']}")
                    if inif:
                        data_inif = json.loads(inif.response.replace("\'", "\""))
                        if isinstance(data_inif, list) and len(data_inif) > 0:
                            data_inif = data_inif[0]
                            data.update({
                                'identity': data_inif.get('input', {}).get('identity',''),
                                'typeId': data_inif.get('input', {}).get('typeId',''),
                                'docNum': data_inif.get('input', {}).get('docNum',''),
                                'generalScore': data_inif.get('generalScore',''),
                                'generalRiskLevel': data_inif.get('generalRiskLevel',''),
                                'generalInfo': data_inif.get('generalInfo',''),
                                'score': data_inif.get('riskResult',{}).get('score',''),
                                'riskLevel': data_inif.get('riskResult',{}).get('riskLevel','')
                            })
            return {
                'datos_front': data,
                "motor_codigo": ejecucion_motor.codigo,
                "credito_id": 1,
                "empresa_id": 2,
                "op": 1
            }
        
        except Exception as error:
            return False

    def get_dias_ocurrencia(self):
        try:
            secret = Aws.getSecret(str(os.getenv('STAGE'))+"/secret-orquestador")
            return secret["dias_ocurrencia"]
            
        except Exception as error:
            raise ValueError(str(error))
        
    
    # obtenemos el risk correspondiente
    def obtenerRisk(self, request, risk):

        almacenamiento = []
        if "resultados" in request:
            # recorremos el array
            for row in request["resultados"]:
                if row["lista"] == risk:
                    return row

        return almacenamiento
        