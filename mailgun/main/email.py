import os
from base64 import b64encode
from datetime import datetime, timedelta
from json import loads
from requests import request
from urllib.parse import quote, unquote

from Log_Api.Utils.Aws import Aws
from Log_Api.Utils.ModelsType import Model
from Log_Api.Utils.Response import Response
from main.Database import Database

from models.email import Email as EmailModel


class Email(Response):
    def __init__(self, subject) -> None:
        __mailgun = Aws('mailgun-orq').get_secret()
        self.__mailgun_request = loads(__mailgun.get('request'))
        self.__mailgun_headers = loads(__mailgun.get('headers'))
        self.__URL = __mailgun.get('URL')
        self.__mailgun_pass = __mailgun.get('key')
        self.__subject = __mailgun.get(subject, 'ALLIANZ')
        self.__body = ''
        self.__source = __mailgun.get('email_source', '')
        self.__to = ''
        self.__files = []
        # self.__allowed_attempts = __mailgun.get('allowed_attempts')
        # self.__validity_period = __mailgun.get('validity_period')
        self.__is_html_template = False
        self.__quote_subject = quote(self.__subject)
        self.__quote_body = quote(self.__body)
        self.__quote_to = quote(self.__to)

    def set_subject(self, subject):
        self.__subject = subject
        self.__quote_subject = quote(self.__subject)

    def get_body(self): return self.__body

    def set_body(self, body):
        self.__body = body
        self.__quote_body = quote(self.__body)

    def set_to(self, to):
        self.__to = to
        self.__quote_to = quote(self.__to)

    def set_files(self, files):
        self.__files = self.__get_attachment(files)

    def set_is_html(self, is_html_template):
        self.__is_html_template = is_html_template

    def send_mailgun_email(self):
        """
        Enviar email mediante Mailgun
        """
        try:

            # un_subject = unquote(self.__quote_subject)
            # un_body = unquote(self.__quote_body)
            # un_to = unquote(self.__quote_to)

            # if (un_subject, un_body, un_to) != (self.__subject, self.__body, self.__to):
            #     raise Exception('Unquote error')

            if self.__is_html_template:
                self.__mailgun_request["html"] = self.__body
                self.__mailgun_request.pop('text')
            else:
                self.__mailgun_request["text"] = self.__body
                self.__mailgun_request.pop('html')

            self.__mailgun_request.update(
                subject=self.__subject,
                to=self.__to
            )

            response = request(
                "POST", self.__URL,
                auth=("api", self.__mailgun_pass),
                files=self.__files,
                data=self.__mailgun_request
            )
            response.raise_for_status()
            response = response.json()
            return self.__save(hash=response.get('id'))

        except Exception as error:
             raise error
        # finally:
        #     Logs.save()

    def is_valid(self):
        """
        TODO:
        Valida si puede enviar el email
        en un tiempo predefinido 
        :return:
            True si puede enviar el email
        """

        if self.__validity_period == 'unlimited':
            return True

        last = self.__last_email()

        if last:
            minutes = timedelta(minutes=self.__validity_period)
            now = datetime.now()

    def __last_email(self):
        session = Database('dbw').session
        try:
            email_types = Model.create('EMAIL_TYPES')
            email_type_id = email_types.get_id_code(self.__subject, session)
            if email_type_id is None:
                raise Exception('Email type not found')

            last = session.query(EmailModel).filter(
                # EmailModel.type == email_type_id,
                EmailModel.to == self.__to,
                EmailModel.subject == self.__subject
            ).order_by(EmailModel.id.desc()).first()

            return last

        except Exception as error:
            raise error
        finally:
            session.invalidate()
            session.close()

    def __save(self, hash: str) -> int:
        """
        Guarda el email en la base de datos
        :return:
            id del email guardado
        """
        session = Database('dbw').session
        try:
            # email_types = Model.create('EMAIL_TYPES')
            # email_type_id = email_types.get_id_code(self.__subject, session)
            # if email_type_id is None:
            #     raise Exception('Email type not found')

            email = EmailModel(
                reference_id=hash,
                subject=self.__subject,
                body=self.__body,
                to=self.__to,
                # type=email_type_id
            )
            session.add(email)
            session.commit()
            return email.id
        except Exception as error:
            raise error
        finally:
            session.invalidate()
            session.close()

    def __get_attachment(self, attachments: list):
        """
        Obtiene el archivo adjunto del s3 para enviarlo por email
        :param attachments:
            nombres de los archivos adjunto
        :return:
            contenido archivo adjunto
        """
        bucket_name = Aws('s3-fcc').get_secret()['bucket_name']

        attachments = {
            f"attachment[{indx}]": (attachment['name'] if attachment['name'].find("/") == -1 else attachment['name'].split("/")[1],
                                    Aws.get_object(bucket_name, attachment['route'])) for indx, attachment in enumerate(attachments)
        }
        return attachments
