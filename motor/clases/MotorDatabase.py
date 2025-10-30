from models.ArbolEjecucion import ArbolEjecucion
from models.VariableComentarioModel import VariableComentarioModel
from models.FuenteMotorModel import FuenteMotorModel
from models.ListaRiskModel import ListaRiskModel
from models.TipoFiguraModel import TipoFiguraModel
from models.TipoMotorModel import TipoMotorModel
from models.Arbol import Arbol
from models.ArbolReglasModel import ArbolReglasModel
from models.ArbolVariablesModel import ArbolVariablesModel
from clases.Database import Database
from sqlalchemy.sql import func

class MotorDatabase:
    """
    Esta clase se encargar de hacer validaciones y crear la relacion con Motor.
    """

    @classmethod
    def create_relationship(cls, payload: list):
        db = Database('dbw').session

        try:
            # Preparamos la estructura para guardar la información
            row = ArbolEjecucion(**payload)

            db.add(row)
            db.commit()

            # Responde el servicio
            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def consult_select(cls, type):
        models = {
            "variable": VariableComentarioModel,
            "figura": TipoFiguraModel,
            "fuente": FuenteMotorModel,
            "lista_risk": ListaRiskModel,
            "tipo_motor": TipoMotorModel
        }

        model = models[type]
        db = Database('dbr').session
        try:
            # Preparamos la estructura para guardar la información
            consult = db.query(model).filter(
                model.estado == 1
                )
            row = consult.all()

            # Responde el servicio
            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def exist_item(cls, type, id: int):
        models = {
            "variable": VariableComentarioModel,
            "figura": TipoFiguraModel,
            "fuente": FuenteMotorModel,
            "lista_risk": ListaRiskModel,
            "tipo_motor": TipoMotorModel
        }

        model = models[type]
        db = Database('dbr').session
        try:
            # Preparamos la estructura para guardar la información
            consult = db.query(model).filter(
                model.estado == 1,
                model.id == id
                )
            row = consult.first()

            # Responde el servicio
            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def exist_motor(cls, id: int):
        db = Database('dbr').session

        try:
            # Preparamos la estructura para guardar la información
            consult = db.query(Arbol).filter(
                Arbol.padre == 1,
                Arbol.activo == 1,
                Arbol.id == id
                )
            row = consult.first()

            # Responde el servicio
            return row
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def delete_relationship(cls, payload, codigo):
        db = Database('dbw').session

        try:
            # Prepara la consulta con los datos que se van actualizar filtrando por id del registro
            query = db.query(ArbolEjecucion).filter(
                ArbolEjecucion.codigo == codigo,
                ArbolEjecucion.estado == 1
            )

            
            query.update(payload)
            db.commit()
            

        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()

    @classmethod
    def exist_arbol(cls, id: int):
        db = Database('dbr').session
        try:
            # Preparamos la estructura para guardar la información
            consult = db.query(Arbol).filter(
                Arbol.padre == 0,
                Arbol.activo == 1,
                Arbol.id == id
                )

            return consult.first()
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()
    
    @classmethod
    def find_inside_motor(cls, id_arbol: int):
        db = Database('dbr').session
        try:
            # Preparamos la estructura para guardar la información
            consult = db.query(func.count(ArbolReglasModel.id).label('num_motores')
                    ).join(
                        Arbol, Arbol.id == ArbolReglasModel.arbol_id
                    ).join(
                        ArbolVariablesModel, ArbolVariablesModel.id == ArbolReglasModel.variable_id
                    ).filter(
                        ArbolReglasModel.activo == 1,
                        ArbolVariablesModel.tipo_variable_id == 3,
                        ArbolVariablesModel.tabla_id == id_arbol,
                        Arbol.activo == 1
                    )

            return consult.first()
        
        except Exception as error:
            raise ValueError(str(error))
        
        finally:
            db.invalidate()
            db.close()
    