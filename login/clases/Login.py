from utils.Response import Response
from clases.LoginDatabase import LoginDatabase
from clases.Cognito import Cognito
from cryptography.fernet import Fernet
from os import environ as os_environ
import base64
import re2
import json
class Login (Response):

    # Funcion construsctor de la clase.
    # def __init__(self, payload = {}):
    #     self.payload = payload

    # Función que envia el correo para recuperar la contraseña del usuario
    def send_email_recover_password(self, data):

        response = Response()
        login_database = LoginDatabase()
        email = data['EMAIL']

        # Se valida si el usuario existe
        resp_user = login_database.valid_user_by_email(email)

        if resp_user is False:
            msj = "El correo ingresado no pertenece a un usuario activo"
            raise ValueError(msj)

        id_usuario = resp_user.id

        datos_recover = {
            "ID_USUARIO": id_usuario,
            "ID_USUARIO_ENCRYPT": self.encrypt(str(id_usuario)),
            "NOMBRES": resp_user.nombres,
            "APELLIDOS": resp_user.apellidos,
            "EMAIL": resp_user.email
        }

        # Se inhabilitan todos los link que tenga el usuario
        login_database.update_register_recover_pass(id_usuario)

        insert = login_database.insert_register_recover_pass(datos_recover)

        body_insert = json.loads(insert["body"])
        if insert["statusCode"] != 201:
            raise ValueError(body_insert["message"])

        return response.armadoBody("OK", 200)

    # Función que valida el link de recuperar contraseña
    def valid_link_recovery_pass(self, data):

        response = Response()
        login_database = LoginDatabase()
        # Validar que el link para recuperar contraseña no haya  sido usado
        id_recuperar_pass = data['ID_RECUPERAR_CONTRASENA']
        enc_id_usuario = data['ID_USUARIO']
        decrypt_id_usuario = self.decrypt(enc_id_usuario)
        resp_link = login_database.valid_id_recuperar_pass(id_recuperar_pass,
                                                           decrypt_id_usuario)

        if resp_link is False:
            msj = "Este enlace ya no se encuentra disponible."
            resp = response.armadoBody(msj, 400)
        else:
            resp = response.armadoBody("OK", 200)

        return resp

    # Función para recuperar la contraseña del usuario
    def recover_password(self, data):

        login_database = LoginDatabase()
        # Validar que el link para recuperar contraseña no haya  sido usado
        id_recuperar_pass = data['ID_RECUPERAR_CONTRASENA']
        enc_id_usuario = data['ID_USUARIO']
        decrypt_id_usuario = self.decrypt(enc_id_usuario)
        resp_link = login_database.valid_id_recuperar_pass(id_recuperar_pass, decrypt_id_usuario)

        if resp_link is False:
            raise ValueError("Este enlace ya no se encuentra disponible.")

        # Se valida si el usuario existe
        resp_valid_user = login_database.valid_user(decrypt_id_usuario)

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
        resp_update_user = login_database.update_pass_user(data)

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

        login_database.update_state_recovey_pass(id_recuperar_pass)

        return resp_update_user

    def validate_correct_email(self, email: str):

        response = Response()
        regular_expressions = (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]"
            r"+\.[A-Z|a-z]{2,}\b")

        if re2.fullmatch(regular_expressions, email) is None:
            raise ValueError("El correo no es una dirección válida")

        return response.armadoBody("OK", 200)

    # Función encargada de validar que la contraseña cumpla los criterios
    def valid_password(self, data):

        response = Response()
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

        return response.armadoBody("OK", 200)

    # Función encargada de validar que el usuario no haya sido verificado
    def valid_link(self, data):

        response = Response()
        login_database = LoginDatabase()
        enc_id_usuario = data['ID_USUARIO']
        decrypt_id_usuario = self.decrypt(enc_id_usuario)

        # Se valida si el usuario existe
        resp_valid_user = login_database.valid_link(decrypt_id_usuario)

        body = json.loads(resp_valid_user["body"])
        if resp_valid_user["statusCode"] != 200:
            raise ValueError(body["message"])

        return response.armadoBody("OK", 200)

    # Funcion que valida los modulos que puede ver un usuario
    def get_modules_by_user(self, data):

        login_database = LoginDatabase()
        id_usuario = data['ID_USUARIO']

        # Se valida si el usuario existe
        resp = login_database.get_modules_by_user(id_usuario)

        if resp["statusCode"] != 200:
            body = json.loads(resp["body"])
            raise ValueError(body["message"])

        return resp
    
    # Funcion que valida los submodulos de un modulo que puede ver un usuario
    def get_submodules_by_user(self, data):

        login_database = LoginDatabase()

        # Se valida si el usuario existe
        resp = login_database.get_submodules_by_user(data)

        if resp["statusCode"] != 200:
            body = json.loads(resp["body"])
            raise ValueError(body["message"])

        return resp

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
