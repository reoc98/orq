from models.UsuariosModel import UsuariosModel
from models.RecuperarContrasena import RecuperarContrasenaModel
from models.ModulosModel import ModulosModel
from models.PermisosModel import PermisosModel
from models.PerfilPermisosModel import PerfilPermisosModel
from models.PerfilUsuariosModel import PerfilUsuariosModel
from models.TipoPermisoModel import TipoPermisoModel
from clases.Database import Database
from sqlalchemy import update, and_
from utils.Response import Response
from Log_Api.Utils.Aws import Aws
from Log_Api.Utils.Template import Template
import json

class LoginDatabase():

    # Valida si el correo ya existe
    def valid_email(self, email):
        response = Response()
        db = Database('dbr').session
        try:

            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.email == email, 
                UsuariosModel.estado == 1
            ).first()

            if search is None:
                resp = response.armadoBody("Correo disponible.", 200)
            else:
                resp = response.armadoBody("El correo ya existe.", 400)

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el correo ya existe
    def valid_user_by_email(self, email):
        response = Response()
        db = Database('dbr').session
        try:

            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.email == email, 
                UsuariosModel.estado == 1,
                UsuariosModel.verificado == 1
            ).first()

            if search is None:
                resp = False
            else:
                resp = search

            # Responde el servicio
            return resp

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    def insert_register_recover_pass(self, payload):
        db = Database('dbw').session
        try:
            row = RecuperarContrasenaModel(
                {"ID_USUARIO": payload["ID_USUARIO"]})
            db.add(row)
            db.flush()
            payload['ID_RECUPERAR_PASS'] = row.id
            email = self.send_email_recover(payload)
            row.email_id = email['data']['id']
            db.add(row)
            db.commit()
            data_insert = json.loads(str(row))

            return Response().armadoBody("Proceso exitoso.", 201, data_insert)
        except KeyError as error:
            return Response().armadoBody("Ocurrió un error al enviar el correo", 400)
        except Exception as error:
            return Response().armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    def send_email_recover(self, data):

        # nombres =  data['NOMBRES']
        # apellidos = data['APELLIDOS']
        email = data['EMAIL']

        link = Aws('mailgun-orq').get_secret().get(
            'recover_password_link', '').format(
                user_id=data['ID_USUARIO_ENCRYPT'],
                is_new_user=0,
                link_id=data['ID_RECUPERAR_PASS']
        )

        template = Template('recover_password.html', 's3-orq')
        template_content = template.get_with_replace_var('%LINK%', link)

        send_email = Aws.function_name(
            'send_email', 'allianz-orq-mailgun', ext_app=True)

        response_mail = Aws.lambdaInvoke(send_email, {
            'to': email,
            'subject': 'S_RECOPASS',
            'body': template_content
        })

        return response_mail
    
    # Funcion que actualizacion los link que tenga el usuarios a estado 0
    def update_register_recover_pass(self, id_usuario):
        response = Response()
        db = Database("dbw").session
        try:

            update_values = {
                "estado": 0
            }

            db.execute(
                update(RecuperarContrasenaModel).where(
                    RecuperarContrasenaModel.id_usuario == id_usuario
                ).values(update_values)
            )
            db.commit()

            # Responde el servicio
            return response.armadoBody("Registro actualizado.", 200)

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el usuario existe
    def valid_user(self, id_usuario):
        response = Response()
        db = Database('dbr').session
        try:
            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.id == id_usuario, 
                UsuariosModel.estado != 0
            ).first()

            if search is None:
                resp = response.armadoBody("El usuario no existe.", 400)
            else:
                resp = response.armadoBody("OK.", 200, json.loads(str(search)))

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el link de cambia pass fue utilizado
    def valid_id_recuperar_pass(self, id_recuperar_pass, id_usuario):
        response = Response()
        db = Database('dbr').session
        try:

            # Prepara los datos para insertarlos
            search = db.query(RecuperarContrasenaModel).filter(
                RecuperarContrasenaModel.id == id_recuperar_pass, 
                RecuperarContrasenaModel.id_usuario == id_usuario, 
                RecuperarContrasenaModel.estado == 1
            ).first()

            if search is None:
                resp = False
            else:
                resp = True

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Valida si el link ya fue verificado
    def valid_link(self, id_usuario):
        response = Response()
        db = Database('dbr').session
        try:

            # Prepara los datos para insertarlos
            search = db.query(UsuariosModel).filter(
                UsuariosModel.id == id_usuario, 
                UsuariosModel.estado == 1,
                UsuariosModel.verificado == 0,
            ).first()

            if search is None:
                msj = "El usuario ya fue verificado."
                resp = response.armadoBody(msj, 400)
            else:
                resp = response.armadoBody("OK.", 200, json.loads(str(search)))

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Funcion encargada de realizar la actualizacion de la contraseña
    def update_pass_user(self, payload):
        response = Response()
        db = Database("dbw").session
        try:
            update_values = {
                "password": payload["PASSWORD"],
                "verificado": 1
            }

            db.execute(
                update(UsuariosModel).where(
                    UsuariosModel.id == payload["ID_USUARIO"]
                ).values(update_values)
            )
            db.commit()

            # Responde el servicio
            return response.armadoBody("Contraseña actualizada.", 200)

        except Exception as error:
            return response.armadoBody(str(error), 500)
    
        finally:
            db.invalidate()
            db.close()

    # Funcion encargada de realizar la actualizacion de la contraseña
    def update_state_recovey_pass(self, id_recuperar_pass):
        response = Response()
        db = Database("dbw").session
        try:
            update_values = {
                "estado": 0
            }

            db.execute(
                update(RecuperarContrasenaModel).where(
                    RecuperarContrasenaModel.id == id_recuperar_pass
                ).values(update_values)
            )
            db.commit()

            # Responde el servicio
            return response.armadoBody("Registro actualizado.", 200)

        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()

    # Query que obtiene los modulos que puede ver un usuario
    def get_modules_by_user(self, id_usuario):
        response = Response()
        db = Database('dbr').session
        try:

            # Prepara los datos para insertarlos
            search = db.query(
                ModulosModel.id,
                ModulosModel.nombre,
                ModulosModel.icono,
                ModulosModel.ruta
            ).join(
                PermisosModel, 
                and_(
                    PermisosModel.id_modulo == ModulosModel.id,
                    PermisosModel.activo == 1)
            ).join(
                PerfilPermisosModel, 
                and_(
                    PerfilPermisosModel.id_permiso == PermisosModel.id,
                    PerfilPermisosModel.estado == 1)
            ).join(
                PerfilUsuariosModel, 
                and_(
                    PerfilUsuariosModel.id_perfil == 
                        PerfilPermisosModel.id_perfil,
                    PerfilUsuariosModel.estado == 1)
            ).join(
                UsuariosModel, 
                and_(
                    UsuariosModel.id == PerfilUsuariosModel.id_usuario,
                    UsuariosModel.estado == 1)
            ).join(
                TipoPermisoModel, 
                TipoPermisoModel.id == PermisosModel.id_tipo_permiso
            ).filter(
                ModulosModel.activo == 1,
                ModulosModel.cabecera == 0,
                UsuariosModel.id == id_usuario,
                TipoPermisoModel.nombre == 'LISTAR'
            ).group_by(
                ModulosModel.id
            ).order_by(
                ModulosModel.orden
            ).all()

            modules = []
            for module in search:

                modules.append({
                    "ID": module.id,
                    "NOMBRE": module.nombre,
                    "ICONO": module.icono,
                    "RUTA": module.ruta
                })

            if len(modules) == 0:
                msj = ("No tiene permisos asociados, por favor comunicarse con"
                    " el administrador.")
                resp = response.armadoBody(msj, 400)
            else:
                resp = response.armadoBody("OK", 200, modules)

            # Responde el servicio
            return resp
        
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
    
    # Query que obtiene los submodulos que puede ver un usuario
    def get_submodules_by_user(self, data):
        id_usuario = data['ID_USUARIO']
        id_modulo = data['ID_MODULO']
        response = Response()
        db = Database('dbr').session
        try:

            # Prepara los datos para insertarlos
            search = db.query(
                ModulosModel.id,
                ModulosModel.nombre,
                ModulosModel.icono,
                ModulosModel.ruta
            ).join(
                PermisosModel, 
                and_(
                    PermisosModel.id_modulo == ModulosModel.id,
                    PermisosModel.activo == 1)
            ).join(
                PerfilPermisosModel, 
                and_(
                    PerfilPermisosModel.id_permiso == PermisosModel.id,
                    PerfilPermisosModel.estado == 1)
            ).join(
                PerfilUsuariosModel, 
                and_(
                    PerfilUsuariosModel.id_perfil == 
                        PerfilPermisosModel.id_perfil,
                    PerfilUsuariosModel.estado == 1)
            ).join(
                UsuariosModel, 
                and_(
                    UsuariosModel.id == PerfilUsuariosModel.id_usuario,
                    UsuariosModel.estado == 1)
            ).join(
                TipoPermisoModel, 
                TipoPermisoModel.id == PermisosModel.id_tipo_permiso
            ).filter(
                ModulosModel.activo == 1,
                ModulosModel.cabecera == id_modulo,
                UsuariosModel.id == id_usuario,
                TipoPermisoModel.nombre == 'LISTAR'
            ).group_by(
                ModulosModel.id
            ).order_by(
                ModulosModel.orden
            ).all()

            modules = []
            for module in search:

                modules.append({
                    "ID": module.id,
                    "NOMBRE": module.nombre,
                    "ICONO": module.icono,
                    "RUTA": module.ruta
                })

            if len(modules) == 0:
                msj = ("No tiene permisos asociados, por favor comunicarse con"
                    " el administrador.")
                resp = response.armadoBody(msj, 400)
            else:
                resp = response.armadoBody("OK", 200, modules)

            # Responde el servicio
            return resp
        except Exception as error:
            return response.armadoBody(str(error), 500)
        
        finally:
            db.invalidate()
            db.close()
