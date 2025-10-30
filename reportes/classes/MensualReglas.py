from classes.ReglasDatabase import ReglasDatabase
from classes.PermissionsDatabase import PermissionsDatabase
from utils.Aws import Aws, os
from utils.Response import Response
from datetime import datetime, date
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.styles import Font
from openpyxl.styles import Border
from openpyxl.styles import Side
import calendar
import json
import os

class MensualReglas(Response):
    @classmethod
    def monthly_rules_report(cls, payload):
        try:
            # Validamos si el usuario tiene los permisos para relizar esta operació
            resp_permission = cls.validate_permission(user = payload["usuario"], type = "LISTAR")

            if resp_permission != False:
                # Validamos los datos de entrada
                anio = payload["anio"]
                month = payload["mes"]
            
                if len(str(anio)) > 4:
                    raise ValueError("Año invalido")
                
                mes = ReglasDatabase.valid_month(payload['mes'])
                if mes is None:
                    raise ValueError("Mes inválido.")

                if payload["departamento"] != 0:
                    departamento = ReglasDatabase.valid_departament(payload["departamento"])
                    if departamento is None:
                        raise ValueError("Departamento inválido.")
                    else:
                        code_departament = departamento.codigo
                        departamento = departamento.descripcion
                else:
                    departamento = "Todos"
                    code_departament = ""

                if payload["tipo_regla"] != 0:
                    motor = ReglasDatabase.valid_motor(payload["tipo_regla"])
                    if motor is None:
                        raise ValueError("La regla seleccionada es inválida.")
                    else:
                        nombre_motor = motor.nombre
                else:
                    nombre_motor = ""

                # Generamos la fecha de inicio y final para el intervalo.
                num_days = calendar.monthrange(anio, month)[1]
                start_date = date(anio, month, 1)
                end_date = date(anio, month, num_days)

                # Guardamos la generacion del reporte
                serv_resp = ReglasDatabase.insert_rules_report(payload)

                # Generamos los porcentajes de acuerdo


                # Generamos un request para enviar al servici oque genera el excel
                request = {
                    "id_report": serv_resp,
                    "id_motor": payload["tipo_regla"],
                    "name_motor": nombre_motor,
                    "start_date": f"{str(start_date)} 00:00:00",
                    "end_date": f"{str(end_date)} 23:59:59",
                    "name_month": mes.descripcion,
                    "departament": departamento,
                    "code_departament": code_departament,
                    "anio": payload["anio"],
                    "email_user": resp_permission['email']
                }

                cls.generarReporteMensual(request)

                return cls.success({"id_report": serv_resp})
            else:
                raise ValueError("No cuenta con los permisos necesarios para realizar esta operación.")
                
        except Exception as e:
            Type = type(e)
            raise Type(str(e))
        
    # Funcion para valdiar el permiso que tiene un usuario
    @classmethod
    def validate_permission(cls, user: int, type: str, module: int = 11):
        try:
            data = {
                "USUARIO": user,
                "ID_MODULO": module,
                "PERMISO": type
            }

            resp_db = PermissionsDatabase.consult_permission(data)
            
            if resp_db is not None:
                return {'estado': True, "email": resp_db.CORREO}
            else:
                return False

        except Exception as e:
            raise ValueError(str(e))

    # ejecutar reporte de siniestro
    @classmethod
    def generarReporteMensual(cls, data):
        try:
            ejecuciones = ReglasDatabase.get_rules_report(data)

            num_invalidate = 0
            num_positive = 0
            num_negative = 0
            total = len(ejecuciones)

            for ejecucion in ejecuciones:
                if ejecucion.desenlace_contenido != 'null':
                    semaforo = json.loads(ejecucion.desenlace_contenido.replace("\'", "\""))
                else:
                    semaforo = {}
                
                if "semaforo" not in semaforo:
                    num_invalidate += 1
                else:
                    if int(semaforo["semaforo"]) == 1:
                        num_positive += 1
                    elif int(semaforo["semaforo"]) in (2,3):
                        num_negative += 1
                    else:
                        num_invalidate += 1

            # Generar porcentaje
            porc_invalidate = cls.round_percentage(num_invalidate, total)
            porc_positive = cls.round_percentage(num_positive, total)
            porc_negative = cls.round_percentage(num_negative, total)

            data['response'] = {
                "id_report": data['id_report'],
                "informacion": {
                    "regla": data['name_motor'],
                    "departamento": data['departament'],
                    "mes": data['name_month'],
                    "anio": data['anio']
                },
                "estadistica": {
                    "positivo": {
                        "cantidad": num_positive,
                        "porcentaje": porc_positive
                    },
                    "negativo": {
                        "cantidad": num_negative,
                        "porcentaje": porc_negative
                    },
                    "fallido": {
                        "cantidad": num_invalidate,
                        "porcentaje": porc_invalidate
                    },
                    "total": total
                }
            }

            # llamamos la lambda asyncrona
            Aws.lambdaInvoke(
                    str(os.getenv('SERVICE'))
                    + '-'+str(os.getenv('STAGE'))
                    + '-async_generar_mensual_reglas', data)

            return data['response']
        
        except Exception as e:
            raise Exception(str(e))
        
    # obtener informacion del reporte mensual
    @classmethod
    def informacionReporte(cls, data):
        try:
            listado = []
            
            if data['id_motor'] == 0:
                motores = ReglasDatabase.get_all_report(data)
                ejecuciones = ReglasDatabase.get_rules_report(data)


                for motor in motores:
                    nom_motor = ""
                    num_invalidate = 0
                    num_positive = 0
                    num_negative = 0
                    total = 0
                    
                    for ejecucion in ejecuciones: 
                        if motor.codigo_arbol == ejecucion.codigo_arbol:
                            if ejecucion.desenlace_contenido != 'null':
                                semaforo = json.loads(ejecucion.desenlace_contenido.replace("\'", "\""))
                            else:
                                semaforo = {}
                                
                            nom_motor = ejecucion.nombre_arbol
                            total += 1

                            if "semaforo" not in semaforo:
                                num_invalidate += 1
                            else:
                                if int(semaforo["semaforo"]) == 1:
                                    num_positive += 1
                                elif int(semaforo["semaforo"]) in (2,3):
                                    num_negative += 1
                                else:
                                    num_invalidate += 1

                    # Generar porcentaje
                    porc_invalidate = cls.round_percentage(num_invalidate, total)
                    porc_positive = cls.round_percentage(num_positive, total)
                    porc_negative = cls.round_percentage(num_negative, total)

                    listado.append({
                        "informacion": {
                            "regla": nom_motor,
                            "departamento": data['departament'],
                            "mes": data['name_month'],
                            "anio": data['anio']
                        },
                        "estadistica": {
                            "positivo": {
                                "cantidad": num_positive,
                                "porcentaje": porc_positive
                            },
                            "negativo": {
                                "cantidad": num_negative,
                                "porcentaje": porc_negative
                            },
                            "fallido": {
                                "cantidad": num_invalidate,
                                "porcentaje": porc_invalidate
                            },
                            "total": total
                        }
                    })

            else:
                listado.append(data['response'])
            
            data = cls.excel_reporte_mensual_reglas(data, listado)

            return data
        
        except Exception as error:
            raise Exception(str(error))

    # genera el excel de reporte
    @classmethod
    def excel_reporte_mensual_reglas(cls, datos, listado):
        try:
            columnas_datos = 'ABCDEFGHIJ'
            date1 = datetime.today()
            date = date1.strftime('%Y%m%d%H%M%S')
            file_name = f"Reporte_Mensual_Reglas_{date}.xlsx"
            tmp_dir = os.getenv('TMP')
            tmp_path = f"{tmp_dir}{file_name}"
            file_path = f"reporte_reglas/{file_name}"

            dateFormat_i = datetime.strptime(datos['start_date'], '%Y-%m-%d %H:%M:%S')
            fecha_inicio = dateFormat_i.strftime('%d/%m/%Y')
            
            dateFormat_f = datetime.strptime(datos['end_date'], '%Y-%m-%d %H:%M:%S')
            fecha_fin = dateFormat_f.strftime('%d/%m/%Y')
            
            wb = Workbook()
            worksheet = wb.active

            f_hoy = date1.strftime('%d/%m/%Y')
            worksheet['A1'] = "Orquestador"
            worksheet['A2'] = "Reporte Mensual de Reglas"
            worksheet['A3'] = f"Reporte generado entre {fecha_inicio} al {fecha_fin}"
            worksheet['A4'] = f"Reporte generado el {f_hoy} por - {datos['email_user']}"

            worksheet['A6'] = 'REGLA'
            worksheet['B6'] = 'MES'
            worksheet['C6'] = 'AÑO'
            worksheet['D6'] = 'POSITIVOS'
            worksheet['E6'] = '% POSITIVOS'
            worksheet['F6'] = 'NEGATIVOS'
            worksheet['G6'] = '% NEGATIVOS'
            worksheet['H6'] = 'FALLIDOS'
            worksheet['I6'] = '% FALLIDOS '
            worksheet['J6'] = 'TOTAL'
            
            bordes = Border(
                    left=Side(border_style='thin'),
                    right=Side(border_style='thin'),
                    top=Side(border_style='thin'),
                    bottom=Side(border_style='thin')
                )
            
            alineacion = Alignment(
                    horizontal="center",
                    vertical="center",
                    wrap_text=True
                )

            for columna in list(columnas_datos):
                # Ancho de las columnas (A hasta J)
                worksheet.column_dimensions[columna].width = 15

                # Estilo negriya para la fuente (A6 hasta J6)
                worksheet[f'{columna}6'].font = Font(bold=True)

                # Bordes para las celdas (A6 hasta J6)
                worksheet[f'{columna}6'].border = bordes
                worksheet[f'{columna}6'].alignment = alineacion


            # Estilo negriya (A1 hasta A4) 
            for num in range(1,5):
                worksheet.merge_cells(f'A{num}:D{num}')
                worksheet[f'A{num}'].font = Font(bold=True)

            i = 7
            for item in listado:
                worksheet[f'A{i}'] = item['informacion']['regla']
                worksheet[f'B{i}'] = item['informacion']['mes']
                worksheet[f'C{i}'] = item['informacion']['anio']
                worksheet[f'D{i}'] = item['estadistica']['positivo']['cantidad']
                worksheet[f'E{i}'] = item['estadistica']['positivo']['porcentaje']
                worksheet[f'F{i}'] = item['estadistica']['negativo']['cantidad']
                worksheet[f'G{i}'] = item['estadistica']['negativo']['porcentaje']
                worksheet[f'H{i}'] = item['estadistica']['fallido']['cantidad']
                worksheet[f'I{i}'] = item['estadistica']['fallido']['porcentaje']
                worksheet[f'J{i}'] = item['estadistica']['total']

                for columna in list(columnas_datos):
                    worksheet[f'{columna}{i}'].border = bordes
                    if columna != 'A':
                        worksheet[f'{columna}{i}'].alignment = alineacion
                    

                i += 1

            wb.save(tmp_path)
            wb["Sheet"].title = "Listado de Reglas"

            secret = Aws.getSecret(str(os.getenv('STAGE'))+"/secret-orquestador")
            Aws.subirArchivoS3(secret['bucket_s3'], tmp_path, file_path)

            # Obtenemos los datos del archivo
            data_path = {
                'ruta': file_path,
                'respuesta': json.dumps(datos),
                'estado': 1,
                'finalizado': 1
            }

            ReglasDatabase.update_rules_report(datos['id_report'], data_path)
            
            return data_path
        
        except ValueError as e:
            ReglasDatabase.update_rules_report(datos['id_report'], {'finalizado': 1, 'respuesta': '{}'})
            raise Exception(f"Error al generar excel "+str(e))
        
        except Exception as e:
            ReglasDatabase.update_rules_report(datos['id_report'], {'finalizado': 1, 'respuesta': '{}'})
            raise Exception(f"Error al generar excel "+str(e))
        
    @classmethod
    def round_percentage(cls, quantity: int, total: int, roun_digit: int = 2):
        try:
            if quantity != 0:
                percentage = (quantity / total) * 100
                percentage = round((percentage * 1.0), roun_digit)

                if percentage == 100:
                    percentage = "100.0"

            else:
                percentage = "0.0"

            return percentage
        
        except Exception as e:
            raise Exception(str(e))
        
    # Función encargada de obtener las reglas de motores
    @classmethod
    def get_select_reglas(cls):
        try:
            reglas = ReglasDatabase.get_select_reglas()

            if len(reglas):
                #Parametros para todas
                todas = [{"id": 0, "nombre": 'Todas' }]
                reglas = [ {"id": regla.id, "nombre": regla.nombre } for regla in reglas ]
                todas.extend(reglas)
                return cls.success(todas)
            else:
                return cls.error(message="No se ha encontrado información.")
        
        except Exception as e:
            raise Exception(str(e))
    
    @classmethod
    def validar_reporte_reglas(cls, payload):
        try:
            # Validamos si el usuario tiene los permisos para relizar esta operació
            resp_permission = cls.validate_permission(user = payload["id_usuario"], type = "LISTAR")

            if resp_permission != False:
                reporte = ReglasDatabase.validar_reporte_reglas(payload["id_reporte"])

                if reporte is not None:
                    if reporte.finalizado == 1:
                        if reporte.estado == 1:
                            respuesta = json.loads(reporte.respuesta)

                            if(respuesta['response']['estadistica']['total'] != 0):
                                data = {
                                    "finalizado": 1,
                                    "respuesta": respuesta['response']
                                }

                                return cls.success(data=data, message="El reporte ha sido genereado con exito.")
                            
                            else:
                                return cls.error(message="No se pudo generar el reporte.")

                        else:
                            return cls.error(message="No se pudo generar el reporte.")
                        
                    else:
                        return cls.success(message="Generando reporte...", data= {"finalizado": reporte.finalizado})

                else:
                    return cls.error(message="No se ha encontrado información.")
                
            else:
                raise ValueError("No cuenta con los permisos necesarios para realizar esta operación.")
        
        except Exception as e:
            Type = type(e)
            raise Type(str(e))
        
    # Obtenr lo años de los reportes
    @classmethod
    def get_years(cls):
        try:
            reglas = ReglasDatabase.select_yeas_rules()

            if len(reglas):
                reglas = [ regla.year for regla in reglas ]
                return cls.success(reglas)
            else:
                return cls.error(message="No se ha encontrado información.")
        
        except Exception as e:
            raise Exception(str(e))
        
    # Descargar reporte mensual de sinietros o reglas por número de ID
    @classmethod
    def download_report(cls, payload):
        try:
            # Validamos si el usuario tiene los permisos para relizar esta operació
            resp_permission = cls.validate_permission(user = payload["id_usuario"], type = "LISTAR", module=payload["id_modulo"])
            if resp_permission == False:
                raise ValueError("No cuenta con los permisos necesarios para realizar esta operación.")
            
            # Consultamos el reporte por su id y tipo
            reporte = ReglasDatabase.get_path_report(payload["id_reporte"], payload["id_modulo"])

            if reporte is not None:
                secret = Aws.getSecret(str(os.getenv('STAGE'))+"/secret-orquestador")
                link_download = Aws.generarLinkDescargaS3(secret['bucket_s3'], reporte.ruta)
                
                if link_download is not None:
                    data = {
                        "url": link_download
                    }
                    return cls.success(data=data, message="El reporte ha sido genereado con exito.")
                else:
                    return cls.error(message="No se pudo generar el archivo.")
            
            else:
                return cls.error(message="No se ha encontrado información.")

        except Exception as e:
            Type = type(e)
            raise Type(str(e))