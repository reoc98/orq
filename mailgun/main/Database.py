from logging import warning
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from Log_Api.Utils.Aws import Aws
import json

base_class = declarative_base()  # Extend class for models

_instaces = {
    "dbw": None,
    "dbr": None,
}


class Database():

    def __new__(cls, mode):
        if mode is None or (mode != "dbw" and mode != "dbr"):
            raise Warning("El modo de uso de base de datos no es válido.")

        global _instaces

        if _instaces[mode] is None:
            _instaces[mode] = super(Database, cls).__new__(cls)
            _instaces[mode]._initialize(mode)
        return _instaces[mode]

    def _initialize(self, mode):
        try:
            connection_data = Aws(f'{mode}-orq').get_secret()

            # Get connections strings from secret manager
            __connection_strings = self.__get_connection_strings(
                connection_data)

            # Create a engine DB
            self.__engine = create_engine(
                __connection_strings,
                poolclass=QueuePool,
                pool_size=1,
                max_overflow=2
            )
            # Create the association between the engine and the session
            self.__session_maker = sessionmaker(bind=self.__engine)
            # Create a new session
            self.session = self.__session_maker()

        except Exception as e:
            raise warning('Error en conexion Base de datos')

    def __get_connection_strings(self, credentials_data):
        """
        Si el nombre de la base de datos no está vacío, devuelva la cadena de conexión con el nombre de
        la base de datos; de lo contrario, devuelva la cadena de conexión con el nombre de la base de
        datos predeterminado

        :param credentials_data: 
        :return: La cadena de conexión
        """

        string_conexion = "mysql+pymysql://{0}:{1}@{2}/{3}".format(
            credentials_data["username"],
            credentials_data["password"],
            credentials_data["host"],
            credentials_data["bd_name"],
        )
        # Se retorna la cadena de conexion
        return string_conexion
