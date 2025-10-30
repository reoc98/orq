from models.RequestsOrquestadorModel import RequestsOrquestadorModel
from models.Arbol import Arbol
from models.EjecucionMotor import EjecucionMotor
from models.ArbolEjecucion import ArbolEjecucion
from clases.Database import Database
from sqlalchemy.sql import func

class ProcesoMotorDB():
    def __init__(self, mode = 'dbr') -> None:
        # Inicializamos una conexion por el Objeto.
        self.db = Database(mode).session

    def cerrar_conexion(self):
        self.db.invalidate()
        self.db.close()
    
    # Obtener request de orquestador
    def get_request_orq(self, ejecucion, limit:int=0, max_reintentos = 0):
        try:
            consult = self.db.query(RequestsOrquestadorModel
                    ).filter(
                        RequestsOrquestadorModel.ejecucion == ejecucion,
                        RequestsOrquestadorModel.risk == 1,
                        RequestsOrquestadorModel.estado == 1,
                        RequestsOrquestadorModel.reintentar <= max_reintentos
                    )
            
            if int(limit) > 0:
                consult = consult.limit(limit)

            rows = consult.all()

            return rows
        except Exception as e:
            raise ValueError(str(e))

    # Obtenemos los motores activos a ejecutar
    def get_motores_ejecutar(self):
        try:
            rows = self.db.query(
                            Arbol,
                            ArbolEjecucion
                        ).join(
                            ArbolEjecucion, Arbol.codigo == ArbolEjecucion.codigo
                        ).filter(
                            Arbol.activo == 1,
                            Arbol.padre == 1,
                            ArbolEjecucion.estado == 1
                        ).order_by(
                            Arbol.id
                        ).all()

            return rows
            
        except Exception as e:
            raise ValueError(str(e))

    # Se prepara la tabla y la ejecucion de los arboles
    def preparar_motores_ejecutar(self, motores_a_ejecutar):
        try:
            for pre_ejecucion in motores_a_ejecutar:
                id_request = pre_ejecucion['id_request']
                id_arbol = pre_ejecucion['id_arbol'] 
                figura = pre_ejecucion['figura']
                codigo_arbol = pre_ejecucion['codigo_arbol']

                # Prepara los datos para insertar
                row = EjecucionMotor(id_request, id_arbol, figura, codigo_arbol)
                
                self.db.add(row)
                self.db.commit()
            
        except Exception as e:
            raise ValueError(str(e))

    def total_motores_ejecucion(self, id_request):
        
        try:
            row = self.db.query(func.count(EjecucionMotor.id).label('total')).filter(
                EjecucionMotor.id_request == id_request).first()

            return row
        except Exception as e:
            raise ValueError(str(e))

    def contar_reintento(self, id_request, reintentar):
        try:
            upd = {'reintentar': reintentar}
            
            row = self.db.query(
                        RequestsOrquestadorModel
                    ).filter(
                        RequestsOrquestadorModel.id == id_request
                    )

            row.update(upd)
            self.db.commit()
            
        except Exception as e:
            raise ValueError(str(e))