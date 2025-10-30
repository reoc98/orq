
from classes.Database import Database
from models.ReporteMensualReglasModel import ReporteMensualReglasModel
from models.Meses import Meses
from models.Departamentos import Departamentos
from models.Arbol import Arbol
from models.EjecucionMotor import EjecucionMotor
from models.RequestsOrquestador import RequestsOrquestador
from models.ReporteMensualSiniestros import ReporteMensualSiniestros
from sqlalchemy.sql import func, extract
import json

class ReglasDatabase():
    @classmethod
    def insert_rules_report(cls, resquest):
        db = Database('dbw').session
        try:
            # guardamos como pendiente en la tabla de reportes siniestro
            payload = {
                "finalizado": 0,
                "estado": 0,
                "request": json.dumps(resquest),
                "usuario": resquest["usuario"]
            }

            row = ReporteMensualReglasModel(**payload)
            db.add(row)
            db.commit()

            return row.id
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def get_all_report(cls, data):
        db = Database('dbr').session
        try:
            consult = db.query(func.distinct(Arbol.codigo).label('codigo_arbol')).join(
                    EjecucionMotor, EjecucionMotor.codigo_arbol == Arbol.codigo
                ).join(
                    RequestsOrquestador, RequestsOrquestador.id == EjecucionMotor.id_request
                ).filter(
                    RequestsOrquestador.ejecucion == 4,
                    RequestsOrquestador.estado == 1,
                    EjecucionMotor.fecha_upd.between(data['start_date'], data['end_date']),
                    Arbol.activo == 1,
                    Arbol.padre == 1
                ).order_by(Arbol.codigo)
            
            if data['id_motor'] != 0:
                consult = consult.filter(Arbol.id == data['id_motor'])
            
            if data['code_departament'] != '':
                consult = consult.filter(RequestsOrquestador.cod_departamento == data['code_departament'])
            
            rows = consult.all()

            return rows

        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()
    
    @classmethod
    def get_rules_report(cls, data):
        db = Database('dbr').session
        try:
            consult = db.query(EjecucionMotor.desenlace_contenido.label('desenlace_contenido'), 
                               Arbol.nombre.label('nombre_arbol'),
                               Arbol.codigo.label('codigo_arbol')
                ).join(
                    RequestsOrquestador, RequestsOrquestador.id == EjecucionMotor.id_request
                ).join(
                    Arbol, Arbol.codigo == EjecucionMotor.codigo_arbol
                ).filter(
                    RequestsOrquestador.ejecucion == 4,
                    RequestsOrquestador.estado == 1,
                    EjecucionMotor.fecha_upd.between(data['start_date'], data['end_date']),
                    Arbol.activo == 1,
                    Arbol.padre == 1
                ).order_by(Arbol.codigo)
            
            if data['id_motor'] != 0:
                consult = consult.filter(Arbol.id == data['id_motor'])
            
            if data['code_departament'] != '':
                consult = consult.filter(RequestsOrquestador.cod_departamento == data['code_departament'])
            
            rows = consult.all()

            return rows

        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def valid_month(cls, id_month):
        db = Database('dbr').session
        try:
            row = db.query(Meses.id, Meses.descripcion).filter(
                Meses.id == id_month
            ).first()

            return row         
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def valid_departament(cls, id_departament):
        db = Database('dbr').session
        try:
            row = db.query(Departamentos.id, Departamentos.descripcion, Departamentos.codigo).filter(
                Departamentos.id == id_departament
            ).first()

            return row         
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def valid_motor(cls, id_motor):
        db = Database('dbr').session
        try:
            row = db.query(Arbol).filter(
                Arbol.id == id_motor,
                Arbol.activo == 1,
                Arbol.padre == 1
            ).first()

            return row         
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    # Función encargada de obtener los motores activos
    @classmethod
    def get_select_reglas(cls):
        db = Database('dbr').session
        try:
            rows = db.query(Arbol.id, Arbol.nombre).filter(
                Arbol.activo == 1,
                Arbol.padre == 1
            ).all()

            return rows        
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    # Función actulizar la talba de reportes
    @classmethod
    def update_rules_report(cls, id_reporte: int, payload):
        dbw = Database('dbw').session
        try:
            query = dbw.query(
                ReporteMensualReglasModel
            ).filter(
                ReporteMensualReglasModel.id == id_reporte
            )
            
            query.update(payload)
            dbw.commit()        
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            dbw.invalidate()
            dbw.close()

    # Validamos si ya se generó el reporte
    @classmethod
    def validar_reporte_reglas(cls, id_reporte):
        db = Database('dbr').session
        try:

            row = db.query(ReporteMensualReglasModel
            ).filter(
                ReporteMensualReglasModel.id == id_reporte
            ).first()

            return row

        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    # Función encargada de obtener los motores activos
    @classmethod
    def select_yeas_rules(cls):
        db = Database('dbr').session
        try:
            consult = db.query(func.distinct(extract('year', RequestsOrquestador.fecha_reg)).label('year')).filter(
                RequestsOrquestador.estado == 1,
                RequestsOrquestador.ejecucion == 4
            )
            rows = consult.all()

            return rows        
        
        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def get_path_report(cls, id_report: int, type: int = 1):
        db = Database('dbr').session
        try:
            if type == 11:
                consult = db.query(ReporteMensualReglasModel).filter(
                                    ReporteMensualReglasModel.estado == 1,
                                    ReporteMensualReglasModel.finalizado == 1,
                                    ReporteMensualReglasModel.id == id_report
                                )
            else:
                consult = db.query(ReporteMensualSiniestros).filter(
                    ReporteMensualSiniestros.estado == 1,
                    ReporteMensualSiniestros.id == id_report
                )

            return consult.first()

        except Exception as e:
            raise Exception(str(e))
        
        finally:
            db.invalidate()
            db.close()
