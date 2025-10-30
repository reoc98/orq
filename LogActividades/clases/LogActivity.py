from utils.Response import Response
from clases.ActivitiesDatabase import ActivitiesDatabase
from utils.Validations import Validations
from datetime import datetime
import json

class LogActivity(Response, Validations):

    # Función encargada de obtener todas los usuarios
    @classmethod
    def get_users_log(cls):
        result = ActivitiesDatabase.get_users_log_bd(option = 1)
        
        if len(result) == 0:
            raise ValueError("No se encontraron datos.")
        
        if "status" in result:
            return cls.internal_server_error()
        
        rows =[]
        # recorre los resultados obtenidos para crear lista
        for users in result:
            rows.append({
            'ID': users.id,
            'CODIGO_CE': users.codigo_ce})
                    
        return cls.success(data = rows)


    # Función encargada de obtener todos los perfiles
    @classmethod
    def get_profiles_log(cls):
        result = ActivitiesDatabase.get_profiles_log_bd()

        if len(result) == 0:
            raise ValueError("No se encontraron datos.")
        
        if "status" in result:
            return cls.internal_server_error()
        
        rows =[]
        # recorre los resultados obtenidos para crear lista
        for profile in result:
            rows.append({
                "ID": profile.id,
                "NOMBRE": profile.nombre
                })

        return cls.success(data = rows)

    # Función encargada de obtener todas los usuarios afectados
    @classmethod
    def get_users_affected(cls):
        result = ActivitiesDatabase.get_users_log_bd(option = 2)

        if len(result) == 0:
            raise ValueError("No se encontraron datos.")
        
        if "status" in result:
            return cls.internal_server_error()
        
        rows =[]
        # recorre los resultados obtenidos para crear lista
        for users in result:
            rows.append({
            'ID': users.id,
            'CODIGO_CE': users.codigo_ce})
                    
        return cls.success(data = rows)

    # Función encargada de obtener los tipos de actividades
    @classmethod
    def get_activity_type(cls, payload):
        result = ActivitiesDatabase.get_activity_type_bd(payload)

        if len(result) == 0:
            raise ValueError("No se encontraron datos.")
        
        if "status" in result:
            return cls.internal_server_error()
        
        rows =[]
        for activity in result:
                rows.append({
                    "ID": activity.id,
                    "NOMBRE": activity.nombre
                    })

        return cls.success(data = rows)

    @classmethod
    def __validate_date_now(cls, name, date):
        if date > datetime.now():  # valida que la fecha no sea mayor a la fecha actual
            raise ValueError(
                f"La fecha {name} no puede ser mayor a la fecha actual")
        

    # Función encargada de crear filtros
    @classmethod
    def create_filter(cls, payload):
        #try:
        if 'ID_PERIODO' in payload and payload['ID_PERIODO'] == 2:
            #valida que se recibe fechas para filtrar actividades en el log
            if 'FECHA_INICIAL' not in payload or 'FECHA_FINAL' not in payload:
                raise ValueError (
                    "Debe seleccionar la fecha inicial y fecha final")

            #validar formato de fecha
            initial_formatted = cls.format_date(payload['FECHA_INICIAL'], 2)
            if initial_formatted == False:
                raise ValueError(
                    'Formato de fecha inicial incorrecto')
            final_formatted = cls.format_date(payload['FECHA_FINAL'], 2)
            if final_formatted == False:
                raise ValueError(
                    'Formato de fecha final incorrecto')

            #validar que la fecha no sea mayor que la actual
            cls.__validate_date_now('inicial', datetime.strptime(
                        payload['FECHA_INICIAL'], '%Y-%m-%d'))

            cls.__validate_date_now('final', datetime.strptime(
                        payload['FECHA_FINAL'], '%Y-%m-%d'))

            #valida que la fecha inicial sea menor que fecha final
            if payload['FECHA_INICIAL'] > payload['FECHA_FINAL']:
                raise ValueError (
                    "La fecha inicial debe ser menor que la fecha final")   
    
        result = ActivitiesDatabase.get_log(payload)
        if result['status'] == 200:
            return cls.success(result['data'])
        elif result['status'] == 400:
            raise ValueError("No se encontraron datos.")
        else:
            return cls.internal_server_error()            


    # Función encargada de obtener los periodos de tiempo del filtro
    @classmethod
    def get_period(cls):
        result = ActivitiesDatabase.get_period_bd()
        
        if len(result) == 0:
            raise ValueError("No se encontraron datos.")
        
        if "status" in result:
            return cls.internal_server_error()
        
        rows = []
        for period in result:
            rows.append({
                "ID": period.id,
                "DESCRIPCION": period.descripcion
                })

        return cls.success(data = rows)

    # Funcion encargada de consultar por Activiada la informacion de esta
    @classmethod
    def get_activity(cls, data):

        # Declaramos las variables que vamos a utilizar
        id_actividad = data['ID_ACTIVIDAD']

        resp_activity = ActivitiesDatabase.get_activity_bd(id_actividad)
        
        if resp_activity['status'] == 400:
            raise ValueError("No se encontraron datos de la actividad")
        elif resp_activity['status'] == 500:
            return cls.internal_server_error()
        
        activity = resp_activity['data'].LogActividadesModel
        type_activity = resp_activity['data'].TipoActividadModel
        user_activity = resp_activity['data'].UsuariosModel

        # Obtenemos el nombre de la entida segun su tipo
        nombreEntidad = ""
        type_format = 3

        if type_activity.modulo == 1:
            nombreEntidad = (ActivitiesDatabase.get_user((activity.entidad)))
        elif type_activity.modulo == 4:
            nombreEntidad = (ActivitiesDatabase.get_perfil(activity.entidad))
            type_format = 4
        elif type_activity.modulo == 3 or type_activity.modulo == 7:
            nombreEntidad = (ActivitiesDatabase.get_arbol(activity.entidad))
        
        if nombreEntidad is None:
            raise ValueError("No se encontraron datos de la entidad")
        if "status" in nombreEntidad:
            return cls.internal_server_error()

        nombreEntidad = nombreEntidad.nombre

        # Le damos un formato para mostrar la inforacion de la entidad dependiendo del tipo de la entidad
        previous_inf = cls.get_only_permissions(activity.inf_anterior, type_activity.modulo)
        current_inf = cls.get_only_permissions(activity.inf_actual, type_activity.modulo)

        date_formatted = cls.format_date(str(activity.fecha_reg))
        if date_formatted == False:
            raise ValueError('Hubo un error al momento de obtener la fecha.')
        
        # Armamos la estructura de la informacion que vamos a regresar, clasificada por informacion general y especifica de la entidad
        inf_general = {
            'COD_TIPO_ACTIVIDAD': type_activity.codigo,
            'TIPO_ACTIVIDAD': type_activity.nombre,
            'ID_ENTIDAD': activity.entidad,
            'ENTIDAD': cls.format_fonts(nombreEntidad, type_format),
            'ID_USUARIO': activity.usuario,
            'USUARIO': cls.format_fonts(f'{user_activity.nombres} {user_activity.apellidos}', 3),
            'CODIGO_CE': user_activity.codigo_ce,
            'FECHA_REG': date_formatted
        }

        data = {
            'INFOMACION_GENERAL': inf_general,
            'INFORMACION_ENTIDAD': {
                'INF_ANTERIOR': previous_inf,
                'INF_ACTUAL': current_inf,
                'COMENTARIO': "" if activity.comentario is None else activity.comentario
            }
        }

        return cls.success(data = data)

    # Funcion encargada de consultar por Activiada la informacion de esta
    @classmethod
    def get_only_permissions(cls, infomation, type_module):
        # Identificamos el tipo de modulo que tenemos
        # Usuario
        info = []
        if type_module == 1:
            info = json.loads(infomation if (infomation != '' and infomation != '""' and infomation != 'null') else '{}')
            perfiles = []

            # Revisamos si hay informacion
            if len(info) > 0:
                # Le damos el formato de texto al nombre  y apellido
                info['INFORMACION_BASICA']['NOMBRES'] = cls.format_fonts(info['INFORMACION_BASICA']['NOMBRES'], 3)
                info['INFORMACION_BASICA']['APELLIDOS'] = cls.format_fonts(info['INFORMACION_BASICA']['APELLIDOS'], 3)

                # Recorrer todos opara obtener todos los perfiles asociados al usuario
                for perfil in info['PERFILES']:
                    perfiles.append(cls.format_fonts(perfil['NOMBRE'], 4))

                info['PERFILES'] = perfiles

        # Perfiles y permisos
        elif type_module == 4:
            # Validamos el numero de elementos que hay en la Entidad 
            info = json.loads(infomation if (infomation != '' and infomation != '""' and infomation != 'null') else '{}'),
            permisos_ant = []

            # Revisamos si hay informacion
            if len(info[0]) > 0:
                # Le damos el formato de texto al nombre del perfil
                info[0]['PERFIL']['NOMBRE'] = cls.format_fonts(info[0]['PERFIL']['NOMBRE'], 4)

                # Recorer todos los modulos para obtener los permisos asociados en estos
                for modulo in info[0]['PERMISOS']:
                    # Recorreo los permiso del mudulo par agregarlos al listado de permisos
                    for permiso in modulo['INFO_PERMISOS']:
                        permisos_ant.append(cls.format_fonts(permiso['DESCRIPCION'], 4))

                info[0]['PERMISOS'] = permisos_ant

            info = info[0]
        elif type_module == 3 or type_module == 7:
            info = json.loads(infomation if (infomation != '' and infomation != '""' and infomation != 'null') else '{}')
            if info != []:
                info = info['datos_configuracion']

        return info

    # Funcion para dar formato a la fecha
    @classmethod
    def format_date(cls, date, format=1):
        try:
            # Le damos el formato con el cual va a entrar y salir para hacer el cambio del formato
            if format == 1:
                entry = '%Y-%m-%d %H:%M:%S'
                out = '%d-%m-%Y %H:%M:%S'
            else:
                entry = '%Y-%m-%d'
                out = '%d-%m-%Y'

            dateFormat = datetime.strptime(date, entry)
            formatted_date = dateFormat.strftime(out)
            
            return formatted_date
        except Exception as error:
            return False 
    
    # Funcion para dar formato al String (Mayuscula/Minuscula)
    @classmethod
    def format_fonts(cls, word, type_format = 1):
        # Validamos e lformato al cual vamos a convertir la palabra
        # Todas la letras minusculas
        if type_format == 1:
            word = word.lower()

        # Todas las letras en mayusculas
        elif type_format == 2:
            word = word.upper()

        # La primera letra de cada palabra en mayuscula
        elif type_format == 3:
            word = word.title()

        # la primera letra de la oracion en mayusculas
        elif type_format == 4:
            word = word.capitalize()

        return word

    # Función encargada de obtener todos los arboles y motores
    @classmethod
    def get_arboles_log(cls, tipo = 0):
        result = ActivitiesDatabase.get_arboles_log_bd(tipo)

        if len(result) == 0:
            raise ValueError("No se encontraron datos.")
        
        if "status" in result:
            return cls.internal_server_error()
        
        rows =[]
        # recorre los resultados obtenidos para crear lista
        for arbol in result:
            rows.append({
            'ID': arbol.codigo,
            'NOMBRE': arbol.nombre})
                    
        return cls.success(data = rows)