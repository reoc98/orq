from utils.Response import Response
from clases.UsuariosDatabase import UsuariosDatabase
from clases.Cognito import Cognito
from cryptography.fernet import Fernet
from os import environ as os_environ
import base64
import secrets
import re2
import json
import string
import math
from Log_Api.Utils.Aws import Aws
from Log_Api.Utils.Template import Template
#import traceback

class Usuario (Response):

    # Funcion construsctor de la clase.
    # def __init__(self, payload = {}):
    #     self.payload = payload

    # Función encargada de la creación de usuarios
    def create_user(self, data: dict):
        data_validate = {
            'USUARIO': data['USUARIO'],
            'ID_MODULO': 1,
            'PERMISO': 'CREAR',
        }

        # Validamos msi el usuario tiene los permisos para relizar esta operación
        resp_val_per = self.validate_permission(data_validate)
        if resp_val_per['statusCode'] == 200:
            usuario_database = UsuariosDatabase()
            resp_cod = usuario_database.val_codigo_ce_unique(data['CODIGO_CE'])
            
            if resp_cod is False:
                raise ValueError("El Código CE ya existe.")

            self.validate_correct_email(data['EMAIL'])
            email = data['EMAIL'].lower()
            resp_valid_email = usuario_database.valid_email(email)

            if resp_valid_email is False:
                raise ValueError("El correo ya está en uso.")

            perfiles = data.get("PERFILES",[])
            if len(perfiles) == 0:
                raise ValueError("Tienes que seleccionar por lo menos un perfil")

            # Se valida si el nombre o el apellido tenga solo letras
            if not(self.only_alpha(data['NOMBRES'])):
                raise ValueError("Ha ingresado algún carácter no permitido en el campo Nombres.")
            elif not(self.only_alpha(data['APELLIDOS'])):
                raise ValueError("Ha ingresado algún carácter no permitido en el campo Apellidos.")

            # Se le da una contraseña
            password = self.generate_password()
            pwd = self.encrypt(password)

            # se arma el payload
            payload = {
                "CODIGO_CE": data['CODIGO_CE'],
                "NOMBRES": data['NOMBRES'].lower(),
                "APELLIDOS": data['APELLIDOS'].lower(),
                "EMAIL": email,
                "ESTADO": data['ESTADO'],
                "USUARIO": data['USUARIO'],
                "PASSWORD": password
            }

            # Se inserta el usuario
            payload["PASSWORD"] = pwd
            resp_insert = usuario_database.insert_user(payload)

            body = json.loads(resp_insert["body"])
            if resp_insert["statusCode"] != 201:
                raise ValueError(body["message"])

            id_usuario = body["data"]["ID"]

            # Se crea el usuario en cognito
            resp_create_user_pass = self.create_user_password(payload, id_usuario)
            if resp_create_user_pass["statusCode"] != 200:
                body = json.loads(resp_create_user_pass["body"])
                raise ValueError(body["message"])

            payload["ID"] = self.encrypt(id_usuario)

            data_profile_user = {}
            for val in perfiles:
                data_profile_user = {
                    "ID_PERFIL": val,
                    "ID_USUARIO": id_usuario,
                    "USUARIO": data['USUARIO'],
                }

                usuario_database.insert_profile_user(data_profile_user)

            self.send_email_password(payload)
            payload["ID_USUARIO"] = id_usuario
            resp_log = self.save_log_create_user(payload)

            if resp_log["statusCode"] != 201:
                body = json.loads(resp_log["body"])
                raise ValueError(body["message"])

            return resp_insert
        else:
            return self.armadoBody(resp_val_per['data'], resp_val_per['statusCode'], {'PERMISOS': False})

    def validate_correct_email(self, email: str):

        regular_expressions = (r"\b[A-Za-z0-9._%+-]+@(allianz|externos.allianz|red5g)"
            r"+\.co\b")
        
        if re2.fullmatch(regular_expressions, email) is None:
            raise ValueError("El correo no es una dirección válida")

        return self.armadoBody("OK", 200)

    # Función encargada de enviar correos
    def send_email_password(self, data):
        
        # name =  data['NOMBRES'].title()
        # lastname = data['APELLIDOS'].title()
        
        # fullname = f"{name} {lastname}"
        # email = f"{fullname} <{data['EMAIL'].lower()}>"
        email = data['EMAIL'].lower()
        
        is_new_user=1
        
        link = Aws('mailgun-orq').get_secret().get('recover_password_link', '')
        
        link_split = link.split('&')
        
        filtered_params = [param for param in link_split if not (
            param.startswith('n=') and is_new_user == 1)]
        
        new_url = '&'.join(filtered_params).format(
            is_new_user=is_new_user, user_id=data['ID'])
        
        template = Template('set_password.html', 's3-orq')
        template_content = template.get_with_replace_var('%LINK%', new_url)
        
        send_email = Aws.function_name(
            'send_email', 'allianz-orq-mailgun', ext_app=True)
        
        Aws.lambdaInvoke(send_email, {
            'to': email,
            'subject': 'S_SETPASS',
            'body': template_content
        })

    # Función encargada de armar el username
    def build_username(self, data: dict):

        codigo_ce = str(data['CODIGO_CE'])
        nombres = data['NOMBRES']
        apellidos = data['APELLIDOS']

        username = nombres[:2] + apellidos[:2]

        number_of_strings = 1
        length_of_string = 4
        for x in range(number_of_strings):
            cod = (''.join(secrets.choice(codigo_ce) 
                for _ in range(length_of_string)))

        username += cod

        return username

    # Función encargada de validar que la contraseña cumpla los criterios
    def valid_password(self, data):

        password = data["PASSWORD"]
        confirm_password = data["CONFIRM_PASSWORD"]

        if password != confirm_password:
            raise ValueError("Las contraseñas no coinciden")

        #password_pattern = ("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")
        #resp = re.fullmatch(password_pattern, password)

        # Caracteristicas de la contraseña
        password_pattern = ["[A-Z]", "[a-z]", "[0-9]", "[[:punct:]]"]
        resp = True

        # Validamos la cantidad de caracteres minima (8) y que solo esten los caracteres permitidos
        if len(password) < 8 or re2.search("[^a-zA-Z0-9[:punct:]]", password) is not None: 
            resp = None
        else:
            # Se valida si la contraseña cumple las condiciones
            for pattern in password_pattern:
                if re2.search(pattern, password) is None:
                    resp = None
                    break

        if resp is None:
            mensaje = ("La contraseña debe tener al menos 8 caracteres, "
                "al menos un dígito, al menos una minúscula, al menos una "
                "mayúscula y al menos un carácter especial.")
            raise ValueError(mensaje)

        return self.armadoBody("OK", 200)

    # Función encargada de establecer la contraseña del usuario
    # def set_password(self, data):

    #     usuario_database = UsuariosDatabase()
    #     enc_id_usuario = data['ID_USUARIO']
    #     decrypt_id_usuario = self.decrypt(enc_id_usuario)

    #     # Se valida si el usuario existe
    #     resp_valid_user = usuario_database.valid_user(decrypt_id_usuario)

    #     body_user = json.loads(resp_valid_user["body"])
    #     if resp_valid_user["statusCode"] != 200:
    #         raise ValueError(body_user["message"])

    #     password = data["PASSWORD"]
    #     email = body_user["data"]["EMAIL"]
    #     user_cognito = {
    #         "password": password,
    #         "username": email
    #     }
    #     # Se valida la contraseña
    #     self.valid_password(data)

    #     enc_pass = self.encrypt(password)
    #     data["PASSWORD"] = enc_pass
    #     data["ID_USUARIO"] = decrypt_id_usuario

    #     # Se actualiza la contraseña
    #     resp_update_user = usuario_database.update_pass_user(data)

    #     if resp_update_user["statusCode"] != 200:
    #         body = json.loads(resp_update_user["body"])
    #         raise ValueError(body["message"])

    #     client_id = os_environ.get("COGNITO_CLIENT_ID", "")
    #     cognito = Cognito(client_id)
    #     resp_cognito = cognito.create_user_cognito(user_cognito)

    #     if body_user["data"]["ESTADO"] == 2:
    #         cognito.admin_disable_user(email)

    #     return resp_cognito

    # Función encargada de validar que el usuario no haya sido verificado
    def valid_link(self, data):

        usuario_database = UsuariosDatabase()
        enc_id_usuario = data['ID_USUARIO']
        decrypt_id_usuario = self.decrypt(enc_id_usuario)

        # Se valida si el usuario existe
        resp_valid_user = usuario_database.valid_link(decrypt_id_usuario)

        body = json.loads(resp_valid_user["body"])
        if resp_valid_user["statusCode"] != 200:
            raise ValueError(body["message"])

        return self.armadoBody("OK", 200)

    # Encrypt information
    def encrypt(self, info: str):

        # Generate key
        key = Fernet.generate_key()

        info = str(info).encode()
        encrypted = Fernet(key).encrypt(info)

        # The key is attached to the encrypted data
        encrypted += b':' + key

        return base64.b64encode(encrypted).decode("ascii")

    # Decrypt information
    def decrypt(self, encrypt: str):

        descrypted = base64.b64decode(encrypt)

        # The key is separated from the encrypted data
        encrypt = descrypted.split(b':')
        key = encrypt[1]
        descrypted = encrypt[0]

        descrypted = Fernet(key).decrypt(descrypted)

        return descrypted.decode("ascii")
    
    # Función encargada de obtener todos los usuarios
    def get_users(self, request_body):

        usuario_database = UsuariosDatabase()

        result = usuario_database.get_users(request_body)
        #operacion para obtener numero de paginas a mostrar
        pages = math.ceil(
            result['registers'].paginas / request_body['NUM_RESULTADOS'])
            
        users_list = []
        # recorre los resultados obtenidos para crear lista de diccionarios
        if len(result['data']) == 0:
            raise ValueError("No se encontraron datos.")
        
        for user in result['data']:
                
            # valida el estado del usuario
            if(user.estado == 1):
                state = 'Habilitado'
            elif (user.estado == 2):
                state = 'Congelado'

            users_list.append(
                {'ID': user.id,
                'CODIGO_CE':user.codigo_ce,
                'NOMBRES': user.nombres,
                'APELLIDOS': user.apellidos,
                'EMAIL': user.email,
                'ESTADO': state}
                )

        rows = {
            'PAGINACION':{
                'PAGINA_ACTUAL':request_body['PAGINA_ACTUAL'],
                'TOTAL_PAGINAS':pages,
                'TOTAL_REGISTROS': result['registers'].paginas,
                'REGISTROS_POR_PAGINA':request_body['NUM_RESULTADOS']
            },
            'LISTADO': users_list
            }
        
        if (len(result)):
            return self.armadoBody("Servicio exitoso.", 200, rows)
        else:
            return self.armadoBody("No se encontraron datos.", 400)
        

    # Función encargada de obtener un usuario 
    def get_user(self, data):

        usuario_database = UsuariosDatabase()

        id_user = int(data['ID_USUARIO'])
       
        # Se valida si el usuario existe
        data_user = usuario_database.valid_user(id_user)

        body = json.loads(data_user["body"])
        
        if data_user["statusCode"] == 200:
            # Se obtiene la información del usuario
           result = usuario_database.get_user(body["data"])
           
           return result
        else:
            return data_user

    # Función encargada de obtener todos los perfiles activos
    def get_perfiles(self):

        usuario_database = UsuariosDatabase()

        result = usuario_database.get_perfiles()

        if len(result) == 0:
            raise ValueError("No se encontraron datos.")
        
        rows = []
        # recorre los resultados obtenidos para crear lista
        for user_perfil in result:
            rows.append({
                'ID': user_perfil.id,
                'NOMBRE': user_perfil.nombre}
            )
        return self.armadoBody("Servicio exitoso.", 200, rows)
        

    # Función encargada de obtener los estados que puede tener un usuario
    def get_state_users(self):

        usuario_database = UsuariosDatabase()

        result = usuario_database.get_state_users()

        if len(result) == 0:
            raise ValueError("No se encontraron datos.")

        rows = []
        # recorre los resultados obtenidos para crear lista
        for state_user in result:
            rows.append({
                'ID': state_user.id,
                'DESCRIPCION': state_user.descripcion}
            )
        return self.armadoBody("Servicio exitoso.", 200, rows)


    # Funcion para editar Usuario
    def edit_user(self, data: dict):
        try:
            # Instanciamos las clases

            data_validate = {
                'USUARIO': data['USUARIO'],
                'ID_MODULO': 1,
                'PERMISO': 'EDITAR',
            }

            # Validamos msi el usuario tiene los permisos para relizar esta operación
            resp_val_per = self.validate_permission(data_validate)
            
            if resp_val_per['statusCode'] == 200:
                cognito = Cognito()
                usuario_database = UsuariosDatabase()

                data_user = usuario_database.valid_user(data['ID_USUARIO'])

                body = json.loads(data_user["body"])
                
                if data_user["statusCode"] == 200:
                    # Se obtiene la información del usuario
                    if (body["data"]["VERIFICADO"] == 1
                        and body["data"]["EMAIL"] != data['EMAIL']):
                        raise ValueError("No es posible editar el correo del usuario")
                else:
                    raise ValueError(body["message"])

                # Se valida el correo electronico, que cumpla con el estandar
                self.validate_correct_email(data['EMAIL'])
                
                # Se valida la existencia del correo electronico en la base de datos, exceptuando el del usuario actual
                resp_valid_email = usuario_database.valid_email_edit(data)

                # Se valida la respuesta de la consulta en la base de datos, sobre el Email
                if resp_valid_email["statusCode"] != 200:
                    body = json.loads(resp_valid_email["body"])
                    raise ValueError(body["message"])

                resp_cod = usuario_database.val_codigo_ce_unique_edit(data)
                if resp_cod is False:
                    raise ValueError("El Código CE ya existe.")

                # Se valida que se haya seleccionado por lo menos un perfil
                perfiles = data.get("PERFILES",[])
                if len(perfiles) == 0:
                    raise ValueError("Tienes que seleccionar por lo menos un perfil.")

                # Se valida si el nombre o el apellido tenga solo letras
                if not(self.only_alpha(data['NOMBRES'])):
                    raise ValueError("Ha ingresado algún carácter no permitido en el campo Nombres.")
                elif not(self.only_alpha(data['APELLIDOS'])):
                    raise ValueError("Ha ingresado algún carácter no permitido en el campo Apellidos.")

                # Se declaran las variableas a utilizar para la funcion y guardar en el log
                activity_type = "USU_EDIT"
                    
                # Se obtienen la informacion del usuario antes de hacer el cambio de estado
                body = self.get_user(data)

                if body["statusCode"] == 200:

                    # Validar el estado, en el cual va a ser cambiado (Habilitado o Desabilitado)
                    if (data['ESTADO'] == 1 or data['ESTADO'] == 2):
                        # Se guarda la información del usuario
                        inf_anterior = json.loads(body['body'])['data']

                        # Se valida el estado en el cual se encuentra el usuario, y saber si es necesario realizar la habilitacion o deshabilicion
                        if (inf_anterior['INFORMACION_BASICA']['ID_ESTADO'] != data['ESTADO']):
                            # Se valida el estado en el cual se encuentra el usuario, y saber si es necesario realizar la habilitacion o deshabilicion
                            if data['ESTADO'] == 2 and (not('COMENTARIO' in data) or data['COMENTARIO'] == ""):
                                return self.armadoBody("Debe ingresar el Comentario.", 400)

                            data_change = {
                                "username": inf_anterior['INFORMACION_BASICA']["EMAIL"],
                                "state":data['ESTADO']
                            }
                            cognito_change_state = self.valid_change_state_user(data_change)
                            if cognito_change_state ["statusCode"] != 200:
                                return cognito_change_state
                            
                        data['EMAIL'] = data['EMAIL'].lower()
                        inf_anterior['INFORMACION_BASICA']['EMAIL'] = inf_anterior['INFORMACION_BASICA']['EMAIL'].lower()
                        if data['EMAIL'] != inf_anterior['INFORMACION_BASICA']['EMAIL']:
                            #Cambio de Correo
                            data_update = {
                                "username": inf_anterior['INFORMACION_BASICA']['EMAIL'],
                                "newEmail":data['EMAIL']
                            }
                            update_cognito_resp = cognito.admin_update_user_attributes(data_update)
                            if update_cognito_resp["statusCode"] != 200:
                                return update_cognito_resp
                            data['VERIFICADO'] = 1

                        # Se actualiza la informacion en la tabla Usuario
                        resp_update = usuario_database.update_user(data)

                        # Se valida la respuesta del guardado de la informacion
                        if resp_update["statusCode"] != 200:
                            body = json.loads(resp_update["body"])
                            raise ValueError(body["message"])

                        # Se desabilitan todos los perfiles, asociados a dicho usuario
                        resp_disable_profile = usuario_database.disable_profile_user(data['ID_USUARIO'])
                        
                        # Se valida la accion que se llevó al cabo
                        if resp_disable_profile["statusCode"] != 200:
                            body = json.loads(resp_disable_profile["body"])
                            raise ValueError(body["message"])

                        # Se obitene todos los perfiles asociados a este usuario
                        profiles_user = json.loads(resp_disable_profile['body'])

                        # Se hace un recoorrdo de los perfiles, que se editaran
                        for val in perfiles:
                            status_profile = False

                            # Se recoore el listado de los perfiles que ya estaban asociados al usuario
                            for prof_user in profiles_user['data']:
                                # Validamos que el perfil este en la tabla, de ser asi ejecutamos una acualizacion sino insertamos
                                if val == prof_user['ID_PERFIL']:
                                    # Cambiamos el estado, (Ya registrado en la tabla), y procedemos a actualizarlo. 
                                    status_profile = True
                                    usuario_database.enable_profile_user(prof_user['ID'])

                            # Si no esta el perfil asiciado en la tabla se procede a insertarlo
                            if status_profile == False:
                                data_profile_user = {
                                    "ID_PERFIL": val,
                                    "ID_USUARIO": data['ID_USUARIO'],
                                    "USUARIO": data['USUARIO']
                                }

                                usuario_database.insert_profile_user(data_profile_user)
                        # Se obtienen la informacion del usuario despues de hacer de hacer el cambio de estado y se guarda
                        body = self.get_user(data)
                        inf_actual = json.loads(body['body'])['data']

                        # Armamos la informacion anterior y actual del usuario
                        user = {
                                'INF_ANTERIOR': inf_anterior,
                                'INF_ACTUAL': inf_actual
                                }

                        #se guardan los datos en el log
                        state_log = usuario_database.save_log(user,data,activity_type)
                        
                        # Devolvemos la respuesta de actualizar los datos de usuario.
                        if state_log:
                            return resp_update
                        else: 
                            return state_log
                    else:
                        return self.armadoBody("Estado Invalido.", 400)
                else:
                    return body
            
            else:
                return self.armadoBody(resp_val_per['data'], resp_val_per['statusCode'], {'PERMISOS': False})

        except Exception as error:
            return self.armadoBody(str(error), 500)

    # Funcion para hacer el cambio de estado habilitado/Desabilitado
    def change_state_user(self, data: dict):
        try:
            # Instanciamos las clases
            usuario_database = UsuariosDatabase()

            # Validar el estado, en el cual va a ser cambiado (Habilitado o Desabilitado)
            if (data['ESTADO'] == 1 or data['ESTADO'] == 2):
                data_validate = {
                    'USUARIO': data['USUARIO'],
                    'ID_MODULO': 1,
                    'PERMISO': 'DESHABILITAR' if data['ESTADO'] == 2 else 'HABILITAR',
                }

                # Validamos msi el usuario tiene los permisos para relizar esta operación
                resp_val_per = self.validate_permission(data_validate)
                if resp_val_per['statusCode'] == 200:
                    # Se declaran las variableas a utilizar para la funcion y guardar en el log
                    activity_type = "USU_DESH" if data['ESTADO'] == 2 else "USU_HABI"

                    # Se valida que valla el comentario
                    if data['ESTADO'] == 2 and (not('COMENTARIO' in data) or data['COMENTARIO'] == ""):
                        return self.armadoBody("Debe ingresar el Comentario.", 400)
                    
                    if len(data['COMENTARIO'])> 150:
                        return self.armadoBody("El comentario sobrepasa los 150 caracteres máximos", 400)
                    
                    # Se obtienen la informacion del usuario antes de hacer el cambio de estado
                    body = self.get_user(data)

                    if body["statusCode"] == 200:
                        # Se guarda la información del usuario
                        inf_anterior = json.loads(body['body'])['data']

                        # Se valida el estado en el cual se encuentra el usuario, y saber si es necesario realizar la habilitacion o deshabilicion
                        if inf_anterior['INFORMACION_BASICA']['ID_ESTADO'] == data['ESTADO']:
                            if data['ESTADO'] == 1:
                                return self.armadoBody("El usuario ya se encuentra habilitado.", 400)
                            elif data['ESTADO'] == 2:
                                return self.armadoBody("El usuario ya se encuentra deshabilitado.", 400)
                        # Se actualiza la informacion en la tabla Usuario
                        data_change = {
                            "username": inf_anterior['INFORMACION_BASICA']["EMAIL"],
                            "state":data['ESTADO']
                        }
                        cognito_change_state = self.valid_change_state_user(data_change)
                        if cognito_change_state ["statusCode"] != 200:
                            return cognito_change_state
                        resp_update = usuario_database.change_state_user(data)

                        # Se valida la respuesta del guardado de la informacion
                        if resp_update["statusCode"] != 200:
                            body = json.loads(resp_update["body"])
                            raise ValueError(body["message"])

                        # Se obtienen la informacion del usuario despues de hacer de hacer el cambio de estado y se guarda
                        body = self.get_user(data)
                        inf_actual = json.loads(body['body'])['data']

                        # Armamos la informacion anterior y actual del usuario
                        user = {
                                'INF_ANTERIOR': inf_anterior,
                                'INF_ACTUAL': inf_actual
                                }

                        #se guardan los datos en el log
                        state_log = usuario_database.save_log(user,data,activity_type)
                        
                        # Devolvemos la respuesta de actualizar los datos de usuario.
                        if state_log:
                            return resp_update
                        else: 
                            return state_log
                    else:
                        return body
                
                else:
                    return self.armadoBody(resp_val_per['data'], resp_val_per['statusCode'], {'PERMISOS': False})

            else:
                return self.armadoBody("Estado Invalido", 400)

        except Exception as error:
            return self.armadoBody(str(error), 500)

    # Funcion encargada de validar que accion ejecuta
    #  el cambio de estado habilitado/Desabilitado
    def valid_change_state_user(self, data: dict):
        try:
            # Instanciamos las clases
            cognito = Cognito()
            resp = {}
            if data["state"] == 2:
                disable_user = cognito.admin_disable_user(data["username"])
                resp = disable_user
            else:
                enable_user = cognito.admin_enable_user(data["username"])
                resp = enable_user         
            return resp
        except Exception as error:
            return self.armadoBody(str(error), 500)

    # Función encargada de eliminar un usuario
    def delete_user(self, data):
        data_validate = {
            'USUARIO': data['USUARIO'],
            'ID_MODULO': 1,
            'PERMISO': 'ELIMINAR',
        }

        # Validamos msi el usuario tiene los permisos para relizar esta operación
        resp_val_per = self.validate_permission(data_validate)
        if resp_val_per['statusCode'] == 200:
            cognito = Cognito()
            usuario_database = UsuariosDatabase()
            
            id_user = int(data['ID_USUARIO'])
            activity_type = "USU_ELIM"

            # Se obtienen la informacion del usuario
            body = self.get_user(data)

            if body["statusCode"] == 200:
                body_user = json.loads(body['body'])['data']
            
                user = {'INF_ANTERIOR':'',
                        'INF_ACTUAL': 
                            body_user
                    }
                    
                #Se elimina usuario en cognito
                response = cognito.delete_user_cognito(body_user)

                #se valida si el usuario fue eliminado en cognito
                if(response["statusCode"] == 200):
                    #se guardan los datos en el log
                    state_log = usuario_database.save_log(user,data,activity_type)
                        
                    if state_log["statusCode"] != 201:
                        body = json.loads(state_log["body"])
                        raise ValueError(body["message"])

                    #se elimina el usuario
                    result = usuario_database.delete_user(id_user)
                    return result
                else:
                    return response
            else:
                return body
        else:
            return self.armadoBody(resp_val_per['data'], resp_val_per['statusCode'], {'PERMISOS': False})


    # Guarda log al crear usuario
    def save_log_create_user(self, data):

        # Se obtienen la informacion del usuario
        body = self.get_user(data)

        if body["statusCode"] != 200:
            raise ValueError(body["message"])

        body_user = json.loads(body['body'])['data']
    
        user = {'INF_ANTERIOR': None,
                'INF_ACTUAL': 
                    body_user
            }

        usuario_database = UsuariosDatabase()
        activity_type = "USU_CREA"
        data["COMENTARIO"] = "Creacion de usuario"
        return usuario_database.save_log(user, data, activity_type)

    def generate_password(self):
        letters_lowercase = string.ascii_lowercase
        letters_uppercase = string.ascii_uppercase
        digits = string.digits

        lowercase = [secrets.choice(letters_lowercase) for i in range(2)]
        uppercase = [secrets.choice(letters_uppercase) for i in range(2)]
        number = [secrets.choice(digits) for i in range(2)]

        pwd = "".join(lowercase) + "".join(uppercase) + "".join(number) + "**"

        return pwd

    def create_user_password(self, data, id_usuario):
        try:
            user_cognito = {
                "password": data['PASSWORD'],
                "username": data['EMAIL'],
                "id_usuario": id_usuario
            }

            client_id = os_environ.get("COGNITO_CLIENT_ID", "")
            cognito = Cognito(client_id)
            resp_cognito = cognito.create_user_cognito(user_cognito)

            if data["ESTADO"] == 2:
                cognito.admin_disable_user(data['EMAIL'])

            return resp_cognito
        except Exception as error:
            return self.armadoBody(str(error), 500)

    # Función para recuperar la contraseña del usuario
    def set_password(self, data):

        usuario_database = UsuariosDatabase()
        enc_id_usuario = data['ID_USUARIO']
        decrypt_id_usuario = self.decrypt(enc_id_usuario)

        # Se valida si el usuario ya fue verificado
        resp_valid_user = usuario_database.valid_link(decrypt_id_usuario)

        body = json.loads(resp_valid_user["body"])
        if resp_valid_user["statusCode"] != 200:
            raise ValueError(body["message"])

        # Se valida si el usuario existe
        resp_valid_user = usuario_database.valid_user(decrypt_id_usuario)

        body = json.loads(resp_valid_user["body"])
        if resp_valid_user["statusCode"] != 200:
            raise ValueError(body["message"])

        # Se valida la contraseña
        self.valid_password(data)

        password = data["PASSWORD"]
        enc_pass = self.encrypt(password)
        data["PASSWORD"] = enc_pass
        data["ID_USUARIO"] = decrypt_id_usuario

        # Se actualiza la contraseña
        resp_update_user = usuario_database.update_pass_user(data)

        if resp_update_user["statusCode"] != 200:
            body_update = json.loads(resp_update_user["body"])
            raise ValueError(body_update["message"])

        user_cognito = {
            "password": password,
            "username": body["data"]["EMAIL"]
        }

        client_id = os_environ.get("COGNITO_CLIENT_ID", "")
        cognito = Cognito(client_id)
        resp_cognito = cognito.admin_set_user_password(user_cognito)
        
        if resp_cognito["statusCode"] != 200:
            body_cognito = json.loads(resp_cognito["body"])
            raise ValueError(body_cognito["message"])

        return resp_update_user

    # Funcion para valdiar solo texto
    def only_alpha(self, word):
        word = word.replace(" ", "")

        return word.isalpha()

    # Funcion para valdiar el permiso que tiene un usuario
    def validate_permission(self, data):
        try:
            # Instanciamos las clases
            usuario_db = UsuariosDatabase()
            resp_consult = usuario_db.consult_permission(data)
            body = json.loads(resp_consult['body'])

            if body['statusCode'] == 200:
                resp = True
            elif body['statusCode'] == 400:
                resp = "No cuenta con los permisos necesarios para realizar esta operación."
            else:
                resp = body['data']
            
            return { 'data': resp, 'statusCode': resp_consult['statusCode'] }

        except Exception as error:
            return { 'data': str(error), 'statusCode': 500 }